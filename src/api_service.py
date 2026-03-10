import subprocess
import re
import json
from config_loader import OPENCLAW_PATH, AI_SETTINGS

def call_openclaw(prompt, timeout=None, agent_name=None):
    """底层 OpenClaw 调用逻辑"""
    if timeout is None:
        timeout = AI_SETTINGS.get("timeout_seconds", 60)
    
    # 使用传入的 agent_name，否则从配置读取默认值
    if agent_name is None:
        agent_name = AI_SETTINGS.get("diary_agent", "main")
        
    try:
        clean_prompt = prompt.replace("\n", " ").strip()
        result = subprocess.run(
            [OPENCLAW_PATH, "agent", "--message", clean_prompt, "--agent", agent_name],
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
    """【极速合并版】单条日记处理"""
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
    try:
        weather = re.search(r'W:\[(.*?)\]', res).group(1)
        drama = re.search(r'D:\[(.*?)\]', res, re.DOTALL).group(1)
        emoji = re.search(r'E:\[(.*?)\]', res).group(1)
        return weather, drama, emoji
    except:
        return "🌫️ 天气未知", res if len(res) > 10 else "[编织失败]", "📝"

def analyze_daily_mood(entries):
    """【新功能】全天心情聚合分析"""
    if not entries: return None
    
    # 构造聚合文本
    combined_text = ""
    for e in entries[::-1]: # 按时间顺序
        combined_text += f"[{e['ts']}] {e['real']}\n"
    
    prompt = f"""
    你是一名专业的情感分析师。请分析以下这一天的日记序列：
    {combined_text}
    
    任务：
    1. 为每一条日记给出一个 0-100 的心情分（0最差，100最好）。
    2. 总结今日的平均心情指数。
    3. 提取3个今日心情关键词。
    4. 撰写一段150字以内的“今日史诗复盘总结”。
    
    回复格式必须严格为 JSON（不要包含任何其他文字）：
    {{
      "scores": [分值列表，数量需与日记条数一致],
      "average": 平均分,
      "keywords": ["词1", "词2", "词3"],
      "summary": "复盘总结文字"
    }}
    """
    res = call_openclaw(prompt)
    
    # 清理可能存在的 Markdown 代码块标记
    clean_res = re.sub(r'```json|```', '', res).strip()
    try:
        return json.loads(clean_res)
    except:
        return {
            "scores": [50] * len(entries),
            "average": 50,
            "keywords": ["未知", "平淡", "神秘"],
            "summary": "AI 正在编织心情丝线，暂时无法给出完整总结。"
        }
