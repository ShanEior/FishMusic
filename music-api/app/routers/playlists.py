from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Playlist, Song
from app.schemas import (
    PlaylistResponse,
    PlaylistCreate,
    PlaylistUpdate,
    PlaylistWithSongs,
    SongResponse
)

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.get("", response_model=List[PlaylistResponse])
def get_playlists(db: Session = Depends(get_db)):
    return db.query(Playlist).all()


@router.get("/{playlist_id}", response_model=PlaylistWithSongs)
def get_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Playlist not found")

    # 获取歌单中每首歌曲的详情
    song_details = []
    if playlist.songs:
        for item in playlist.songs:
            song = db.query(Song).filter(Song.id == item["song_id"]).first()
            if song:
                song_details.append(song)

    return {
        "id": playlist.id,
        "name": playlist.name,
        "songs": playlist.songs,
        "created_at": playlist.created_at,
        "song_details": song_details
    }


@router.post("", response_model=PlaylistResponse)
def create_playlist(playlist: PlaylistCreate, db: Session = Depends(get_db)):
    db_playlist = Playlist(
        name=playlist.name,
        songs=[s.model_dump() for s in playlist.songs]
    )
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist


@router.put("/{playlist_id}", response_model=PlaylistResponse)
def update_playlist(
    playlist_id: int,
    playlist: PlaylistUpdate,
    db: Session = Depends(get_db)
):
    db_playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not db_playlist:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Playlist not found")

    if playlist.name is not None:
        db_playlist.name = playlist.name
    if playlist.songs is not None:
        db_playlist.songs = [s.model_dump() if hasattr(s, 'model_dump') else s for s in playlist.songs]

    db.commit()
    db.refresh(db_playlist)
    return db_playlist


@router.delete("/{playlist_id}")
def delete_playlist(playlist_id: int, db: Session = Depends(get_db)):
    db_playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not db_playlist:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Playlist not found")

    db.delete(db_playlist)
    db.commit()
    return {"message": "Playlist deleted"}
