# agent_execute.py 任务执行能力（三位一体之执行层）
# 智能体通过运维云平台下发指令控制电动开窗器、可调档新风、空调目标温度；
# 出现设备离线、执行异常时自动向后勤管理人员告警


class ExecuteAgent:
    """接收决策指令，模拟下发硬件控制报文，返回设备反馈"""

    def __init__(self):
        self.simulate_offline = False

    def run(self, action):
        window_target = action["window"]
        fresh_air_target = action["fresh_air"]
        mode = action.get("mode", "")
        ac_target = action.get("ac_target_temp")
        exec_success = not self.simulate_offline
        hardware_feedback = {
            "window_real": window_target if exec_success else None,
            "fresh_air_real": fresh_air_target if exec_success else None,
            "ac_target_real": ac_target if exec_success else None,
            "exec_success": exec_success,
            "device_online": exec_success,
        }
        if exec_success:
            ac_part = f"，空调目标温度{ac_target}℃" if ac_target is not None else ""
            exec_msg = (f"下发指令成功：电动开窗器开窗{window_target}%，"
                        f"可调档新风档位{fresh_air_target}{ac_part}，模式[{mode}]")
        else:
            exec_msg = "⚠ 设备离线/执行异常，运维云平台已自动向后勤管理人员告警"
        return hardware_feedback, exec_msg