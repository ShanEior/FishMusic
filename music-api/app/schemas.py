from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SongBase(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None
    cover_url: Optional[str] = None
    audio_url: str
    duration: float = 0
    tags: List[str] = []
    lyrics: Optional[str] = None


class SongCreate(SongBase):
    pass


class SongUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    cover_url: Optional[str] = None
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    tags: Optional[List[str]] = None
    lyrics: Optional[str] = None


class SongResponse(SongBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PlaylistBase(BaseModel):
    name: str


class PlaylistSongItem(BaseModel):
    song_id: int
    order: int = 0


class PlaylistCreate(PlaylistBase):
    songs: List[PlaylistSongItem] = []


class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    songs: Optional[List[PlaylistSongItem]] = None


class PlaylistResponse(PlaylistBase):
    id: int
    songs: List[PlaylistSongItem]
    created_at: datetime

    class Config:
        from_attributes = True


class PlaylistWithSongs(PlaylistResponse):
    song_details: List[SongResponse] = []
