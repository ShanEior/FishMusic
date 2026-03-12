# Music Station - 音乐站项目规划

## 1. 项目概述

**项目名称**: Music Station (音乐站)
**项目类型**: 音乐播放 Web 应用
**核心功能**: 一个极简主义的音乐播放页面，支持歌词显示、心情标签筛选、歌单管理
**目标用户**: 喜欢沉浸式音乐体验的用户

## 2. 技术栈

### 后端
- **框架**: Python FastAPI
- **数据库**: SQLite (轻量级，适合演示)
- **音频处理**: 预留接口，可后续集成

### 前端
- **框架**: Vue 3 (Composition API + Script Setup)
- **UI 库**: Tailwind CSS + 自定义组件 (可选用 Naive UI)
- **动画库**: Vue Transition + @vueuse/motion
- **状态管理**: Pinia
- **路由**: Vue Router
- **样式增强**: Tailwind CSS + 自定义 CSS 变量

## 3. UI/UX 设计方向

### 整体视觉
- **风格**: 极简、沉浸式暗黑主题
- **背景**: 动态毛玻璃效果，基于封面主色调
- **字体**: 现代无衬线字体 (Inter, SF Pro)

### 布局
- **单页面**: 只有一个播放页面，无传统首屏
- **中央播放器**: 大面积歌词显示 + 底部控制栏
- **侧边栏**: 可展开的心情/标签选择面板
- **歌单抽屉**: 从侧边滑出的歌单管理

### 动效设计
- 毛玻璃背景: 使用 `backdrop-filter: blur()` + CSS 渐变动画
- 歌词动效: 逐字高亮卡拉 OK 效果 + 淡入淡出 (Vue Transition + CSS)
- 页面过渡: Vue Router 过渡动画
- 播放指示: 均衡器动画 + 专辑封面旋转

## 4. 核心功能

### 4.1 播放页面
- 大尺寸专辑封面 (居中或侧边)
- 歌词显示区域 (可滚动，支持自动滚动)
- 播放控制: 上一首/播放暂停/下一首
- 进度条: 可拖拽，支持显示时间
- 音量控制

### 4.2 心情/标签系统
- 预设心情标签: 欢快、平静、忧郁、浪漫、能量等
- 标签颜色主题
- 点击标签筛选对应歌曲
- 标签存储在歌曲 metadata 中

### 4.3 歌单功能
- 创建歌单 (自定义名称)
- 向歌单添加/移除歌曲
- 歌单内歌曲可以重复
- 歌单播放模式: 顺序/随机/循环
- 当前播放队列显示

### 4.4 歌词显示
- 逐字高亮效果
- 自动滚动跟随
- 毛玻璃背景板
- 字体发光效果
- 无歌词时显示占位

## 5. 数据模型

### 歌曲 (Song)
```
- id: int
- title: str
- artist: str
- album: str
- cover_url: str
- audio_url: str
- duration: int (秒)
- tags: list[str] (心情标签)
- lyrics: str (LRC 格式)
- created_at: datetime
```

### 歌单 (Playlist)
```
- id: int
- name: str
- songs: list[SongItem] (song_id + 出现次数)
- created_at: datetime
```

## 6. API 设计

### 歌曲接口
- `GET /api/songs` - 获取所有歌曲 (支持 tag 筛选)
- `GET /api/songs/{id}` - 获取歌曲详情
- `GET /api/songs/tags` - 获取所有可用标签

### 歌单接口
- `GET /api/playlists` - 获取所有歌单
- `POST /api/playlists` - 创建歌单
- `GET /api/playlists/{id}` - 获取歌单详情
- `PUT /api/playlists/{id}` - 更新歌单
- `DELETE /api/playlists/{id}` - 删除歌单

## 7. 前端项目结构

```
music-web/              # 前端项目
├── public/             # 静态资源
├── src/
│   ├── assets/         # 样式、图片
│   ├── components/
│   │   ├── player/
│   │   │   ├── Player.vue           # 播放器主组件
│   │   │   ├── PlayerControls.vue   # 播放控制
│   │   │   ├── ProgressBar.vue      # 进度条
│   │   │   ├── VolumeControl.vue    # 音量控制
│   │   │   └── AlbumArt.vue         # 专辑封面
│   │   ├── lyrics/
│   │   │   ├── LyricsDisplay.vue    # 歌词显示
│   │   │   └── LyricsLine.vue       # 单行歌词
│   │   ├── sidebar/
│   │   │   ├── TagSelector.vue      # 标签选择
│   │   │   └── PlaylistDrawer.vue   # 歌单抽屉
│   │   └── common/                  # 通用组件
│   ├── composables/    # 组合式函数
│   ├── stores/          # Pinia 状态管理
│   ├── router/          # Vue Router
│   ├── services/        # API 调用
│   ├── utils/           # 工具函数
│   ├── App.vue
│   └── main.ts
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

## 8. 视觉特效方案

### 毛玻璃效果
- 使用 CSS `backdrop-filter: blur(20px)`
- 背景渐变动画模拟专辑封面颜色
- 多层叠加创造深度感

### 歌词动画
- Vue Transition + CSS 实现逐字动画
- 当前行高亮 + 放大效果
- 上下滚动平滑过渡

### 配色方案
- 主色: 从封面提取 (使用 color.js 或 similar)
- 辅助色: 渐变色阶
- 文字: 白色/半透明白色

## 9. 实施步骤

1. **后端搭建** (Day 1)
   - FastAPI 项目初始化
   - 数据库模型定义
   - 基础 CRUD API
   - 种子数据

2. **前端基础** (Day 2)
   - Vue 3 + Vite 项目初始化
   - Tailwind CSS 配置
   - 布局框架搭建

3. **播放器核心** (Day 3)
   - 音频播放逻辑
   - 播放控制组件
   - 进度条/音量

4. **歌词系统** (Day 4)
   - 歌词解析 (LRC)
   - 歌词显示组件
   - 自动滚动

5. **标签与歌单** (Day 5)
   - 标签筛选逻辑
   - 歌单 CRUD
   - 歌单播放队列

6. **视觉美化** (Day 6)
   - 毛玻璃效果
   - 动画优化
   - 响应式调整

## 10. 注意事项

- 音频文件使用占位 URL，后续可替换真实资源
- 歌词使用 LRC 格式存储
- 考虑移动端适配
- 性能优化: 图片懒加载、歌词虚拟滚动
