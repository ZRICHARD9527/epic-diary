from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
import datetime
import uuid

# 确保能加载迁移过来的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import storage
import api_service
import utils
import config_loader

import time
from collections import defaultdict

import json
import logging

# --- File-based Rate Limiter with Poetic Persistence ---
class RateLimiter:
    def __init__(self, requests_limit: int, window_seconds: int, storage_path: str = None):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        # Ensure path is absolute and robust
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.storage_path = storage_path or os.path.join(base_dir, "..", "diary", "rate_limits.json")
        self.records = defaultdict(list)
        self._load_from_disk()

    def _load_from_disk(self):
        """Load rate limit records from disk for persistence across restarts"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    now = time.time()
                    # Only load records within window
                    for client_id, timestamps in data.items():
                        valid_timestamps = [t for t in timestamps if now - t < self.window_seconds]
                        if valid_timestamps:
                            self.records[client_id] = valid_timestamps
        except Exception as e:
            logging.warning(f"Failed to load rate limits from disk: {e}")

    def _save_to_disk(self):
        """Save rate limit records to disk"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(dict(self.records), f)
        except Exception as e:
            logging.warning(f"Failed to save rate limits to disk: {e}")

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        # Clean old records
        self.records[client_id] = [t for t in self.records[client_id] if now - t < self.window_seconds]
        if len(self.records[client_id]) < self.requests_limit:
            self.records[client_id].append(now)
            self._save_to_disk()
            return True
        return False

# Limit to 5 magic requests per minute per IP-ish (simulated)
magic_limiter = RateLimiter(requests_limit=5, window_seconds=60)

app = FastAPI(title="EpicDiary API", version="4.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DiaryEntry(BaseModel):
    ts: str
    weather: str
    real: str
    drama: str
    emoji: str
    date_folder: Optional[str] = None

class SaveRequest(BaseModel):
    text: str
    city: Optional[str] = None

task_store = {}

import logging

# --- 后台任务：AI 深度织梦 (包含天气补全) ---
def process_magic_weaving(task_id: str, raw_text: str, date_folder: str, timestamp: str, city: str):
    try:
        task_store[task_id] = "weaving"
        # 调用 AI 核心：generate_full_package (天气, 史诗, Emoji, 主题)
        weather, drama, emoji, themes = api_service.generate_full_package(raw_text, city)
        
        # 将 AI 编织的所有内容回写
        success = storage.update_entry(date_folder, timestamp, {
            "weather": weather,
            "drama": drama, 
            "emoji": emoji,
            "tags": themes
        })
        if success:
            task_store[task_id] = "done"
        else:
            task_store[task_id] = "failed: 记忆载体保存失败"
    except Exception as e:
        import logging
        logging.exception(f"Magic weaving failed for task {task_id}")
        task_store[task_id] = "failed: 史诗编织过程中星辰偏航"

@app.get("/api/dates")
def get_dates():
    return storage.get_all_diary_files()

@app.get("/api/entries/{date_str}", response_model=List[DiaryEntry])
def get_entries(date_str: str):
    entries = storage.parse_entries(date_str)
    for e in entries:
        e['date_folder'] = date_str
    return entries

@app.post("/api/save/pure")
def save_pure(req: SaveRequest):
    city = req.city or "南京"
    weather = utils.get_weather(city)
    ts = storage.save_entry(req.text, drama="[纯净记录]", weather=weather)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    return {
        "status": "success", 
        "ts": ts, 
        "date": today,
        "message": "记忆已尘封"
    }

@app.post("/api/save/magic")
def save_magic(req: SaveRequest, background_tasks: BackgroundTasks, request: Request):
    client_id = request.client.host
    if not magic_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=429, 
            detail="✨ 星辰之门暂时拥挤，请稍候片刻，让灵感沉淀后再续写诗篇。"
        )
    
    city = req.city or "南京"
    # 魔法转换初始保存：使用占位符
    ts = storage.save_entry(req.text, drama="✨ 正在跨越次元编织史诗...", emoji="⏳", weather="🌪️ 正在同步天气...")
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    task_id = str(uuid.uuid4())
    # 将任务交给后台
    background_tasks.add_task(process_magic_weaving, task_id, req.text, today, ts, city)
    
    return {
        "status": "accepted", 
        "task_id": task_id, 
        "ts": ts, 
        "date": today,
        "message": "史诗编织中..."
    }

@app.get("/api/tasks/{task_id}")
def check_task(task_id: str):
    status = task_store.get(task_id, "not_found")
    return {"status": status}

@app.get("/api/entries/{date_folder}/{timestamp}/related")
def get_related(date_folder: str, timestamp: str):
    return storage.get_related_entries(date_folder, timestamp)

@app.get("/api/admin/reindex")
def reindex_all():
    """Manual trigger to re-sync SQLite with Markdown files"""
    try:
        all_dates = storage.get_all_diary_files()
        db = database.get_database()
        count = 0
        for d in all_dates:
            entries = storage.parse_entries(d)
            for e in entries:
                db.index_entry(d, e['ts'], e['weather'], e['real'], e['drama'], e['emoji'])
                count += 1
        return {"status": "success", "indexed": count}
    except Exception as e:
        logging.error(f"Reindex failed: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/search")
def search_entries(query: str, limit: int = 20):
    """Full-text search across all entries with unified results"""
    try:
        db = database.get_database()
        results = db.search_entries(query, limit)
        # Results are already dicts with all fields
        return {"status": "success", "results": results}
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return {"status": "error", "results": []}

@app.delete("/api/entries/{date_folder}/{timestamp}")
def delete_entry(date_folder: str, timestamp: str):
    storage.delete_entry(date_folder, timestamp)
    return {"status": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
