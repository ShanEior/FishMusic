# Music Station 音乐站

一个极简主义的音乐播放 Web 应用，支持歌词显示、心情标签筛选、歌单管理。

## 特性

- 🎵 沉浸式暗黑主题播放器
- 📝 歌词显示（支持逐字高亮卡拉 OK 效果）
- 🏷️ 心情标签筛选歌曲
- 📋 歌单管理与播放队列
- 🖼️ 毛玻璃视觉效果

## 技术栈

### 前端
- Vue 3 (Composition API + Script Setup)
- Vite
- Tailwind CSS
- Pinia 状态管理
- Vue Router

### 后端
- FastAPI
- SQLite
- SQLAlchemy

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/music-station.git
cd music-station
```

### 2. 启动后端

```bash
cd music-api

# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload
```

后端运行在 http://localhost:8000

### 3. 启动前端

```bash
cd music-web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 http://localhost:5173

## 项目结构

```
music-station/
├── music-api/          # FastAPI 后端
│   ├── app/
│   │   ├── main.py    # 主应用
│   │   ├── models.py  # 数据模型
│   │   ├── schemas.py # Pydantic 模型
│   │   └── routers/   # API 路由
│   ├── seed.py        # 种子数据
│   └── requirements.txt
│
└── music-web/          # Vue 3 前端
    ├── src/
    │   ├── components/ # 组件
    │   ├── stores/    # Pinia 状态
    │   ├── services/  # API 服务
    │   └── assets/    # 静态资源
    ├── package.json
    └── vite.config.ts
```

## API 文档

启动后端后访问 http://localhost:8000/docs 查看 API 文档。

### 主要接口

- `GET /api/songs` - 获取歌曲列表（支持标签筛选）
- `GET /api/songs/{id}` - 获取歌曲详情
- `GET /api/songs/tags` - 获取所有标签
- `GET /api/playlists` - 获取歌单列表
- `POST /api/playlists` - 创建歌单

##  License

MIT
