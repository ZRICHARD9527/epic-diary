import logging
import random
import re
import json
import os
import requests
from config_loader import load_config

def generate_full_package(text, city="南京", max_retries=2):
    """
    直接调用 Volcengine (火山引擎) 原生 API 进行史诗编织
    """
    config = load_config()
    api_settings = config.get('ai_settings', {})
    
    api_key = api_settings.get('api_key')
    base_url = api_settings.get('base_url', 'https://ark.cn-beijing.volces.com/api/v3')
    model_id = api_settings.get('model_id', 'ep-20260212220341-2hlrx')
    timeout = api_settings.get('timeout_seconds', 60)

    prompt = f"""
    请为这段记忆赋予史诗感。
    
    【当下记录】："{text}"
    【 atmospheric context 】：{city} (仅作氛围参考)

    请遵循以下要求：
    1. DRAMA 部分应完全基于记录中的情感波动、思考或瞬间进行“史诗级转换”。
    2. 追求纯粹的文学感和超越时间的叙事风格。
    3. 风格温暖，字句精炼，大约 50-100 字。

    请严格按以下格式输出：
    WEATHER: <意象化天气，如：微雨洇墨 🌦️>
    DRAMA: <史诗级转换内容>
    THEMES: <3个情感或主题标签，用逗号分隔>
    EMOJI: <3个相关Emoji意象>
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
            
            logging.info(f"Direct Volcengine API call (Attempt {attempt+1})...")
            resp = requests.post(f"{base_url}/chat/completions", headers=headers, json=data, timeout=timeout)
            resp.raise_for_status()
            
            res_json = resp.json()
            content = res_json['choices'][0]['message']['content']
            
            return _parse_weaver_content(content, text)
            
        except Exception as e:
            logging.error(f"Volcengine API Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries:
                import time
                time.sleep(2 ** attempt)  # 指数退避
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
    # 改进的正则解析
    weather_match = re.search(r'WEATHER:\s*(.*)', content, re.IGNORECASE)
    drama_match = re.search(r'DRAMA:\s*(.*)', content, re.IGNORECASE | re.DOTALL)
    themes_match = re.search(r'THEMES:\s*(.*)', content, re.IGNORECASE)
    emoji_match = re.search(r'EMOJI:\s*(.*)', content, re.IGNORECASE)
    
    weather = weather_match.group(1).strip() if weather_match else "🌫️ 意象收敛中"
    drama = drama_match.group(1).strip() if drama_match else "[编织中断]"
    
    # 截断处理：防止 AI 把后面的字段也塞进 DRAMA 里
    if "THEMES:" in drama: drama = drama.split("THEMES:")[0].strip()
    if "EMOJI:" in drama: drama = drama.split("EMOJI:")[0].strip()

    themes = themes_match.group(1).strip() if themes_match else "碎片, 时光, 宿命"
    raw_emoji = emoji_match.group(1).strip() if emoji_match else "📝"
    
    # 提取 Emoji (过滤非 Emoji 字符)
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
