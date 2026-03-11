import requests
import logging

def get_current_city():
    """通过 IP 自动识别当前城市"""
    try:
        r = requests.get('http://ip-api.com/json/?lang=zh-CN', timeout=3).json()
        return r.get('city', '所在城市')
    except Exception as e:
        logging.warning(f"Failed to detect city: {e}")
        return "本地"

def get_weather(city):
    """获取指定城市的天气 (wttr.in API)"""
    try:
        url = f"https://wttr.in/{city}?format=%c+%t"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.text.strip()
    except Exception as e:
        logging.error(f"Weather API error for {city}: {e}")
    
    return "🌫️ 天气未知"

def clean_text(text):
    """通用文本清洗"""
    return text.strip() if text else ""
