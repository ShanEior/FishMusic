from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
import os
import uuid
from pathlib import Path

from app.database import get_db
from app.models import Song
from app.schemas import SongResponse

router = APIRouter(prefix="/songs", tags=["songs"])

# 上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload", response_model=SongResponse)
async def upload_song(
    title: str = Form(...),
    artist: str = Form(...),
    album: Optional[str] = Form(None),
    tags: str = Form("[]"),  # JSON string
    lyrics: Optional[str] = Form(None),
    audio: UploadFile = File(...),
    cover: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """上传歌曲"""
    import json

    # 保存音频文件
    audio_ext = os.path.splitext(audio.filename)[1] if audio.filename else ".mp3"
    audio_filename = f"{uuid.uuid4()}{audio_ext}"
    audio_path = UPLOAD_DIR / audio_filename

    with open(audio_path, "wb") as f:
        content = await audio.read()
        f.write(content)

    audio_url = f"/uploads/{audio_filename}"

    # 保存封面图片
    cover_url = None
    if cover:
        cover_ext = os.path.splitext(cover.filename)[1] if cover.filename else ".jpg"
        cover_filename = f"{uuid.uuid4()}{cover_ext}"
        cover_path = UPLOAD_DIR / cover_filename

        with open(cover_path, "wb") as f:
            content = await cover.read()
            f.write(content)

        cover_url = f"/uploads/{cover_filename}"

    # 解析标签
    try:
        tags_list = json.loads(tags) if tags else []
    except:
        tags_list = []

    # 创建歌曲记录
    song = Song(
        title=title,
        artist=artist,
        album=album,
        cover_url=cover_url,
        audio_url=audio_url,
        duration=0,  # 可以后续计算
        tags=tags_list,
        lyrics=lyrics
    )

    db.add(song)
    db.commit()
    db.refresh(song)

    return song
