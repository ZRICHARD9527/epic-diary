import subprocess
import re
from config_loader import OPENCLAW_PATH, AI_SETTINGS

def call_openclaw(prompt, timeout=None):
    """底层 OpenClaw 调用逻辑"""
    if timeout is None:
        timeout = AI_SETTINGS.get("timeout_seconds", 60)
        
    try:
        clean_prompt = prompt.replace("\n", " ").strip()
        result = subprocess.run(
            [OPENCLAW_PATH, "agent", "--message", clean_prompt, "--agent", AI_SETTINGS.get("agent_name", "main")],
            capture_output=True, text=True, encoding='utf-8', errors='ignore', 
            timeout=timeout, check=True
        )
        raw_output = result.stdout
        
        if "Hey!" in raw_output:
            return raw_output.split("Hey!", 1)[1].strip()
        parts = re.split(r'[\u25cf\u25cb\u25cc\u25cd\u25ce]', raw_output)
        if len(parts) > 1:
            return parts[-1].strip()
        return raw_output.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

def generate_full_package(user_text, city):
    """【极速合并版】一次调用完成三个任务"""
    prompt = f"""
    任务：
    1. 联网查询“{city}”今日的天气。
    2. 将日记“{user_text}”改写成200字以内、充满戏剧冲突的史诗感文字。
    3. 生成3-5个 Emoji 总结心情。
    
    回复格式必须严格如下（包含括号）：
    W:[图标 气温 状况]
    D:[史诗内容]
    E:[Emoji内容]
    """
    res = call_openclaw(prompt)
    
    # 解析逻辑
    try:
        weather = re.search(r'W:\[(.*?)\]', res).group(1)
        drama = re.search(r'D:\[(.*?)\]', res, re.DOTALL).group(1)
        emoji = re.search(r'E:\[(.*?)\]', res).group(1)
        return weather, drama, emoji
    except:
        return "🌫️ 天气未知", res if len(res) > 10 else "[编织失败]", "📝"
