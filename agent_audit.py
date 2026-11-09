# agent_audit.py 五元组决策日志（三位一体之审计层）
# 五元组：时间戳 → 环境快照 → Agent推理依据 → 执行指令 → 设备反馈
# 完整留存每一次交互与决策记录，消除AI黑盒，全部操作可追溯复现
# 符合《教育人工智能伦理规范》"校园AI应用决策可追溯、行为可复盘"合规要求
# 日志安全存储于企业专属运维云平台，支持学校随时导出审计
import json


class AuditAgent:
    """后台自动保存五元组决策日志，支持追溯复盘与导出审计"""

    def __init__(self):
        self.log_list = []

    def record(self, timestamp, env_snapshot, reasoning, command, feedback):
        """记录一条五元组决策日志
        :param timestamp: 时间戳
        :param env_snapshot: 环境快照（多源感知数据）
        :param reasoning: Agent推理依据
        :param command: 执行指令
        :param feedback: 设备反馈
        """
        log_item = {
            "时间戳": timestamp,
            "环境快照": env_snapshot,
            "Agent推理依据": reasoning,
            "执行指令": command,
            "设备反馈": feedback,
        }
        self.log_list.append(log_item)
        return log_item

    def show_log(self):
        """打印全部五元组运行日志，供追溯复盘"""
        for i, item in enumerate(self.log_list, 1):
            print(f"---- 五元组决策日志 #{i} ----")
            print(f"[1]时间戳：{item['时间戳']}")
            print(f"[2]环境快照：{item['环境快照']}")
            print(f"[3]Agent推理依据：{item['Agent推理依据']}")
            print(f"[4]执行指令：{item['执行指令']}")
            print(f"[5]设备反馈：{item['设备反馈']}\n")

    def export_log(self, filepath="audit_log.json"):
        """导出审计日志至运维云平台存储，支持学校随时导出审计"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.log_list, f, ensure_ascii=False, indent=2)
        return filepath