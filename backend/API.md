# 📖 EpicDiary v4.0 API 接口规范

本文档用于规范前端 (React) 与后端 (FastAPI) 之间的数据契约。

**Base URL**: `http://localhost:8000/api`

---

## 1. 数据模型 (Data Models)

### `DiaryEntry` (日记条目)
| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `ts` | string | 时间戳 (格式: HH:MM:SS) |
| `weather` | string | 天气描述 (含图标) |
| `real` | string | 用户原始记录内容 |
| `drama` | string | AI 编织的史诗叙事 |
| `emoji` | string | AI 提取的心情 Emoji |
| `date_folder` | string | 日期文件夹 (格式: YYYY-MM-DD) |

---

## 2. 核心接口 (Endpoints)

### 📂 档案管理

#### 获取日期列表
- **GET** `/dates`
- **Response**: `string[]` (例如 `["2026-03-10", "2026-03-09"]`)

#### 获取指定日期的日记列表
- **GET** `/entries/{date_str}`
- **Response**: `DiaryEntry[]`

#### 删除条目
- **DELETE** `/entries/{date_folder}/{timestamp}`
- **Note**: `timestamp` 中的冒号需替换为连字符 (例如 `12-01-49`)。

### ✍️ 写入与转换

#### 纯净保存 (同步)
- **POST** `/save/pure`
- **Payload**: `{"text": string, "city": string}`
- **Response**: `{"status": "success", "ts": string}`

#### 魔法转换 (异步)
- **POST** `/save/magic`
- **Payload**: `{"text": string, "city": string}`
- **Response**: `{"status": "accepted", "task_id": string, "ts": string, "date": string}`
- **Logic**: 立即返回 `task_id`，并在后台启动 AI 编织任务。

### ⚙️ 任务与状态

#### 检查异步任务状态
- **GET** `/tasks/{task_id}`
- **Response**: `{"status": "weaving" | "done" | "failed: error_msg"}`

---

## 3. 异步任务状态机 (Task State Machine)

1. **`weaving`**: AI 正在联网获取天气并生成史诗内容。
2. **`done`**: 任务完成，内容已写入本地 `.md` 文件。前端收到此状态后应触发局部刷新。
3. **`failed`**: 任务因网络或 API 错误中断。

