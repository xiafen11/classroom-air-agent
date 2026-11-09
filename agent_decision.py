# agent_decision.py AI智能决策引擎（三位一体之决策层）
# 叠加差异化自适应调控：地域·季节·突变天气·学龄段·气象预报预判五位一体
CO2_STANDARD = 1000
PM25_STANDARD = 75
TEMP_COMFORT = (18, 26)
OUTDOOR_NOISE_LIMIT = 55

AGE_PROFILES = {
    "kindergarten": {"temp_comfort": (20, 26), "co2_warn": 800,
                     "window_scale": 0.6, "fresh_air_cap": 3, "label": "幼儿园/小学低年级"},
    "primary": {"temp_comfort": (18, 26), "co2_warn": 900,
                "window_scale": 0.8, "fresh_air_cap": 4, "label": "小学"},
    "middle": {"temp_comfort": (18, 26), "co2_warn": 1000,
               "window_scale": 1.0, "fresh_air_cap": 4, "label": "中学"},
    "university": {"temp_comfort": (18, 26), "co2_warn": 1000,
                   "window_scale": 1.0, "fresh_air_cap": 4, "fresh_air_boost": 1, "label": "高校"},
}


class DecisionAgent:
    """AI Agent核心大脑：通用决策引擎之上叠加差异化自适应调控"""

    def run(self, data):
        co2 = data.get("co2")
        outdoor_noise = data.get("outdoor_noise")
        noise_type = data.get("noise_type", "none")
        pm25 = data.get("pm25")
        outdoor_pm25 = data.get("outdoor_pm25")
        temp = data.get("temperature")
        humidity = data.get("humidity")
        rain = data.get("rain", False)
        period = data.get("period", "class")
        region = data.get("region", "south")
        season = data.get("season", "spring_autumn")
        age_stage = data.get("age_stage", "middle")
        weather_alert = data.get("weather_alert", "none")
        forecast = data.get("forecast")

        window = 0
        fresh_air = 0
        mode = "自然通风"
        ac_target_temp = None
        warn = False
        reasons = []

        # ===== 时段策略分叉 =====
        if period == "class":
            outdoor_noisy = (outdoor_noise is not None and outdoor_noise > OUTDOOR_NOISE_LIMIT) or noise_type == "outdoor"
            if outdoor_noisy:
                window = 0
                fresh_air = 3
                mode = "内循环净化"
                reasons.append(f"上课时段拾音阵列判定室外噪音过高({outdoor_noise}dB)，关闭外窗避免干扰授课，切换新风内循环净化模式")
            elif co2 is not None and co2 > CO2_STANDARD:
                window = 30
                fresh_air = 2
                mode = "低噪换气"
                reasons.append(f"上课时段CO₂超标({co2}ppm)，采用低噪音通风方式：小开窗+新风中档换气")
            else:
                window = 20
                fresh_air = 1
                mode = "低噪换气"
                reasons.append("上课时段空气质量达标，低档新风维持新鲜度，保障授课安静环境")
        else:
            if co2 is not None and co2 > CO2_STANDARD:
                window = 80
                fresh_air = 4
                mode = "快速换气"
                reasons.append(f"课间CO₂超标({co2}ppm)，放宽降噪约束，大开窗+新风最高档快速稀释室内气溶胶，降低病毒累积风险")
            else:
                window = 60
                fresh_air = 2
                mode = "快速换气"
                reasons.append("课间时段快速换气，为下节课储备良好空气")

        # ===== 雨天禁开窗 =====
        if rain:
            window = 0
            reasons.append("室外下雨，关闭外窗防止雨水侵入，由新风承担换气")

        # ===== PM2.5 协同 =====
        if pm25 is not None and pm25 > PM25_STANDARD:
            if outdoor_pm25 is not None and outdoor_pm25 > pm25:
                window = min(window, 10)
                mode = "内循环净化"
                reasons.append(f"室内PM2.5超标({pm25})且室外更差({outdoor_pm25})，关窗依赖新风内循环净化")
            else:
                fresh_air = max(fresh_air, 3)
                reasons.append(f"室内PM2.5超标({pm25})，提升新风档位加强过滤")

        # ===== 气象预报预判式前置调控 =====
        if forecast and forecast.get("alerts"):
            fc_source = forecast.get("source", "公开气象预报API")
            fc_time = forecast.get("forecast_time", "")
            pre_actions = []
            for fa in forecast["alerts"]:
                if fa == "cold_wave":
                    window = min(window, max(10, window // 2))
                    fresh_air = max(fresh_air, 3)
                    ac_target_temp = 24
                    pre_actions.append("预判寒潮降温：提前收窄开窗最大开度、提高新风内循环占比、联动空调预补偿室温，避免教室内温度断崖式下跌")
                elif fa in ("dust_storm", "heavy_pollution"):
                    window = 0
                    mode = "内循环净化"
                    fresh_air = max(fresh_air, 3)
                    pre_actions.append("预判大风沙尘/重污染：提前关闭电动外窗，强制切换新风净化模式，规避室外颗粒物扬尘涌入教室")
                elif fa == "heavy_rain":
                    window = min(window, 15)
                    ac_target_temp = 25
                    pre_actions.append("预判暴雨高湿：减少开窗通风，新风除湿+空调除湿协同运行，抑制室内结露与高湿闷热")
                elif fa == "heat_wave":
                    if period == "class":
                        window = min(window, 15)
                        fresh_air = min(fresh_air, 2)
                    ac_target_temp = 23
                    pre_actions.append("预判高温热浪：课前课间优先完成换气，上课减少开窗引入室外热空气，依靠空调控温+新风低档位换气")
                elif fa == "typhoon":
                    window = 0
                    mode = "内循环净化"
                    fresh_air = max(fresh_air, 3)
                    ac_target_temp = 26
                    pre_actions.append("预判台风来袭：提前关闭电动外窗防风雨侵袭，切换新风内循环+空调除湿控温，保障师生安全与室内温湿稳定")
                elif fa == "snowstorm":
                    window = 0
                    fresh_air = max(fresh_air, 3)
                    ac_target_temp = 24
                    pre_actions.append("预判暴雪：提前关闭外窗防积雪倒灌与冷风渗透，新风换气+空调供暖补偿，维持室内温暖")
                elif fa == "gale":
                    window = 0
                    fresh_air = max(fresh_air, 2)
                    pre_actions.append("预判大风：关闭外窗防风噪干扰授课与扬尘涌入，新风承担换气")
                elif fa == "returning_humidity":
                    window = 0
                    mode = "内循环净化"
                    fresh_air = max(fresh_air, 3)
                    ac_target_temp = 25
                    pre_actions.append("预判回南天极端高湿：关闭外窗阻断暖湿气流，新风除湿+空调除湿协同，防止墙面地面结露与霉变")
            if co2 is not None and co2 > 1200 and window == 0:
                window = 15
                fresh_air = max(fresh_air, 3)
                pre_actions.append("校验兜底：本地实测CO₂严重超标，预报仅作前置参考，恢复适度开窗保障换气")
            reasons.append(f"【气象预报预判·来源{fc_source}·预报时间{fc_time}】" + "；".join(pre_actions) + "（预报仅作前置参考，最终以本地实测为准，气象触发记录已入五元组日志）")

        # ===== 季节性差异调整（全年全时段覆盖） =====
        if season == "winter":
            window = min(window, max(10, window // 2))
            fresh_air = max(fresh_air, 2)
            reasons.append("冬季严寒期优先保障温湿度稳定，受限通风+新风承担换气，避免体感剧烈波动")
        elif season == "heating_season":
            window = min(window, max(10, window // 2))
            fresh_air = max(fresh_air, 3)
            reasons.append("北方供暖季教室密闭性强、空气干燥且CO₂累积快，受限通风并加强新风换气，联动加湿维持湿度")
        elif season == "summer":
            window = min(window, max(10, window // 2))
            fresh_air = max(fresh_air, 2)
            reasons.append("夏季高温高湿期优先保障温湿度稳定，受限通风+新风承担换气，避免室外热湿空气涌入")
        elif season == "plum_rain":
            window = min(window, 15)
            fresh_air = max(fresh_air, 3)
            reasons.append("梅雨季持续高湿，严格限制开窗防室外湿气侵入，新风除湿承担换气，抑制室内结露与霉变")
        elif season == "spring":
            window = min(100, int(window * 1.2) + 10)
            fresh_air = min(4, fresh_air + 1)
            reasons.append("春季花粉与换季呼吸道传染病高发期，加大通风换气强度快速稀释室内气溶胶（室外花粉/飞絮浓度高时由预报预判限窗）")
        else:  # autumn
            window = min(100, int(window * 1.3) + 10)
            fresh_air = min(4, fresh_air + 1)
            reasons.append("秋季秋高气爽空气本底优良，最大化自然通风换气，为冬季前储备良好室内环境")

        # ===== 地域性差异调整 =====
        if region == "north":
            if temp is not None and temp <= TEMP_COMFORT[0] + 2:
                window = min(window, 15)
                fresh_air = max(fresh_air, 3)
                reasons.append(f"北方供暖期室内偏冷({temp}℃)，限制开窗幅度至{window}%避免体感骤降，提升新风至{fresh_air}档承担换气并配合温度补偿")
            else:
                fresh_air = max(fresh_air, 2)
                reasons.append("北方供暖期教室密闭性强、CO₂累积速度快，适度加强新风换气")
        elif region == "south":
            if humidity is not None and humidity > 70:
                window = min(window, 20)
                fresh_air = max(fresh_air, 3)
                reasons.append(f"南方高湿环境(湿度{humidity}%)，限制开窗防室外湿气侵入，提升新风至{fresh_air}档配合除湿，缓解潮湿闷热")
            elif humidity is not None and humidity > 60:
                fresh_air = max(fresh_air, 2)
                reasons.append(f"南方湿度偏高({humidity}%)，适度加强新风换气辅助除湿")
        elif region == "coastal_industrial":
            window = min(window, 20)
            fresh_air = max(fresh_air, 3)
            if outdoor_pm25 is not None and outdoor_pm25 > PM25_STANDARD:
                window = 0
                mode = "内循环净化"
            reasons.append("沿海/工业区室外空气质量本底较差，限制开窗降低室外污染向室内扩散，优先保障新风净化与PM2.5过滤")
        elif region == "northwest_arid":
            if humidity is not None and humidity < 30:
                fresh_air = max(fresh_air, 2)
                reasons.append(f"西北干旱区空气干燥(湿度{humidity}%)，新风换气同时联动加湿模块维持教室湿度，避免呼吸道黏膜干燥")
            if outdoor_pm25 is not None and outdoor_pm25 > PM25_STANDARD:
                window = 0
                mode = "内循环净化"
                reasons.append(f"西北沙尘天气室外PM2.5偏高({outdoor_pm25})，关闭外窗防沙尘涌入，新风内循环净化+加湿沉降颗粒物")
            else:
                window = min(window, 30)
                reasons.append("西北昼夜温差大，限制开窗幅度防冷风直灌引起体感骤变")
        elif region == "qinghai_tibet":
            window = min(window, 15)
            fresh_air = max(fresh_air, 3)
            reasons.append("青藏高原高海拔缺氧环境，严格限制开窗防冷风，新风辅助增氧换气保障师生血氧与专注力")
        elif region == "central_plain":
            if outdoor_pm25 is not None and outdoor_pm25 > PM25_STANDARD:
                window = 0
                mode = "内循环净化"
                reasons.append(f"华北平原雾霾本底偏高(室外PM2.5={outdoor_pm25})，关闭外窗防霾渗透，新风内循环净化优先")
            else:
                window = min(window, 25)
                fresh_air = max(fresh_air, 2)
                reasons.append("华北平原秋冬雾霾频发，限制开窗幅度，新风净化承担换气")
        else:  # southwest_plateau
            if (outdoor_pm25 is not None and outdoor_pm25 <= PM25_STANDARD
                    and outdoor_noise is not None and outdoor_noise <= OUTDOOR_NOISE_LIMIT):
                window = min(100, int(window * 1.3) + 10)
                reasons.append("西南高原空气本底优良、气候温和，自然通风优先，最大化利用室外新鲜空气并节能")
            else:
                fresh_air = max(fresh_air, 2)
                reasons.append("西南高原室外空气欠佳时适度加强新风换气")

        # ===== 年龄阶段感知能力差异调整 =====
        profile = AGE_PROFILES.get(age_stage, AGE_PROFILES["middle"])
        window = min(window, int(window * profile["window_scale"]))
        fresh_air = min(fresh_air, profile["fresh_air_cap"])
        if "fresh_air_boost" in profile:
            fresh_air = min(4, fresh_air + profile["fresh_air_boost"])
        if age_stage == "kindergarten":
            reasons.append(f"{profile['label']}儿童体温调节与耐受能力较弱、对温湿度变化更敏感，调控步长保守温和(开窗幅度×{profile['window_scale']}、新风≤{profile['fresh_air_cap']}档)，避免温度骤变与噪声惊扰")
        elif age_stage == "primary":
            reasons.append(f"{profile['label']}学童耐受能力尚在发育，适度保守调控(开窗幅度×{profile['window_scale']})")
        elif age_stage == "middle":
            reasons.append(f"{profile['label']}专注力需求高，课堂降噪与空气质量保障并重")
        elif age_stage == "university":
            reasons.append(f"{profile['label']}人员密度大、连续授课时长更长，CO₂累积更快，适度加大换气强度(+{profile.get('fresh_air_boost', 0)}档)")

        # ===== 突变天气应急调整 =====
        if weather_alert in ("cold_wave", "heat_wave", "heavy_rain", "dust_storm", "heavy_haze"):
            if weather_alert in ("heavy_rain", "dust_storm", "heavy_haze"):
                window = 0
            else:
                window = min(window, 10)
            fresh_air = max(fresh_air, 3)
            if weather_alert in ("dust_storm", "heavy_haze"):
                mode = "内循环净化"
            if weather_alert == "cold_wave":
                ac_target_temp = 24
            elif weather_alert == "heat_wave":
                ac_target_temp = 22
            elif weather_alert == "heavy_rain":
                ac_target_temp = 25
            alert_names = {"cold_wave": "寒潮骤降", "heat_wave": "高温热浪", "heavy_rain": "强降水",
                           "dust_storm": "大风沙尘", "heavy_haze": "重度雾霾"}
            reasons.append(f"突发{alert_names[weather_alert]}，启动应急调控预案：以温湿度稳定为优先，切换受限通风与空调温控协同模式(目标{ac_target_temp}℃)，先稳定室内温湿度再逐步恢复换气；已向教师、后勤推送突变天气提示与预期影响")

        # ===== 温控协同 =====
        if temp is not None and (temp < TEMP_COMFORT[0] or temp > TEMP_COMFORT[1]):
            reasons.append(f"室内温度{temp}℃超出舒适区间，已交由空调调节；智能体仅负责换气，不使用通风替代温控")

        # ===== 超标预警触发 =====
        if co2 is not None and co2 > CO2_STANDARD:
            warn = True
            reasons.append(f"CO₂超过《室内空气质量标准》限值{CO2_STANDARD}ppm，触发预警推送")

        action = {"window": window, "fresh_air": fresh_air, "mode": mode, "warn": warn}
        if ac_target_temp is not None:
            action["ac_target_temp"] = ac_target_temp
        reason = "；".join(reasons)
        return action, reason