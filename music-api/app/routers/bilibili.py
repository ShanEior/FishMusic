from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
import re
import uuid
import json
from pathlib import Path
from pydantic import BaseModel

from app.database import get_db
from app.models import Song
from app.schemas import SongResponse

router = APIRouter(prefix="/bilibili", tags=["bilibili"])

# 上传目录
UPLOAD_DIR = Path("C:/Users/18636/Desktop/test-demo/music-api/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 临时下载目录
TEMP_DIR = Path("C:/Users/18636/Desktop/test-demo/music-api/temp")
TEMP_DIR.mkdir(exist_ok=True)


class BiliBiliParseResponse(BaseModel):
    """B站视频解析响应"""
    bvid: str
    title: str
    author: str
    cover_url: Optional[str] = None
    duration: Optional[float] = None
    description: Optional[str] = None


def extract_bvid(url: str) -> Optional[str]:
    """从URL中提取BV号"""
    # 支持多种URL格式
    # https://www.bilibili.com/video/BV1xx411c7mD
    # https://b23.tv/xxxxxx (短链)
    # BV1xx411c7mD

    # 匹配BV号
    bv_pattern = r'BV[a-zA-Z0-9]{10}'
    match = re.search(bv_pattern, url)
    if match:
        return match.group()

    # 匹配短链接 b23.tv/xxxxx
    short_pattern = r'b23\.tv/([a-zA-Z0-9]+)'
    match = re.search(short_pattern, url)
    if match:
        # 需要解析短链接（这里返回None让调用方处理）
        return match.group(1)

    # 如果直接是BV号
    if url.startswith('BV'):
        return url

    return None


@router.post("/parse", response_model=BiliBiliParseResponse)
async def parse_bilibili_video(url: str = Form(...)):
    """解析B站视频URL，获取视频信息"""
    import yt_dlp

    bvid = extract_bvid(url)
    if not bvid:
        raise ValueError("无法识别B站视频URL")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 如果是短链接，先获取真实URL
            if 'b23.tv' in url:
                # 提取信息时会自动解析
                pass

            info = ydl.extract_info(url, download=False)

            return BiliBiliParseResponse(
                bvid=info.get('id', bvid),
                title=info.get('title', ''),
                author=info.get('uploader', ''),
                cover_url=info.get('thumbnail') or info.get('thumbnails', [{}])[0].get('url') if info.get('thumbnails') else None,
                duration=info.get('duration'),
                description=info.get('description', '')
            )
    except Exception as e:
        raise ValueError(f"解析失败: {str(e)}")


@router.post("/download", response_model=SongResponse)
async def download_bilibili_video(
    url: str = Form(...),
    title: str = Form(...),
    artist: str = Form(...),
    album: Optional[str] = Form(None),
    tags: str = Form("[]"),
    lyrics: Optional[str] = Form(None),
    cover_url_from_parse: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """下载B站视频并提取音频，上传到服务器"""
    import yt_dlp
    from urllib.parse import urljoin
    import requests

    bvid = extract_bvid(url)
    if not bvid:
        raise ValueError("无法识别B站视频URL")

    # 生成唯一文件名
    unique_id = str(uuid.uuid4())

    # 先检查ffmpeg是否可用
    import shutil
    has_ffmpeg = shutil.which('ffmpeg') is not None

    # 进度回调函数
    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = int(downloaded * 100 / total)
                print(f"[进度] {percent}%")
        elif d['status'] == 'finished':
            print(f"[进度] 100%")

    if has_ffmpeg:
        # 下载选项 - 提取音频
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(TEMP_DIR / f'{unique_id}_%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'writethumbnail': True,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
        }
    else:
        # 无ffmpeg时，直接下载最佳音视频（m4a格式）
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(TEMP_DIR / f'{unique_id}_%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 先获取视频信息
            info = ydl.extract_info(url, download=True)

            # 查找下载的文件
            video_title = info.get('title', 'unknown')

            # 查找音频文件
            audio_files = list(TEMP_DIR.glob(f'{unique_id}_*.*'))
            if not audio_files:
                raise ValueError("视频下载失败")

            audio_path = audio_files[0]
            ext = audio_path.suffix

            # 移动到上传目录
            audio_filename = f"{uuid.uuid4()}{ext}"
            final_audio_path = UPLOAD_DIR / audio_filename
            audio_path.rename(final_audio_path)

            audio_url = f"/uploads/{audio_filename}"

            # 处理封面 - 优先从参数获取，否则从下载的文件中找
            cover_url = None
            cover_files = list(TEMP_DIR.glob(f'{unique_id}_*.webp')) + list(TEMP_DIR.glob(f'{unique_id}_*.jpg'))
            if cover_files:
                cover_path = cover_files[0]
                # 转换为jpg
                from PIL import Image
                img = Image.open(cover_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                cover_filename = f"{uuid.uuid4()}.jpg"
                cover_final_path = UPLOAD_DIR / cover_filename
                img.save(cover_final_path, 'JPEG')
                cover_url = f"/uploads/{cover_filename}"
                # 清理临时封面
                cover_path.unlink(missing_ok=True)
            elif cover_url_from_parse:
                # 从解析API获取的封面URL下载图片，添加伪装Headers
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Referer': 'https://www.bilibili.com/',
                        'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    }
                    response = requests.get(cover_url_from_parse, headers=headers, timeout=10)
                    if response.status_code == 200:
                        cover_filename = f"{uuid.uuid4()}.jpg"
                        cover_path = UPLOAD_DIR / cover_filename
                        with open(cover_path, 'wb') as f:
                            f.write(response.content)
                        cover_url = f"/uploads/{cover_filename}"
                except Exception as e:
                    print(f"封面下载失败: {e}")

            # 解析标签
            try:
                tags_list = json.loads(tags) if tags else []
            except:
                tags_list = []

            # 获取视频时长
            duration = int(info.get('duration', 0) or 0)

            # 创建歌曲记录
            song = Song(
                title=title,
                artist=artist,
                album=album or info.get('album', ''),
                cover_url=cover_url,
                audio_url=audio_url,
                duration=duration,
                tags=tags_list,
                lyrics=lyrics
            )

            db.add(song)
            db.commit()
            db.refresh(song)

            return song

    except Exception as e:
        # 清理临时文件
        for f in TEMP_DIR.glob(f'{unique_id}_*'):
            f.unlink(missing_ok=True)
        raise ValueError(f"下载失败: {str(e)}")
