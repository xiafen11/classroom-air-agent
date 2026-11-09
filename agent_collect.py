# agent_collect.py 硬件感知基座（三位一体之感知层）
# 多源感知：CO2/温湿度/PM2.5传感器 + 拾音阵列噪声分类 + 校园课表时段
#           + 室外天气 + 定位服务(地域气候分区/季节/学龄段) + 突变天气监测
#           + 气象预报API联动；数据上传运维云平台预处理后交付决策引擎
import copy
from datetime import datetime


class CollectAgent:
    """物联网传感与执行硬件的物理底座，完成环境数据采集与预处理清洗。
    硬件为成熟量产设备（平均无故障≥30000小时，单台故障率<0.3%），无需额外研发"""

    RANGES = {
        "co2": (400, 5000),
        "temperature": (-10, 50),
        "humidity": (0, 100),
        "pm25": (0, 500),
        "noise": (0, 120),
        "outdoor_noise": (0, 120),
        "outdoor_pm25": (0, 500),
    }
    NOISE_TYPES = ("teacher", "student", "equipment", "outdoor", "none")
    PERIODS = ("class", "break")
    REGIONS = ("north", "south", "coastal_industrial",
               "northwest_arid", "qinghai_tibet",
               "central_plain", "southwest_plateau")  # 7大气候分区
    SEASONS = ("spring", "summer", "autumn", "winter",
               "plum_rain", "heating_season")  # 全年全时段：四季+梅雨季+供暖季
    AGE_STAGES = ("kindergarten", "primary", "middle", "university")
    WEATHER_ALERTS = ("none", "cold_wave", "heat_wave", "heavy_rain",
                      "dust_storm", "heavy_haze")  # 6种突变天气
    FORECAST_ALERTS = ("cold_wave", "heat_wave", "heavy_rain", "dust_storm",
                       "heavy_pollution", "typhoon", "snowstorm", "gale",
                       "returning_humidity")  # 9种本地气象预报预警

    def run(self, raw_data):
        """数据采集+清洗：过滤异常传感器数值，输出标准化环境快照"""
        data = copy.deepcopy(raw_data)
        for key, (low, high) in self.RANGES.items():
            if key in data and data[key] is not None:
                if not (isinstance(data[key], (int, float)) and low <= data[key] <= high):
                    data[key] = None
        if data.get("noise_type") not in self.NOISE_TYPES:
            data["noise_type"] = "none"
        if data.get("period") not in self.PERIODS:
            data["period"] = "class"
        if data.get("region") not in self.REGIONS:
            data["region"] = "south"
        if data.get("season") not in self.SEASONS:
            data["season"] = "autumn"
        if data.get("age_stage") not in self.AGE_STAGES:
            data["age_stage"] = "middle"
        if data.get("weather_alert") not in self.WEATHER_ALERTS:
            data["weather_alert"] = "none"
        forecast = data.get("forecast")
        if not isinstance(forecast, dict):
            data["forecast"] = None
        else:
            fc = copy.deepcopy(forecast)
            fc.setdefault("source", "公开气象预报API")
            fc.setdefault("forecast_time", "")
            alerts = fc.get("alerts", [])
            if not isinstance(alerts, list):
                alerts = []
            fc["alerts"] = [a for a in alerts if a in self.FORECAST_ALERTS]
            for key in ("temp_drop", "temp_rise", "wind_level", "humidity_rise", "pm25_rise"):
                v = fc.get(key)
                if v is not None and not (isinstance(v, (int, float)) and v >= 0):
                    fc[key] = None
            data["forecast"] = fc
        data["rain"] = bool(data.get("rain", False))
        data["collect_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return data