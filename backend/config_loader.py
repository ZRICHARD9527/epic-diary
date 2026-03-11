import yaml
import os

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

def validate_config(config):
    """验证配置完整性，提供默认值"""
    defaults = {
        'ai_settings': {
            'api_key': '',
            'base_url': 'http://localhost:8000',
            'model_id': 'gpt-3.5-turbo',
            'timeout_seconds': 60,
            'default_city': '北京',
            'agent_name': 'main'
        },
        'paths': {
            'diary_dir': 'diary',
            'openclaw_cmd': 'openclaw.cmd'
        },
        'ui_settings': {
            'primary_color': '#4CAF50',
            'secondary_color': '#f8f9fa',
            'page_title': 'EpicDiary',
            'page_icon': '📖',
            'button_border_radius': '4px'
        }
    }
    
    # 递归合并默认值
    def merge_defaults(target, defaults):
        for key, value in defaults.items():
            if key not in target:
                target[key] = value
            elif isinstance(value, dict) and isinstance(target[key], dict):
                merge_defaults(target[key], value)
    
    merge_defaults(config, defaults)
    return config

def load_config():
    """加载并解析 YAML 配置文件"""
    if not os.path.exists(CONFIG_PATH):
        config = {
            "paths": {"diary_dir": "diary", "openclaw_cmd": "openclaw.cmd"},
            "ai_settings": {"default_city": "北京", "timeout_seconds": 60, "agent_name": "main"},
            "ui_settings": {"page_title": "EpicDiary", "page_icon": "📖", "button_border_radius": "4px"}
        }
        return validate_config(config)
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        return validate_config(config)

def save_config(new_config):
    """将配置写回文件"""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(new_config, f, allow_unicode=True)

def update_setting(category, key, value):
    """更新特定设置并保存"""
    current_config = load_config()
    if category in current_config:
        current_config[category][key] = value
        save_config(current_config)

# 实例化全局配置对象
config = load_config()

# 提供便捷的全局变量
PATHS = config.get("paths", {})
AI_SETTINGS = config.get("ai_settings", {})
UI_SETTINGS = config.get("ui_settings", {})

# 处理绝对路径
DIARY_DIR = os.path.join(BASE_DIR, PATHS.get("diary_dir", "diary"))
OPENCLAW_PATH = PATHS.get("openclaw_cmd")
