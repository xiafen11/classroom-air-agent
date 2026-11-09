# agent_interact.py 人机协同管理平台（三位一体之管理层）
# 双向语音交互、主动预警与确认保护、多端协同、突变天气提示推送


class InteractAgent:
    """面向教师、后勤的交互与管理载体"""

    CRITICAL_OPS = {"close_fresh_air", "close_window", "stop_ventilation"}
    NOISE_TYPE_CN = {
        "teacher": "教师讲课声", "student": "学生交谈声",
        "equipment": "设备杂音", "outdoor": "室外传入噪音", "none": "环境声",
    }
    WEATHER_ALERT_CN = {
        "cold_wave": "寒潮骤降", "heat_wave": "高温热浪",
        "heavy_rain": "强降水", "dust_storm": "大风沙尘",
        "heavy_haze": "重度雾霾", "none": None,
    }
    FORECAST_ALERT_CN = {
        "cold_wave": "寒潮", "heat_wave": "高温热浪", "heavy_rain": "暴雨",
        "dust_storm": "沙尘暴", "heavy_pollution": "重污染", "typhoon": "台风",
        "snowstorm": "暴雪", "gale": "大风", "returning_humidity": "回南天",
    }

    def __init__(self):
        self.pending_confirm = None

    def voice_query(self, question, env_data, action, reason):
        q = question.replace("？", "").replace("小智", "").replace("，", "").strip()
        if "闷" in q or "空气" in q or "二氧化碳" in q or "co2" in q.lower():
            co2 = env_data.get("co2")
            if co2 is None:
                reply = "小智：抱歉，CO₂传感器数据异常，已上报后勤检查设备。"
            elif co2 > 1000:
                reply = (f"小智：教室目前有点闷，CO₂浓度{co2}ppm已超过国标1000ppm。"
                         f"当前策略：{reason}。预计5~10分钟内可降至800ppm以下，我会持续守护。")
            else:
                reply = f"小智：教室空气很清新，CO₂浓度{co2}ppm优于国标限值，请放心授课。"
        elif "雾霾" in q or "pm2.5" in q.lower() or "污染" in q or "粉尘" in q or "口罩" in q:
            pm25 = env_data.get("pm25")
            out_pm25 = env_data.get("outdoor_pm25")
            if pm25 is None:
                reply = "小智：抱歉，PM2.5传感器数据异常，已上报后勤检查设备。"
            elif pm25 > 75:
                mask_tip = ("PM2.5严重超标，建议师生减少剧烈运动，敏感体质学生可佩戴口罩"
                            if pm25 > 150 else "已加强新风内循环净化，室内颗粒物正在下降，暂无需佩戴口罩")
                reply = (f"小智：教室内PM2.5为{pm25}μg/m³已超标（室外{out_pm25}μg/m³），"
                         f"我已切换新风内循环净化模式优先过滤颗粒物。{mask_tip}。")
            else:
                reply = f"小智：教室内PM2.5为{pm25}μg/m³优于国标75限值，空气洁净，无需佩戴口罩。"
        elif "吵" in q or "噪" in q:
            noise = env_data.get("noise")
            ntype = self.NOISE_TYPE_CN.get(env_data.get("noise_type"), "环境声")
            if noise is not None and noise > 50:
                reply = (f"小智：当前室内噪音约{noise}分贝（拾音阵列识别主要为{ntype}），"
                         f"我已优先选择低噪音通风方式，不影响授课。")
            else:
                reply = f"小智：当前室内噪音约{noise}分贝（主要为{ntype}），环境安静，适合授课。"
        elif "潮湿" in q or "干燥" in q or "湿度" in q or "回南天" in q or "结露" in q or "冒水" in q:
            humidity = env_data.get("humidity")
            if humidity is None:
                reply = "小智：抱歉，湿度传感器数据异常，已上报后勤检查设备。"
            elif humidity > 70:
                reply = (f"小智：当前室内湿度{humidity}%偏高，我已限制开窗并联动新风除湿，"
                         f"防止墙面结露与霉菌滋生，预计可逐步降至60%以下。")
            elif humidity < 30:
                reply = (f"小智：当前室内湿度{humidity}%偏低，空气偏干燥，"
                         f"我已联动新风加湿模块维持舒适湿度，缓解师生呼吸道干燥不适。")
            else:
                reply = f"小智：当前室内湿度{humidity}%处于舒适区间，体感适宜。"
        elif "预报" in q or "天气" in q or "台风" in q or "寒潮" in q or "沙尘" in q or "暴雪" in q:
            forecast = env_data.get("forecast")
            if isinstance(forecast, dict) and forecast.get("alerts"):
                alerts_cn = "、".join(self.FORECAST_ALERT_CN.get(a, a) for a in forecast["alerts"])
                reply = (f"小智：{forecast.get('source', '')}预报{alerts_cn}将至（预报时间{forecast.get('forecast_time', '')}），"
                         f"我已提前启动前置调控：关窗/收窗+新风净化+空调温湿补偿，"
                         f"以本地实测为准动态修正，请师生留意天气变化，注意安全。")
            else:
                reply = "小智：当前本地气象预报无预警信息，天气平稳，我会持续监测预报并联动调控。"
        elif "开窗" in q or "窗户" in q:
            window = action.get("window", 0) if action else 0
            if window == 0:
                reply = (f"小智：当前外窗已关闭，由新风系统承担换气。原因：{reason}。"
                         f"关窗是为了防噪音/污染/风雨侵入，室内换气量有保障，请放心。")
            else:
                reply = (f"小智：当前外窗开启{window}%配合新风换气，"
                         f"在保障安静与温湿稳定的前提下最大化自然通风。")
        elif "温度" in q or "热" in q or "冷" in q:
            temp = env_data.get("temperature")
            ac = action.get("ac_target_temp") if action else None
            ac_part = f"空调目标温度已设为{ac}℃" if ac else "温度调节由空调负责"
            reply = (f"小智：当前室内温度{temp}℃，{ac_part}，"
                     f"我负责换气，分工协作保障舒适。")
        else:
            reply = (f"小智：收到。当前CO₂{env_data.get('co2')}ppm、"
                     f"PM2.5{env_data.get('pm25')}、噪音{env_data.get('noise')}dB、"
                     f"湿度{env_data.get('humidity')}%，执行策略：{reason}。")
        return reply

    def push_warning(self, env_data):
        co2 = env_data.get("co2")
        pm25 = env_data.get("pm25")
        weather_alert = env_data.get("weather_alert", "none")
        messages = []
        if co2 is not None and co2 > 1000:
            messages.append(f"【预警推送·语音+小程序】CO₂浓度{co2}ppm超标，已自动加强通风，请关注教室空气状况")
        if pm25 is not None and pm25 > 75:
            messages.append(f"【预警推送·语音+小程序】PM2.5浓度{pm25}超标，已切换新风内循环净化模式")
        alert_cn = self.WEATHER_ALERT_CN.get(weather_alert)
        if alert_cn:
            messages.append(f"【突变天气提示·语音+小程序】检测到{alert_cn}，系统已启动应急调控预案，以温湿度稳定为优先，必要时暂缓通风，保障课堂舒适与师生健康")
        forecast = env_data.get("forecast")
        if isinstance(forecast, dict):
            for fa in forecast.get("alerts", []):
                fa_cn = self.FORECAST_ALERT_CN.get(fa)
                if fa_cn:
                    messages.append(f"【本地天气预报协同·语音+小程序】{forecast.get('source', '')}预报{fa_cn}将至，系统已前置调控（收窗/关窗+新风换气净化+空调温湿补偿），以本地实测为准动态修正")
        return messages

    def manual_control(self, op, env_data):
        if op in self.CRITICAL_OPS:
            co2 = env_data.get("co2")
            if co2 is not None and co2 > 800:
                risk = (f"当前CO₂已达{co2}ppm，关闭后浓度将快速攀升超标，"
                        f"可能导致学生困倦、注意力下降")
            else:
                risk = "关闭后室内换气量下降，长时间关闭可能导致空气品质下降"
            self.pending_confirm = op
            return False, f"⚠ 确认保护：您正在执行【{op}】。{risk}。确认执行请回复'确认'。"
        return True, f"已执行手动操作【{op}】"

    def confirm(self):
        if self.pending_confirm:
            op = self.pending_confirm
            self.pending_confirm = None
            return op, True, f"教师已确认，放行手动操作【{op}】"
        return None, False, "当前没有待确认的操作"