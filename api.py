# api.py - FastAPI封装：教室环境智能调控智能体 HTTP API
# 供扣子(Coze)平台自定义插件调用，暴露三位一体闭环与人机协同问答能力
# 启动：uvicorn api:app --host 0.0.0.0 --port 8000
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from agent_collect import CollectAgent
from agent_decision import DecisionAgent
from agent_execute import ExecuteAgent
from agent_audit import AuditAgent
from agent_interact import InteractAgent

app = FastAPI(title="教室环境智能调控智能体", version="1.0.0")

collect = CollectAgent()
decide = DecisionAgent()
execute = ExecuteAgent()
interact = InteractAgent()
audit = AuditAgent()


# ---------------- 请求/响应模型 ----------------
class ForecastData(BaseModel):
    source: str = "公开气象预报API"
    forecast_time: str = ""
    alerts: List[str] = []
    temp_drop: Optional[float] = None
    temp_rise: Optional[float] = None
    wind_level: Optional[float] = None
    humidity_rise: Optional[float] = None
    pm25_rise: Optional[float] = None


class SensorData(BaseModel):
    co2: Optional[float] = Field(None, description="室内CO2浓度(ppm)")
    temperature: Optional[float] = Field(None, description="室内温度(℃)")
    humidity: Optional[float] = Field(None, description="室内相对湿度(%)")
    pm25: Optional[float] = Field(None, description="室内PM2.5(μg/m³)")
    noise: Optional[float] = Field(None, description="室内噪音(dB)")
    noise_type: str = Field("none", description="噪音类型:teacher/student/equipment/outdoor/none")
    outdoor_noise: Optional[float] = Field(None, description="室外噪音(dB)")
    outdoor_pm25: Optional[float] = Field(None, description="室外PM2.5(μg/m³)")
    rain: bool = Field(False, description="室外是否下雨")
    period: str = Field("class", description="时段:class上课/break课间")
    region: str = Field("south", description="地域:north/south/coastal_industrial/northwest_arid/qinghai_tibet/central_plain/southwest_plateau")
    season: str = Field("autumn", description="季节:spring/summer/autumn/winter/plum_rain/heating_season")
    age_stage: str = Field("middle", description="学龄段:kindergarten/primary/middle/university")
    weather_alert: str = Field("none", description="突变天气:none/cold_wave/heat_wave/heavy_rain/dust_storm/heavy_haze")
    forecast: Optional[ForecastData] = Field(None, description="本地气象预报预判")


class RunRequest(BaseModel):
    sensor_data: SensorData


class QueryRequest(BaseModel):
    question: str = Field(..., description="教师/后勤的自然语言问题")
    sensor_data: Optional[SensorData] = Field(None, description="当前传感器数据，不传则使用默认教室环境")


def _run_pipeline(sensor_dict):
    """跑通一次完整闭环：感知→决策→执行→预警→审计"""
    clean_data = collect.run(sensor_dict)
    action, reason = decide.run(clean_data)
    feedback, exec_msg = execute.run(action)
    warnings = interact.push_warning(clean_data)
    audit.record(
        timestamp=clean_data.get("collect_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        env_snapshot=clean_data,
        reasoning=reason,
        command=action,
        feedback=feedback,
    )
    return clean_data, action, reason, feedback, exec_msg, warnings


@app.get("/", summary="健康检查")
def health():
    return {"status": "ok", "service": "教室环境智能调控智能体"}


@app.post("/agent/run", summary="执行一次完整调控闭环")
def run_agent(req: RunRequest):
    """接收传感器数据，执行感知→决策→执行→预警→审计完整闭环，返回调控结果"""
    data, action, reason, feedback, exec_msg, warnings = _run_pipeline(req.sensor_data.model_dump())
    return {
        "env_snapshot": data,
        "action": action,
        "reason": reason,
        "hardware_feedback": feedback,
        "exec_msg": exec_msg,
        "warnings": warnings,
    }


@app.post("/agent/query", summary="自然语言问答")
def query_agent(req: QueryRequest):
    """接收教师/后勤的自然语言问题与可选传感器数据，返回智能体语音回复与当前调控策略"""
    if req.sensor_data is not None:
        sensor_dict = req.sensor_data.model_dump()
    else:
        sensor_dict = {
            "co2": 950, "temperature": 24, "humidity": 55, "pm25": 35,
            "noise": 45, "noise_type": "teacher", "outdoor_noise": 48,
            "outdoor_pm25": 40, "rain": False, "period": "class",
            "region": "south", "season": "autumn", "age_stage": "middle",
            "weather_alert": "none",
        }
    data, action, reason, feedback, exec_msg, warnings = _run_pipeline(sensor_dict)
    reply = interact.voice_query(req.question, data, action, reason)
    return {
        "reply": reply,
        "action": action,
        "reason": reason,
        "exec_msg": exec_msg,
        "warnings": warnings,
    }


@app.get("/agent/log", summary="获取五元组审计日志")
def get_log():
    """返回全部五元组决策日志(时间戳→环境快照→推理依据→执行指令→设备反馈)"""
    return {"count": len(audit.log_list), "logs": audit.log_list}


@app.post("/agent/manual", summary="手动操作(高风险操作触发确认保护)")
def manual_control(
    op: str = Query(..., description="操作名:close_fresh_air/close_window/stop_ventilation等"),
    sensor_data: Optional[SensorData] = None,
):
    """教师手动操作设备，高风险操作触发确认保护提示风险"""
    sensor_dict = sensor_data.model_dump() if sensor_data else {}
    ok, msg = interact.manual_control(op, sensor_dict)
    return {"need_confirm": not ok, "msg": msg}


@app.post("/agent/confirm", summary="确认手动操作")
def confirm_op():
    """对触发确认保护的手动操作进行二次确认放行"""
    op, confirmed, msg = interact.confirm()
    return {"op": op, "confirmed": confirmed, "msg": msg}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)