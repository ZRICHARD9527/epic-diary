import os
import subprocess
import datetime
import re
import config_loader

# 项目根目录 (动态获取)
BASE_DIR = config_loader.BASE_DIR
SRC_DIR = os.path.join(BASE_DIR, "src")
TODO_FILE = os.path.join(BASE_DIR, "TODO.md")
OPENCLAW_PATH = config_loader.OPENCLAW_PATH
TEMP_PROMPT = os.path.join(BASE_DIR, "temp_ai_prompt.txt")

def get_project_context():
    context = "### EpicDiary 项目当前上下文 ###\n\n"
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            context += "--- TODO.md ---\n" + f.read() + "\n\n"
    for file in ["web_diary.py", "storage.py", "api_service.py"]:
        path = os.path.join(SRC_DIR, file)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                context += f"--- {file} (Partial) ---\n" + "".join(f.readlines()[:100]) + "\n\n"
    return context

def update_todo(new_insight):
    if not os.path.exists(TODO_FILE): return
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    header = "## 🔮 AI 首席创意官实时洞察 (Latest AI Insights)"
    insight_block = f"{header}\n> *更新于: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n{new_insight}\n\n"
    if header in content:
        new_content = re.sub(rf"{re.escape(header)}.*?(?=\n##|\Z)", insight_block, content, flags=re.DOTALL)
    else:
        new_content = content + "\n\n" + insight_block
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

def run_ai_review():
    print(f"[{datetime.datetime.now()}] 🚀 启动 AI 深度评审...")
    context = get_project_context()
    prompt = f"你现在是 EpicDiary 的首席创意官 (CCO)。请基于以下现状，给出 3 条简洁、硬核的优化建议：1. UI/UX 微调；2. 架构/存储优化；3. 史诗感功能。请输出纯 Markdown。\n\n{context}"
    
    with open(TEMP_PROMPT, "w", encoding="utf-8") as f:
        f.write(prompt)
    
    try:
        # 使用配置中的 OPENCLAW_PATH
        result = subprocess.run(
            f'"{OPENCLAW_PATH}" agent --message "$(Get-Content \'{TEMP_PROMPT}\' -Raw)" --agent project_critic',
            shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        report = result.stdout
        if "Hey!" in report: report = report.split("Hey!", 1)[1].strip()
        
        if len(report) < 10:
            print(f"⚠️ 报告内容异常短，可能调用失败: {report}")
            return

        report_dir = os.path.join(BASE_DIR, "docs", "ai_reviews")
        if not os.path.exists(report_dir): os.makedirs(report_dir)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        report_file = os.path.join(report_dir, f"{today}.md")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"# EpicDiary AI 评审报告 ({today})\n\n{report}")
        
        update_todo(report)
        print(f"✅ 成功！报告: {report_file}，TODO 已更新。")
        if os.path.exists(TEMP_PROMPT): os.remove(TEMP_PROMPT)
        
    except Exception as e:
        print(f"❌ 失败: {str(e)}")

if __name__ == "__main__":
    run_ai_review()
