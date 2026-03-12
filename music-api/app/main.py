from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from app.database import engine, Base
from app.routers import songs, playlists
from app.routers.upload import router as upload_router
from app.routers.bilibili import router as bilibili_router
import os

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Music Station API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务 - 自定义路由
UPLOADS_DIR = Path("C:/Users/18636/Desktop/test-demo/music-api/uploads")

@app.get("/uploads/{filename}")
async def get_file(filename: str):
    import os
    print(f"Current dir: {os.getcwd()}")
    print(f"Looking for: {UPLOADS_DIR / filename}")
    file_path = UPLOADS_DIR / filename
    if file_path.exists():
        return FileResponse(file_path, media_type="audio/mpeg")
    return {"detail": "File not found"}

# 注册路由
app.include_router(songs.router)
app.include_router(playlists.router)
app.include_router(upload_router)
app.include_router(bilibili_router)


@app.get("/")
def root():
    return {"message": "Music Station API", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
