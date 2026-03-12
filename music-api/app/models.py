from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from datetime import datetime
from app.database import Base


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    artist = Column(String(100), nullable=False)
    album = Column(String(100))
    cover_url = Column(String(500))
    audio_url = Column(String(500), nullable=False)
    duration = Column(Integer, default=0)  # seconds
    tags = Column(JSON, default=list)  # ["happy", "calm"]
    lyrics = Column(Text, nullable=True)  # LRC format
    created_at = Column(DateTime, default=datetime.utcnow)


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    songs = Column(JSON, default=list)  # [{"song_id": 1, "order": 0}]
    created_at = Column(DateTime, default=datetime.utcnow)
