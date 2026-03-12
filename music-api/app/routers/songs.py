from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Song
from app.schemas import SongResponse, SongCreate, SongUpdate

router = APIRouter(prefix="/songs", tags=["songs"])


@router.get("", response_model=List[SongResponse])
def get_songs(
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Song)
    if tag:
        query = query.filter(Song.tags.contains(tag))
    return query.all()


@router.get("/tags")
def get_tags(db: Session = Depends(get_db)):
    """获取所有可用的标签"""
    songs = db.query(Song).all()
    all_tags = set()
    for song in songs:
        if song.tags:
            all_tags.update(song.tags)
    return sorted(list(all_tags))


@router.get("/{song_id}", response_model=SongResponse)
def get_song(song_id: int, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Song not found")
    return song


@router.post("", response_model=SongResponse)
def create_song(song: SongCreate, db: Session = Depends(get_db)):
    db_song = Song(**song.model_dump())
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


@router.put("/{song_id}", response_model=SongResponse)
def update_song(song_id: int, song_data: SongUpdate, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    update_data = song_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(song, key, value)

    db.commit()
    db.refresh(song)
    return song


@router.delete("/{song_id}")
def delete_song(song_id: int, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    db.delete(song)
    db.commit()
    return {"message": "Song deleted successfully"}
