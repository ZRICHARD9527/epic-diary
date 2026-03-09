# 📖 EpicDiary (史诗日记)

[English](#english) | [中文](#chinese)

---

<a name="chinese"></a>
## 中文介绍

**EpicDiary** 是一个基于 AI 的创意日记应用。它能将您日常平淡的记录，通过 **AI** 瞬间转化为一段充满戏剧冲突、波澜壮阔的“史诗”文学，并自动同步当日天气。

### ✨ 核心功能
- **史诗编织**：将琐碎生活升华为史诗文学。
- **Emoji 密语**：AI 自动提炼心情符号。
- **自动天气**：同步记录时刻的真实天气。
- **极速保存**：支持“纯净保存”模式，秒记原话。
- **档案管理**：支持日期回溯、全文搜索、编辑与删除。

### 🚀 快速开始
1. **安装 OpenClaw** 并配置 AI 接口。
2. 克隆仓库：`git clone https://github.com/ZRICHARD9527/epic-diary.git`
3. 安装依赖：`pip install streamlit PyYAML requests`
4. 配置文件：将 `config.yaml.example` 重命名为 `config.yaml` 并填入您的 `openclaw.cmd` 路径。
5. 启动：`python -m streamlit run src/web_diary.py`

---

<a name="english"></a>
## English Introduction

**EpicDiary** is an AI-powered creative diary application. It uses **AI** to transform your mundane daily logs into dramatic, magnificent "epic" narratives while automatically syncing the local weather.

### ✨ Key Features
- **Epic Weaving**: Elevates daily life into grand epic literature.
- **Emoji Cipher**: AI-generated mood summaries using emojis.
- **Auto Weather**: Syncs real-time weather at the moment of recording.
- **Pure Save**: Quick-save mode for original text without AI transformation.
- **Archive Management**: Date tracing, full-text search, editing, and deletion.

### 🚀 Quick Start
1. **Install OpenClaw** and configure AI API.
2. Clone repo: `git clone https://github.com/ZRICHARD9527/epic-diary.git`
3. Install dependencies: `pip install streamlit PyYAML requests`
4. Config: Rename `config.yaml.example` to `config.yaml` and set your `openclaw.cmd` path.
5. Launch: `python -m streamlit run src/web_diary.py`

---

## 📜 CHANGELOG (更新日志)

### [v2.2.0] - 2026-03-08
- **工程化重构**：引入配置管理，实现代码分层。
- **性能优化**：合并 AI 任务，响应速度提升 2 倍。
- **功能增强**：支持手动设置城市，新增全文搜索。

---

## 📜 License
MIT License. Created by RICH.
