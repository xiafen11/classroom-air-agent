# main.py 主程序 - 可验证的AI智能体交互闭环（三位一体架构落地）
# ①硬件感知基座 + ②AI智能决策引擎 + ③人机协同管理平台
# 叠加差异化自适应调控：地域·季节·突变天气·学龄段·气象预报预判
from datetime import datetime
from agent_collect import CollectAgent
from agent_decision import DecisionAgent
from agent_execute import ExecuteAgent
from agent_audit import AuditAgent
from agent_interact import InteractAgent

collect = CollectAgent()
decide = DecisionAgent()
execute = ExecuteAgent()
interact = InteractAgent()
audit = AuditAgent()


def run_once(sensor_data, label="自动监测"):
    """跑通一次完整闭环：感知→决策→执行→预警→审计"""
    print(f"\n{'=' * 16} {label} {'=' * 16}")
    clean_data = collect.run(sensor_data)
    print(f"[感知层] 环境快照：{clean_data}")
    action, reason = decide.run(clean_data)
    print(f"[决策层] 调控策略：{action}")
    print(f"[决策层] 推理依据：{reason}")
    feedback, msg = execute.run(action)
    print(f"[执行层] {msg}")
    for w in interact.push_warning(clean_data):
        print(f"[管理层] {w}")
    audit.record(
        timestamp=clean_data.get("collect_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        env_snapshot=clean_data,
        reasoning=reason,
        command=action,
        feedback=feedback,
    )
    return clean_data, action, reason


if __name__ == "__main__":
    print("=" * 62)
    print("   可验证的AI智能体交互闭环 · 三位一体架构落地")
    print("   硬件感知基座 | AI智能决策引擎 | 人机协同管理平台")
    print("   差异化自适应调控：7大气候分区·全年6季节·6种突变天气·学龄段·9种本地天气预报协同")
    print("=" * 62)

    # ---------- 场景1：上课时段，CO₂超标，室外噪音过高 ----------
    s1 = {"co2": 1100, "temperature": 24, "humidity": 55, "pm25": 35,
          "noise": 48, "noise_type": "outdoor", "outdoor_noise": 65,
          "outdoor_pm25": 40, "rain": False, "period": "class",
          "region": "south", "season": "autumn", "age_stage": "middle",
          "weather_alert": "none"}
    d1, a1, r1 = run_once(s1, "场景1·上课CO₂超标+室外噪音高→关窗内循环")

    # ---------- 场景2：课间时段，CO₂超标，室外安静 ----------
    s2 = {"co2": 1300, "temperature": 25, "humidity": 60, "pm25": 30,
          "noise": 58, "noise_type": "student", "outdoor_noise": 45,
          "outdoor_pm25": 30, "rain": False, "period": "break",
          "region": "south", "season": "autumn", "age_stage": "middle",
          "weather_alert": "none"}
    d2, a2, r2 = run_once(s2, "场景2·课间放宽降噪→快速换气稀释气溶胶")

    # ---------- 场景3：上课时段，室外下雨 + 室内外PM2.5超标 ----------
    s3 = {"co2": 900, "temperature": 23, "humidity": 65, "pm25": 90,
          "noise": 45, "noise_type": "teacher", "outdoor_noise": 50,
          "outdoor_pm25": 120, "rain": True, "period": "class",
          "region": "south", "season": "autumn", "age_stage": "middle",
          "weather_alert": "none"}
    d3, a3, r3 = run_once(s3, "场景3·雨天+PM2.5超标→新风内循环净化")

    # ---------- 场景4：设备离线异常 → 自动告警后勤 ----------
    execute.simulate_offline = True
    s4 = {"co2": 1050, "temperature": 26, "humidity": 58, "pm25": 40,
          "noise": 50, "noise_type": "teacher", "outdoor_noise": 40,
          "outdoor_pm25": 35, "rain": False, "period": "class",
          "region": "south", "season": "autumn", "age_stage": "middle",
          "weather_alert": "none"}
    run_once(s4, "场景4·设备离线异常→自动告警后勤")
    execute.simulate_offline = False

    # ============ 四川·2026年国庆节（10月1日）差异化调控演示 ============
    # 定位：四川成都 → 南方湿热区(region=south)；10月初 → 秋季(autumn)
    # 华西秋雨时节湿度偏高；国庆假期值班教室/补课场景
    print(f"\n{'=' * 10} 四川成都·2026年国庆节(10.1)差异化自适应调控 {'=' * 10}")

    # ---------- 场景5：四川国庆·中学上课·CO₂超标+华西秋雨高湿 ----------
    s5 = {"co2": 1050, "temperature": 22, "humidity": 75, "pm25": 45,
          "noise": 46, "noise_type": "teacher", "outdoor_noise": 48,
          "outdoor_pm25": 50, "rain": False, "period": "class",
          "region": "south", "season": "autumn", "age_stage": "middle",
          "weather_alert": "none"}
    run_once(s5, "场景5·四川国庆·中学上课CO₂超标+秋雨高湿→限窗除湿+加大换气")

    # ---------- 场景6：四川国庆·课间·换季传染病高发期加大换气 ----------
    s6 = {"co2": 950, "temperature": 23, "humidity": 68, "pm25": 40,
          "noise": 55, "noise_type": "student", "outdoor_noise": 45,
          "outdoor_pm25": 42, "rain": False, "period": "break",
          "region": "south", "season": "autumn", "age_stage": "middle",
          "weather_alert": "none"}
    run_once(s6, "场景6·四川国庆·课间换季传染病高发期→加大换气稀释气溶胶")

    # ---------- 场景7：四川国庆·幼儿园上课·保守温和调控 ----------
    s7 = {"co2": 850, "temperature": 23, "humidity": 72, "pm25": 38,
          "noise": 42, "noise_type": "teacher", "outdoor_noise": 44,
          "outdoor_pm25": 40, "rain": False, "period": "class",
          "region": "south", "season": "autumn", "age_stage": "kindergarten",
          "weather_alert": "none"}
    run_once(s7, "场景7·四川国庆·幼儿园上课→保守温和调控避免惊扰")

    # ---------- 场景8：四川国庆·华西秋雨突发强降水应急 ----------
    s8 = {"co2": 980, "temperature": 21, "humidity": 85, "pm25": 42,
          "noise": 47, "noise_type": "teacher", "outdoor_noise": 52,
          "outdoor_pm25": 45, "rain": True, "period": "class",
          "region": "south", "season": "autumn", "age_stage": "middle",
          "weather_alert": "heavy_rain"}
    run_once(s8, "场景8·四川国庆·华西秋雨突发强降水→应急调控温湿稳定优先")

    # ---------- 场景9：四川国庆·气象预报预判寒潮南下 ----------
    s9 = {"co2": 900, "temperature": 20, "humidity": 65, "pm25": 38,
          "noise": 44, "noise_type": "teacher", "outdoor_noise": 42,
          "outdoor_pm25": 40, "rain": False, "period": "class",
          "region": "south", "season": "autumn", "age_stage": "middle",
          "weather_alert": "none",
          "forecast": {"source": "中央气象台公开API", "forecast_time": "2026-10-01 08:00",
                       "alerts": ["cold_wave"], "temp_drop": 10}}
    run_once(s9, "场景9·四川国庆·气象预报预判寒潮→前置收窗+新风内循环+空调预补偿")

    # ============ 广东·2026年国庆节（10月1日）差异化调控演示 ============
    # 定位：广东珠三角 → 南方湿热区(region=south)；10月初仍处夏末高温高湿(season=summer)
    # 与四川华西秋雨形成地域气候对比；沿海工业区演示coastal_industrial分区；
    # 国庆假期值班教室/补课场景，需防台风强降水与"秋老虎"高温
    print(f"\n{'=' * 10} 广东·2026年国庆节(10.1)差异化自适应调控 {'=' * 10}")

    # ---------- 场景10：广东国庆·中学上课·夏末高温高湿CO₂超标 ----------
    s10 = {"co2": 1080, "temperature": 31, "humidity": 78, "pm25": 42,
           "noise": 45, "noise_type": "teacher", "outdoor_noise": 50,
           "outdoor_pm25": 45, "rain": False, "period": "class",
           "region": "south", "season": "summer", "age_stage": "middle",
           "weather_alert": "none"}
    run_once(s10, "场景10·广东国庆·中学上课夏末高温高湿CO₂超标→受限通风+新风除湿")

    # ---------- 场景11：广东国庆·课间·高温天快速换气 ----------
    s11 = {"co2": 920, "temperature": 32, "humidity": 75, "pm25": 38,
           "noise": 56, "noise_type": "student", "outdoor_noise": 48,
           "outdoor_pm25": 40, "rain": False, "period": "break",
           "region": "south", "season": "summer", "age_stage": "middle",
           "weather_alert": "none"}
    run_once(s11, "场景11·广东国庆·课间高温天快速换气→为下节课储备空气")

    # ---------- 场景12：广东国庆·幼儿园上课·高温保守温和调控 ----------
    s12 = {"co2": 820, "temperature": 31, "humidity": 76, "pm25": 36,
           "noise": 42, "noise_type": "teacher", "outdoor_noise": 46,
           "outdoor_pm25": 38, "rain": False, "period": "class",
           "region": "south", "season": "summer", "age_stage": "kindergarten",
           "weather_alert": "none"}
    run_once(s12, "场景12·广东国庆·幼儿园上课高温天→保守温和调控避免惊扰")

    # ---------- 场景13：广东国庆·沿海工业区室外污染本底偏高 ----------
    s13 = {"co2": 950, "temperature": 30, "humidity": 72, "pm25": 55,
           "noise": 44, "noise_type": "teacher", "outdoor_noise": 48,
           "outdoor_pm25": 85, "rain": False, "period": "class",
           "region": "coastal_industrial", "season": "summer", "age_stage": "middle",
           "weather_alert": "none"}
    run_once(s13, "场景13·广东国庆·沿海工业区室外污染偏高→限窗新风净化优先")

    # ---------- 场景14：广东国庆·台风外围突发强降水应急 ----------
    s14 = {"co2": 980, "temperature": 28, "humidity": 90, "pm25": 40,
           "noise": 47, "noise_type": "teacher", "outdoor_noise": 55,
           "outdoor_pm25": 42, "rain": True, "period": "class",
           "region": "south", "season": "summer", "age_stage": "middle",
           "weather_alert": "heavy_rain"}
    run_once(s14, "场景14·广东国庆·台风外围强降水→应急调控温湿稳定优先")

    # ---------- 场景15：广东国庆·气象预报预判"秋老虎"高温热浪 ----------
    s15 = {"co2": 900, "temperature": 30, "humidity": 72, "pm25": 38,
           "noise": 44, "noise_type": "teacher", "outdoor_noise": 46,
           "outdoor_pm25": 40, "rain": False, "period": "class",
           "region": "south", "season": "summer", "age_stage": "middle",
           "weather_alert": "none",
           "forecast": {"source": "中央气象台公开API", "forecast_time": "2026-10-01 08:00",
                        "alerts": ["heat_wave"], "temp_rise": 3}}
    run_once(s15, "场景15·广东国庆·气象预报预判秋老虎高温→前置减窗+空调预补偿控温")

    # ============ 东北·2026年国庆节（10月1日）差异化调控演示 ============
    # 定位：东北沈阳/哈尔滨 → 北方供暖区(region=north)；10月初 → 秋季(autumn)但气温已低
    # 与四川华西秋雨、广东夏末高温形成地域气候对比；供暖期临近/室内偏冷、空气干燥，
    # 国庆假期值班教室/补课场景，需防寒潮骤降与秋季大风沙尘/秸秆焚烧重污染
    print(f"\n{'=' * 10} 东北·2026年国庆节(10.1)差异化自适应调控 {'=' * 10}")

    # ---------- 场景16：东北国庆·中学上课·CO₂超标+供暖期低温干燥 ----------
    s16 = {"co2": 1080, "temperature": 14, "humidity": 40, "pm25": 45,
           "noise": 46, "noise_type": "teacher", "outdoor_noise": 48,
           "outdoor_pm25": 50, "rain": False, "period": "class",
           "region": "north", "season": "autumn", "age_stage": "middle",
           "weather_alert": "none"}
    run_once(s16, "场景16·东北国庆·中学上课CO₂超标+供暖期低温→限窗防冷+新风承担换气")

    # ---------- 场景17：东北国庆·课间·低温天快速换气储备空气 ----------
    s17 = {"co2": 920, "temperature": 13, "humidity": 42, "pm25": 40,
           "noise": 55, "noise_type": "student", "outdoor_noise": 45,
           "outdoor_pm25": 42, "rain": False, "period": "break",
           "region": "north", "season": "autumn", "age_stage": "middle",
           "weather_alert": "none"}
    run_once(s17, "场景17·东北国庆·课间低温天快速换气→为下节课储备空气")

    # ---------- 场景18：东北国庆·幼儿园上课·低温保守温和调控 ----------
    s18 = {"co2": 850, "temperature": 14, "humidity": 40, "pm25": 38,
           "noise": 42, "noise_type": "teacher", "outdoor_noise": 44,
           "outdoor_pm25": 40, "rain": False, "period": "class",
           "region": "north", "season": "autumn", "age_stage": "kindergarten",
           "weather_alert": "none"}
    run_once(s18, "场景18·东北国庆·幼儿园上课低温天→保守温和调控避免惊扰")

    # ---------- 场景19：东北国庆·突发寒潮骤降应急 ----------
    s19 = {"co2": 980, "temperature": 8, "humidity": 55, "pm25": 42,
           "noise": 47, "noise_type": "teacher", "outdoor_noise": 52,
           "outdoor_pm25": 45, "rain": True, "period": "class",
           "region": "north", "season": "autumn", "age_stage": "middle",
           "weather_alert": "cold_wave"}
    run_once(s19, "场景19·东北国庆·突发寒潮初雪→应急调控温湿稳定优先")

    # ---------- 场景20：东北国庆·气象预报预判大风沙尘/秸秆焚烧重污染 ----------
    s20 = {"co2": 900, "temperature": 12, "humidity": 45, "pm25": 80,
           "noise": 44, "noise_type": "teacher", "outdoor_noise": 50,
           "outdoor_pm25": 150, "rain": False, "period": "class",
           "region": "north", "season": "autumn", "age_stage": "middle",
           "weather_alert": "none",
           "forecast": {"source": "中央气象台公开API", "forecast_time": "2026-10-01 08:00",
                        "alerts": ["heavy_pollution"], "pm25_rise": 80}}
    run_once(s20, "场景20·东北国庆·气象预报预判大风沙尘重污染→前置关窗+新风内循环净化")

    # ============ 全年全时段·7大气候分区·本地天气预报协同调控 ============
    print(f"\n{'=' * 10} 全年全时段·7大气候分区·本地天气预报协同调控 {'=' * 10}")
    YEAR_ROUND = [
        # ---- 1月·隆冬/供暖季 ----
        {"label": "场景21·东北沈阳·1月供暖季干燥密闭CO₂累积+本地预报暴雪→关窗新风加湿",
         "data": {"co2": 1150, "temperature": 20, "humidity": 28, "pm25": 55,
                  "noise": 46, "noise_type": "teacher", "outdoor_noise": 50,
                  "outdoor_pm25": 60, "rain": False, "period": "class",
                  "region": "north", "season": "heating_season", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "沈阳气象台公开API", "forecast_time": "2026-01-12 07:30",
                               "alerts": ["snowstorm"], "temp_drop": 12}}},
        {"label": "场景22·青藏那曲·1月严寒缺氧+本地预报暴雪→限窗新风增氧+空调补偿",
         "data": {"co2": 1000, "temperature": 8, "humidity": 35, "pm25": 30,
                  "noise": 45, "noise_type": "teacher", "outdoor_noise": 48,
                  "outdoor_pm25": 25, "rain": False, "period": "class",
                  "region": "qinghai_tibet", "season": "winter", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "西藏气象台公开API", "forecast_time": "2026-01-12 07:00",
                               "alerts": ["snowstorm"], "temp_drop": 15}}},
        {"label": "场景23·华南广州·1月湿冷无集中供暖+本地预报寒潮→限窗新风+空调预补偿",
         "data": {"co2": 980, "temperature": 12, "humidity": 75, "pm25": 40,
                  "noise": 44, "noise_type": "teacher", "outdoor_noise": 46,
                  "outdoor_pm25": 42, "rain": False, "period": "class",
                  "region": "south", "season": "winter", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "广东气象台公开API", "forecast_time": "2026-01-12 08:00",
                               "alerts": ["cold_wave"], "temp_drop": 10}}},
        {"label": "场景24·华北石家庄·1月供暖期雾霾+本地预报重污染→关窗内循环净化",
         "data": {"co2": 1050, "temperature": 22, "humidity": 35, "pm25": 85,
                  "noise": 45, "noise_type": "teacher", "outdoor_noise": 48,
                  "outdoor_pm25": 160, "rain": False, "period": "class",
                  "region": "central_plain", "season": "heating_season", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "河北气象台公开API", "forecast_time": "2026-01-12 07:30",
                               "alerts": ["heavy_pollution"], "pm25_rise": 60}}},
        # ---- 3-4月·春季 ----
        {"label": "场景25·西北敦煌·4月春季沙尘暴+本地预报沙尘→关窗内循环净化+加湿",
         "data": {"co2": 950, "temperature": 18, "humidity": 20, "pm25": 120,
                  "noise": 47, "noise_type": "teacher", "outdoor_noise": 55,
                  "outdoor_pm25": 280, "rain": False, "period": "class",
                  "region": "northwest_arid", "season": "spring", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "甘肃气象台公开API", "forecast_time": "2026-04-08 07:00",
                               "alerts": ["dust_storm"], "pm25_rise": 150}}},
        {"label": "场景26·华北北京·4月春旱杨絮飞絮+本地预报大风→关窗防风防絮",
         "data": {"co2": 900, "temperature": 20, "humidity": 30, "pm25": 70,
                  "noise": 48, "noise_type": "teacher", "outdoor_noise": 58,
                  "outdoor_pm25": 90, "rain": False, "period": "class",
                  "region": "central_plain", "season": "spring", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "北京气象台公开API", "forecast_time": "2026-04-08 07:30",
                               "alerts": ["gale"], "wind_level": 7}}},
        {"label": "场景27·华南广州·3月回南天极端高湿+本地预报回南天→关窗新风除湿",
         "data": {"co2": 920, "temperature": 22, "humidity": 88, "pm25": 35,
                  "noise": 44, "noise_type": "teacher", "outdoor_noise": 46,
                  "outdoor_pm25": 38, "rain": False, "period": "class",
                  "region": "south", "season": "spring", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "广东气象台公开API", "forecast_time": "2026-03-15 07:00",
                               "alerts": ["returning_humidity"], "humidity_rise": 15}}},
        {"label": "场景28·西南昆明·4月春季干暖空气优→自然通风优先+节能",
         "data": {"co2": 850, "temperature": 22, "humidity": 45, "pm25": 20,
                  "noise": 45, "noise_type": "student", "outdoor_noise": 42,
                  "outdoor_pm25": 18, "rain": False, "period": "break",
                  "region": "southwest_plateau", "season": "spring", "age_stage": "kindergarten",
                  "weather_alert": "none"}},
        {"label": "场景29·东北长春·4月春季大风+本地预报大风→关窗防风噪",
         "data": {"co2": 900, "temperature": 12, "humidity": 35, "pm25": 60,
                  "noise": 50, "noise_type": "teacher", "outdoor_noise": 62,
                  "outdoor_pm25": 80, "rain": False, "period": "class",
                  "region": "north", "season": "spring", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "吉林气象台公开API", "forecast_time": "2026-04-08 07:00",
                               "alerts": ["gale"], "wind_level": 8}}},
        # ---- 6-7月·夏季/梅雨季 ----
        {"label": "场景30·长江中下游武汉·6月梅雨季持续高湿+本地预报暴雨→限窗新风除湿",
         "data": {"co2": 1050, "temperature": 26, "humidity": 85, "pm25": 35,
                  "noise": 46, "noise_type": "teacher", "outdoor_noise": 50,
                  "outdoor_pm25": 30, "rain": True, "period": "class",
                  "region": "south", "season": "plum_rain", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "湖北气象台公开API", "forecast_time": "2026-06-20 07:30",
                               "alerts": ["heavy_rain"], "humidity_rise": 10}}},
        {"label": "场景31·华南深圳·7月台风来袭+本地预报台风红色预警→关窗内循环+空调除湿",
         "data": {"co2": 980, "temperature": 28, "humidity": 82, "pm25": 40,
                  "noise": 48, "noise_type": "teacher", "outdoor_noise": 60,
                  "outdoor_pm25": 42, "rain": True, "period": "class",
                  "region": "south", "season": "summer", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "深圳气象台公开API", "forecast_time": "2026-07-18 06:00",
                               "alerts": ["typhoon"], "wind_level": 12}}},
        {"label": "场景32·沿海工业区宁波·7月台风+工业污染叠加+本地预报台风→关窗净化",
         "data": {"co2": 950, "temperature": 29, "humidity": 80, "pm25": 65,
                  "noise": 46, "noise_type": "teacher", "outdoor_noise": 58,
                  "outdoor_pm25": 95, "rain": True, "period": "class",
                  "region": "coastal_industrial", "season": "summer", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "浙江气象台公开API", "forecast_time": "2026-07-18 06:00",
                               "alerts": ["typhoon"], "wind_level": 11}}},
        {"label": "场景33·华北济南·7月高温热浪+本地预报高温→减窗+空调预补偿控温",
         "data": {"co2": 1000, "temperature": 33, "humidity": 55, "pm25": 50,
                  "noise": 45, "noise_type": "teacher", "outdoor_noise": 48,
                  "outdoor_pm25": 55, "rain": False, "period": "class",
                  "region": "central_plain", "season": "summer", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "山东气象台公开API", "forecast_time": "2026-07-10 08:00",
                               "alerts": ["heat_wave"], "temp_rise": 4}}},
        {"label": "场景34·西北吐鲁番·7月极端干热+本地预报高温热浪→关窗+空调+加湿",
         "data": {"co2": 980, "temperature": 38, "humidity": 15, "pm25": 45,
                  "noise": 45, "noise_type": "teacher", "outdoor_noise": 47,
                  "outdoor_pm25": 50, "rain": False, "period": "class",
                  "region": "northwest_arid", "season": "summer", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "新疆气象台公开API", "forecast_time": "2026-07-10 07:00",
                               "alerts": ["heat_wave"], "temp_rise": 3}}},
        {"label": "场景35·青藏拉萨·7月夏季凉爽紫外线强→适度通风+新风增氧",
         "data": {"co2": 900, "temperature": 22, "humidity": 40, "pm25": 15,
                  "noise": 44, "noise_type": "student", "outdoor_noise": 45,
                  "outdoor_pm25": 12, "rain": False, "period": "break",
                  "region": "qinghai_tibet", "season": "summer", "age_stage": "university",
                  "weather_alert": "none"}},
        {"label": "场景36·西南贵阳·7月雨季凉爽+本地预报暴雨→限窗新风换气",
         "data": {"co2": 920, "temperature": 24, "humidity": 78, "pm25": 28,
                  "noise": 45, "noise_type": "teacher", "outdoor_noise": 48,
                  "outdoor_pm25": 25, "rain": False, "period": "class",
                  "region": "southwest_plateau", "season": "summer", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "贵州气象台公开API", "forecast_time": "2026-07-10 07:30",
                               "alerts": ["heavy_rain"], "humidity_rise": 12}}},
        # ---- 9-10月·秋季 ----
        {"label": "场景37·东北沈阳·10月秋高气爽空气优→加大自然通风",
         "data": {"co2": 950, "temperature": 16, "humidity": 45, "pm25": 25,
                  "noise": 48, "noise_type": "student", "outdoor_noise": 45,
                  "outdoor_pm25": 22, "rain": False, "period": "break",
                  "region": "north", "season": "autumn", "age_stage": "primary",
                  "weather_alert": "none"}},
        {"label": "场景38·华北石家庄·10月秸秆焚烧突发重度雾霾应急→关窗内循环净化",
         "data": {"co2": 1000, "temperature": 18, "humidity": 50, "pm25": 95,
                  "noise": 45, "noise_type": "teacher", "outdoor_noise": 48,
                  "outdoor_pm25": 180, "rain": False, "period": "class",
                  "region": "central_plain", "season": "autumn", "age_stage": "middle",
                  "weather_alert": "heavy_haze"}},
        {"label": "场景39·四川成都·10月华西秋雨高湿+本地预报秋雨→限窗新风除湿",
         "data": {"co2": 1020, "temperature": 19, "humidity": 80, "pm25": 38,
                  "noise": 46, "noise_type": "teacher", "outdoor_noise": 50,
                  "outdoor_pm25": 40, "rain": True, "period": "class",
                  "region": "south", "season": "autumn", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "四川气象台公开API", "forecast_time": "2026-10-15 07:00",
                               "alerts": ["heavy_rain"], "humidity_rise": 8}}},
        {"label": "场景40·西北敦煌·10月秋季沙尘+本地预报沙尘→关窗内循环净化+加湿",
         "data": {"co2": 930, "temperature": 15, "humidity": 22, "pm25": 90,
                  "noise": 47, "noise_type": "teacher", "outdoor_noise": 52,
                  "outdoor_pm25": 200, "rain": False, "period": "class",
                  "region": "northwest_arid", "season": "autumn", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "甘肃气象台公开API", "forecast_time": "2026-10-15 07:00",
                               "alerts": ["dust_storm"], "pm25_rise": 100}}},
        # ---- 11-12月·初冬/供暖季 ----
        {"label": "场景41·东北沈阳·11月供暖季开始干燥密闭+本地预报寒潮→限窗新风加湿",
         "data": {"co2": 1080, "temperature": 19, "humidity": 30, "pm25": 50,
                  "noise": 46, "noise_type": "teacher", "outdoor_noise": 48,
                  "outdoor_pm25": 55, "rain": False, "period": "class",
                  "region": "north", "season": "heating_season", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "沈阳气象台公开API", "forecast_time": "2026-11-15 07:30",
                               "alerts": ["cold_wave"], "temp_drop": 12}}},
        {"label": "场景42·西南昆明·11月初冬晴好空气优→自然通风优先",
         "data": {"co2": 880, "temperature": 15, "humidity": 50, "pm25": 22,
                  "noise": 46, "noise_type": "student", "outdoor_noise": 44,
                  "outdoor_pm25": 20, "rain": False, "period": "break",
                  "region": "southwest_plateau", "season": "autumn", "age_stage": "middle",
                  "weather_alert": "none"}},
        {"label": "场景43·沿海工业区青岛·12月冬季海风+工业污染+本地预报大风→关窗净化",
         "data": {"co2": 960, "temperature": 5, "humidity": 55, "pm25": 70,
                  "noise": 47, "noise_type": "teacher", "outdoor_noise": 60,
                  "outdoor_pm25": 110, "rain": False, "period": "class",
                  "region": "coastal_industrial", "season": "winter", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "山东气象台公开API", "forecast_time": "2026-12-10 07:30",
                               "alerts": ["gale"], "wind_level": 8}}},
        {"label": "场景44·青藏那曲·12月严寒+本地预报寒潮→限窗新风增氧+空调补偿",
         "data": {"co2": 990, "temperature": -5, "humidity": 30, "pm25": 25,
                  "noise": 45, "noise_type": "teacher", "outdoor_noise": 50,
                  "outdoor_pm25": 20, "rain": False, "period": "class",
                  "region": "qinghai_tibet", "season": "winter", "age_stage": "middle",
                  "weather_alert": "none",
                  "forecast": {"source": "西藏气象台公开API", "forecast_time": "2026-12-10 07:00",
                               "alerts": ["cold_wave"], "temp_drop": 10}}},
    ]
    year_results = {}
    for sc in YEAR_ROUND:
        d_y, a_y, r_y = run_once(sc["data"], sc["label"])
        year_results[sc["label"].split("·")[0]] = (d_y, a_y, r_y)

    # ================= 人机协同·双向语音交互（场景化具体问答） =================
    print(f"\n{'=' * 16} 人机协同·双向语音交互 {'=' * 16}")

    # 问答1·东北供暖季+暴雪预报：教师关心开窗与保暖
    d21, a21, r21 = year_results["场景21"]
    print("教师：小智，气象台说今天有大暴雪，窗户还开着吗？孩子们会不会冷？")
    print(interact.voice_query("小智，气象台说今天有大暴雪，窗户还开着吗？孩子们会不会冷？", d21, a21, r21))

    # 问答2·华北供暖期雾霾：教师关心PM2.5与口罩
    d24, a24, r24 = year_results["场景24"]
    print("\n教师：小智，外面灰蒙蒙的，今天雾霾重不重？孩子们需要戴口罩吗？")
    print(interact.voice_query("小智，外面灰蒙蒙的，今天雾霾重不重？孩子们需要戴口罩吗？", d24, a24, r24))

    # 问答3·广州回南天：教师关心墙面结露与潮湿
    d27, a27, r27 = year_results["场景27"]
    print("\n教师：小智，教室墙面和黑板都冒水珠了，是不是回南天？湿度多少？怎么办？")
    print(interact.voice_query("小智，教室墙面和黑板都冒水珠了，是不是回南天？湿度多少？怎么办？", d27, a27, r27))

    # 问答4·深圳台风红色预警：教师关心天气预报与教室安全
    d31, a31, r31 = year_results["场景31"]
    print("\n教师：小智，台风红色预警了，气象预报怎么说？窗户关好了吗？教室安全吗？")
    print(interact.voice_query("小智，台风红色预警了，气象预报怎么说？窗户关好了吗？教室安全吗？", d31, a31, r31))

    # 问答5·吐鲁番极端干热：教师关心干燥与加湿
    d34, a34, r34 = year_results["场景34"]
    print("\n教师：小智，今天太干了，孩子们嗓子疼直咳嗽，教室湿度多少？能不能加湿？")
    print(interact.voice_query("小智，今天太干了，孩子们嗓子疼直咳嗽，教室湿度多少？能不能加湿？", d34, a34, r34))

    # 问答6·场景1上课室外噪音：教师关心授课环境
    print("\n教师：小智，外面工地太吵了，影响上课吗？窗户能不能关小点？")
    print(interact.voice_query("小智，外面工地太吵了，影响上课吗？窗户能不能关小点？", d1, a1, r1))

    # ================= 人机协同·主动预警与确认保护 =================
    print(f"\n{'=' * 16} 人机协同·确认保护 {'=' * 16}")
    ok, msg = interact.manual_control("close_fresh_air", d2)
    print(f"教师手动操作关闭新风 → {msg}")
    op, confirmed, msg2 = interact.confirm()
    print(f"教师回复确认 → {msg2}")
    if confirmed:
        manual_action = {"window": 0, "fresh_air": 0, "mode": "手动关闭新风", "warn": True}
        fb, m = execute.run(manual_action)
        print(f"[执行层] {m}")
        audit.record(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            env_snapshot=d2,
            reasoning=f"教师手动操作({op})，经确认保护提示风险并二次确认后执行",
            command=manual_action,
            feedback=fb,
        )

    # ================= 审计层·五元组决策日志 =================
    print(f"\n{'=' * 16} 五元组决策日志（可追溯·可复盘） {'=' * 16}")
    print("时间戳 → 环境快照 → Agent推理依据 → 执行指令 → 设备反馈")
    audit.show_log()
    path = audit.export_log()
    print(f"日志已安全存储于运维云平台并导出备份：{path}")
    print("\n===== 三位一体闭环运行结束，全部决策可追溯复现 =====")
    