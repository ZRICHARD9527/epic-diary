import requests

def get_current_city():
    """通过 IP 自动识别当前城市"""
    try:
        r = requests.get('http://ip-api.com/json/?lang=zh-CN', timeout=3).json()
        return r.get('city', '所在城市')
    except:
        return "本地"

def clean_text(text):
    """通用文本清洗，去除首尾空格和不必要的换行"""
    return text.strip() if text else ""
