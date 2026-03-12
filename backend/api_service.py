import logging
import random
import re
import json
import requests
from config_loader import load_config

# 全局 Session 对象，实现连接池复用 (Keep-Alive)
_SESSION = requests.Session()

def generate_full_package(text, city="南京", max_retries=2):
    """
    通过全局 Session 连接池极速调用 AI API
    """
    config = load_config()
    api_settings = config.get('ai_settings', {})
    
    api_key = api_settings.get('api_key')
    base_url = api_settings.get('base_url')
    model_id = api_settings.get('model_id')
    timeout = api_settings.get('timeout_seconds', 60)

    if not api_key or not base_url or not model_id:
        logging.error("AI settings (api_key, base_url, or model_id) are missing in config.yaml")
        return "🌫️ 配置缺失", "请检查 config.yaml 中的 AI 配置", "⚠️", "配置, 错误, 系统"

    prompt = f"""
    请按照要求完成日记的史诗感转换。
    
    【日记】："{text}"
    【城市】：{city} (注：仅供天气意象参考，不需要在史诗叙事中提及地名)

    请遵循以下要求：
    1. DRAMA 部分必须聚焦于【日记】中的情感、动作或思想。
    2. 追求极致的文学感，风格应如历史长卷般厚重或如诗歌般轻盈。
    3. 字数控制在 50-100 字之间。

    请严格按以下格式输出：
    WEATHER: <查询{city}的天气，并将其意象化表达（四个字和一个天气emoji）>
    DRAMA: <基于日记内容的史诗感转换>
    THEMES: <3个基于情感的主题标签>
    EMOJI: <3个符合日记内容的Emoji>
    """

    for attempt in range(max_retries + 1):
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model_id,
                "messages": [{"role": "user", "content": prompt.strip()}],
                "temperature": 0.7
            }
            
            logging.info(f"Optimized Session API call (Attempt {attempt+1})...")
            
            # 使用全局 _SESSION 发送请求
            resp = _SESSION.post(f"{base_url}/chat/completions", headers=headers, json=data, timeout=timeout)
            resp.raise_for_status()
            
            res_json = resp.json()
            content = res_json['choices'][0]['message']['content']
            
            return _parse_weaver_content(content, text)
            
        except Exception as e:
            logging.error(f"API Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries:
                import time
                time.sleep(2 ** attempt)
                continue
            
            fallback_messages = [
                "星辰暂时隐没，但记忆已在时光中定格",
                "史诗的墨迹正在天际重聚，请稍候片刻",
                "这段情感已如古卷般封存，待星光重现时再续"
            ]
            return "🌫️ 云端暂隐", random.choice(fallback_messages), "📜", "碎片, 时光, 宿命"

def _parse_weaver_content(content, original_text):
    """
    解析 AI 返回的结构化内容
    """
    weather_match = re.search(r'WEATHER:\s*(.*)', content, re.IGNORECASE)
    drama_match = re.search(r'DRAMA:\s*(.*)', content, re.IGNORECASE | re.DOTALL)
    themes_match = re.search(r'THEMES:\s*(.*)', content, re.IGNORECASE)
    emoji_match = re.search(r'EMOJI:\s*(.*)', content, re.IGNORECASE)
    
    weather = weather_match.group(1).strip() if weather_match else "🌫️ 意象收敛中"
    drama = drama_match.group(1).strip() if drama_match else "[编织中断]"
    
    if "THEMES:" in drama: drama = drama.split("THEMES:")[0].strip()
    if "EMOJI:" in drama: drama = drama.split("EMOJI:")[0].strip()

    themes = themes_match.group(1).strip() if themes_match else "碎片, 时光, 宿命"
    raw_emoji = emoji_match.group(1).strip() if emoji_match else "📝"
    
    emoji_list = [c for c in raw_emoji if ord(c) > 127][:3]
    final_emoji = "".join(emoji_list) if emoji_list else "📝📜✨"
    
    logging.info(f"Successfully wove epic for: {original_text[:20]}...")
    return weather, drama, final_emoji, themes

def get_ai_client():
    """保持接口兼容性"""
    config = load_config()
    api_key = config['ai_settings'].get('api_key', '')
    base_url = config['ai_settings'].get('base_url', '')
    return api_key, base_url
