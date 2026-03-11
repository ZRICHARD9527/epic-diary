# 📖 EpicDiary (史诗日记)

[English](#english) | [中文](#chinese)

> **"好的设计，是让技术消失，让情感浮现。"**

**EpicDiary** 已进化至 v4.0+ 时代。我们告别了 Streamlit 的局促，拥抱了 **FastAPI + React** 带来的极致优雅与丝滑响应。这不仅是一个记录工具，更是一部会呼吸的生命史诗。

---

<a name="chinese"></a>
## ✨ v4.0 核心进化 (Fast Edition)

### 🎨 视觉之魂：温润如玉
- **宣纸材质**: 详情卡片引入细腻的宣纸纹理，模拟纸张在书桌上的触感。
- **呼吸感布局**: 基于 **CORE_SPEC.md** 宪章，拒绝纯黑纯白，采用浅淡温暖的米色调。
- **静默内敛**: 移除所有跳跃的干扰，让每一处阴影和偏移都服务于沉浸式书写。

### 🧠 交互哲学：无感交互
- **极速响应**: 引入 **SQLite + FTS5** 索引层，实现历史记忆的秒级唤醒。
- **宿命交织 (Fate Lines)**: 自动挖掘记忆间的隐形线条，展示与当前心境共鸣的历史瞬间。
- **异步织梦**: 采用 FastAPI 后台任务，AI 编织过程不打断您的连续记录。

### 🛠️ 技术栈
- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: React + Vite + TypeScript (Lucide Icons)
- **Database**: SQLite (FTS5 全文搜索)
- **AI Engine**: Volcengine (火山引擎) 原生集成

---

## 🚀 快速开始

### 1. 克隆与配置
```bash
git clone https://github.com/ZRICHARD9527/epic-diary.git
cd epic-diary
```
将 `config.yaml.example` 重命名为 `config.yaml` 并填入您的 **Volcengine API Key**。

### 2. 启动后端 (Python)
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 3. 启动前端 (Node.js)
```bash
cd frontend
npm install
npm run dev
```

---

<a name="english"></a>
## 📖 English Introduction

**EpicDiary** has evolved into the v4.0+ era, transitioning from Streamlit to a high-performance **FastAPI + React** architecture. 

### Key Highlights:
- **Visual Essence**: "Warm as Jade" aesthetic with handmade paper textures.
- **Fate Lines**: Automatic discovery of connected memories using SQLite FTS5.
- **Silent Immersion**: Non-blocking AI weaving and minimalist UI.
- **Native AI**: Direct integration with Volcengine API for stability.

---

## 📜 CHANGELOG (更新日志)

### [v4.7.3] - 2026-03-11
- **重大架构迁移**：从 Streamlit 全面转向 FastAPI + React。
- **视觉重塑**：引入宣纸材质、暖金色呼吸光晕与玻璃拟态通知。
- **数据层升级**：启用 SQLite 混合索引，大幅提升“宿命交织”关联速度。
- **AI 提示词优化**：DRAMA 叙事回归纯粹情感，支持自动提炼 THEMES 标签。

### [v3.0.0] - 2026-03-10
- **架构大跳跃**：引入多 Agent 隔离系统 (`diary_weaver`, `project_critic`)，实现隐私保护与专业化分工。
- **自动化评审系统**：部署基于 OpenClaw Cron 的 **AI 首席创意官 (CCO)** 机制，每晚自动审计代码并更新 TODO。
- **心情复盘预研**：重构存储层支持 `mood_report.json`。

### [v2.6.1] - 2026-03-09
- **UI 极致打磨**：实现主界面整体上移，压缩顶部留白；侧边栏记录点文本实现左对齐与优雅截断。

### [v2.5.0] - 2026-03-09
- **配置持久化**：设置实时写回 `config.yaml`，偏好城市永久记住。
- **布局锁定**：通过 CSS 强制锁定按钮水平排布，彻底解决窗口缩放时的走位问题。

### [v2.4.0] - 2026-03-09
- **史诗感排版**：引入 Noto Serif SC 衬线体，增加引言边框装饰与卡片 Fade-In 动效。

### [v2.3.0] - 2026-03-09
- **存储结构重构**：由单文件模式升级为日期文件夹模式，提升数据隔离度。

### [v1.5.0] - 2026-03-08
- **交互升级**：支持 `Ctrl+Enter` 提交，新增侧边栏全文搜索与“纯净保存”功能。

### [v1.0.0] - 2026-03-08
- **起源**：项目立项，完成基础日记存储与 AI 转换。

---

## 📜 License
MIT License. Created by RICH.
