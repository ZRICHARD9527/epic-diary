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

### 🛠️ 环境要求
- **Python 3.10+**
- **依赖库**: `streamlit`, `PyYAML`, `requests`
- **[OpenClaw](https://github.com/OpenClaw/OpenClaw)** (用于对接 AI API)

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

### 🛠️ Requirements
- **Python 3.10+**
- **Libraries**: `streamlit`, `PyYAML`, `requests`
- **[OpenClaw](https://github.com/OpenClaw/OpenClaw)** (for connecting AI API)

### 🚀 Quick Start
1. **Install OpenClaw** and configure AI API.
2. Clone repo: `git clone https://github.com/ZRICHARD9527/epic-diary.git`
3. Install dependencies: `pip install streamlit PyYAML requests`
4. Config: Rename `config.yaml.example` to `config.yaml` and set your `openclaw.cmd` path.
5. Launch: `python -m streamlit run src/web_diary.py`

---

## 📜 CHANGELOG (更新日志)

### [v2.6.1] - 2026-03-09
- **UI 极致打磨**：实现主界面整体上移，压缩顶部留白。
- **侧边栏优化**：记录点文本实现左对齐与优雅的省略号截断。
- **布局回归**：设置按钮回归侧边栏顶部，采用更稳健的 Popover 布局。

### [v2.5.0] - 2026-03-09
- **配置持久化**：实现设置实时写回 `config.yaml`，偏好城市永久记住。
- **布局锁定**：通过 CSS 强制锁定按钮水平排布，彻底解决窗口缩放时的走位问题。

### [v2.4.0] - 2026-03-09
- **史诗感排版**：引入 Noto Serif SC 衬线体，增加引言边框装饰。
- **交互升级**：增加内容卡片 Fade-In Up 动效，按钮内嵌至卡片边缘。

### [v2.3.0] - 2026-03-09
- **存储结构重构**：由单文件模式升级为日期文件夹模式，提升数据隔离度与安全性。

### [v2.2.0] - 2026-03-08
- **工程化重构**：引入配置管理，实现代码分层。
- **性能优化**：合并 AI 任务，响应速度提升 2 倍。
- **功能增强**：支持手动设置城市，新增全文搜索。

### [v1.6.0] - 2026-03-08
- **代码重构**：代码移至 `src` 目录，新增“纯净保存”功能。

### [v1.5.0] - 2026-03-08
- **交互升级**：支持 `Ctrl+Enter` 提交，新增侧边栏全文搜索。

### [v1.2.0] - 2026-03-08
- **网页化**：正式上线 Streamlit 驱动的 Web 界面。
- **修复**：解决了 Windows 编码乱码问题和路径错误。

### [v1.0.0] - 2026-03-08
- **起源**：项目立项，完成基础日记存储与 AI 转换。

---

## 📜 License
MIT License. Created by RICH.
