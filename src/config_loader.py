import yaml
import os

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

def load_config():
    """加载并解析 YAML 配置文件"""
    if not os.path.exists(CONFIG_PATH):
        # 如果文件不存在，返回默认值
        return {
            "paths": {"diary_dir": "diary", "openclaw_cmd": "openclaw.cmd"},
            "ai_settings": {"default_city": "北京", "timeout_seconds": 60, "agent_name": "main"},
            "ui_settings": {"page_title": "EpicDiary", "page_icon": "📖", "button_border_radius": "4px"}
        }
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# 实例化全局配置对象
config = load_config()

# 提供便捷的全局变量
PATHS = config.get("paths", {})
AI_SETTINGS = config.get("ai_settings", {})
UI_SETTINGS = config.get("ui_settings", {})

# 处理绝对路径
DIARY_DIR = os.path.join(BASE_DIR, PATHS.get("diary_dir", "diary"))
OPENCLAW_PATH = PATHS.get("openclaw_cmd")
