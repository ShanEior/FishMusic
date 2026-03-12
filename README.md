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

### 一键启动（推荐）

项目提供了一键部署脚本，会自动检测并安装所需环境：

**Windows**: 双击 `deploy.bat`

**Linux/Mac**:
```bash
chmod +x deploy.sh
./deploy.sh
```

脚本会自动：
1. 检测/安装 Python（如未安装）
2. 检测/安装 Node.js（如未安装）
3. 创建 Python 虚拟环境
4. 安装后端依赖
5. 安装前端依赖
6. 初始化数据库
7. 启动后端和前端服务

启动完成后访问：
- 前端：http://localhost:5173
- 后端：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 手动启动

如果已具备 Python 和 Node.js 环境，也可以手动启动：

```bash
# 克隆项目
git clone https://github.com/你的用户名/music-station.git
cd music-station

# === 启动后端 ===
cd music-api

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload
```

```bash
# === 启动前端 ===
cd music-web

# 安装依赖
npm install  # 或 pnpm install

# 启动开发服务器
npm run dev
```

## 项目结构

```
music-station/
├── deploy.bat           # Windows 一键部署脚本
├── deploy.sh            # Linux/Mac 一键部署脚本
├── README.md            # 项目说明
├── CLAUDE.md            # 项目规划文档
│
├── music-api/           # FastAPI 后端
│   ├── app/
│   │   ├── main.py     # 主应用
│   │   ├── models.py   # 数据模型
│   │   ├── schemas.py  # Pydantic 模型
│   │   └── routers/    # API 路由
│   ├── seed.py         # 种子数据
│   └── requirements.txt
│
└── music-web/           # Vue 3 前端
    ├── src/
    │   ├── components/  # 组件
    │   ├── stores/      # Pinia 状态
    │   ├── services/    # API 服务
    │   └── assets/      # 静态资源
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

## License

MIT
