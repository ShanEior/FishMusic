"""
种子数据脚本 - 运行此脚本添加示例歌曲
"""
from app.database import SessionLocal, engine, Base
from app.models import Song, Playlist

# 创建表
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 检查是否已有数据
if db.query(Song).first():
    print("数据已存在，跳过种子数据")
    db.close()
    exit()

# 示例歌曲数据 (使用免费在线音频资源)
songs_data = [
    {
        "title": "Summer Breeze",
        "artist": "Relaxing Vibes",
        "album": "Chill Summer",
        "cover_url": "https://picsum.photos/seed/song1/400/400",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "duration": 280,
        "tags": ["欢快", "夏天", "放松"],
        "lyrics": """[00:00.00]Summer Breeze
[00:05.00]Relaxing Vibes
[00:10.00]
[00:15.00]Sunshine on my face
[00:20.00]Feeling so warm
[00:25.00]The breeze is blowing
[00:30.00]Taking all my worries away
[00:40.00]
[00:45.00]Summer days are here
[00:50.00]Everything is bright
[00:55.00]Let the music play
[01:00.00]Dance in the light
[01:10.00]
[01:20.00]Oh summer breeze
[01:25.00]Soft and sweet
[01:30.00]Carry me away
[01:35.00]To where I'll meet
[01:40.00]Dreams and possibilities
[01:50.00]
[02:00.00]Feel the warmth
[02:05.00]Feel the glow
[02:10.00]Let it show
[02:15.00]Everything will be alright"""
    },
    {
        "title": "",
        "artist": "Night Owl",
        "album": "Quiet Hours",
        "cover_url": "https://picsum.photos/seed/song2/400/400",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        "duration": 320,
        "tags": ["平静", "夜晚", "忧郁"],
        "lyrics": """[00:00.00]Midnight Dreams
[00:05.00]Night Owl
[00:10.00]
[00:15.00]Stars are shining bright
[00:20.00]In the velvet sky
[00:25.00]Moon is glowing soft
[00:30.00]As the night goes by
[00:40.00]
[00:45.00]Midnight dreams
[00:50.00]Take me away
[00:55.00]To a place where
[01:00.00]Stars and I can play
[01:10.00]
[01:20.00]Floating in the dark
[01:25.00]Thinking of tomorrow
[01:30.00]What will life bring
[01:35.00]Joy or sorrow
[01:45.00]
[01:50.00]But tonight I dream
[01:55.00]Of something beautiful
[02:00.00]Something pure
[02:05.00]Something wonderful"""
    },
    {
        "title": "Energy Boost",
        "artist": "Power Beats",
        "album": "Workout Mix",
        "cover_url": "https://picsum.photos/seed/song3/400/400",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
        "duration": 240,
        "tags": ["能量", "运动", "欢快"],
        "lyrics": """[00:00.00]Energy Boost
[00:05.00]Power Beats
[00:10.00]
[00:12.00]Get up and move
[00:15.00]Don't stop now
[00:18.00]Feel the rhythm
[00:21.00]Show us how
[00:24.00]
[00:27.00]Running fast
[00:30.00]Heart beats quick
[00:33.00]Adrenaline
[00:36.00]Doing its trick
[00:42.00]
[00:45.00]Energy boost
[00:48.00]Feel the power
[00:51.00]Every cell
[00:54.00]Every hour
[01:00.00]
[01:03.00]Push it hard
[01:06.00]Never give
[01:09.00]Live your life
[01:12.00]To the full live
[01:18.00]
[01:21.00]We are the champions
[01:24.00]We will prevail
[01:27.00]Never stopping
[01:30.00]We will never fail"""
    },
    {
        "title": "Romantic Evening",
        "artist": "Love Songs",
        "album": "Sweet Moments",
        "cover_url": "https://picsum.photos/seed/song4/400/400",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
        "duration": 300,
        "tags": ["浪漫", "平静", "夜晚"],
        "lyrics": """[00:00.00]Romantic Evening
[00:05.00]Love Songs
[00:10.00]
[00:15.00]Candlelight dinner
[00:20.00]Soft music plays
[00:25.00]Two hearts beating
[00:30.00]In a gentle haze
[00:40.00]
[00:45.00]Hold me close
[00:50.00]Dance with me
[00:55.00]Under the stars
[01:00.00]So beautifully
[01:10.00]
[01:15.00]This moment is ours
[01:20.00]Forever and ever
[01:25.00]Love will last
[01:30.00]True and forever
[01:40.00]
[01:45.00]Whisper sweet words
[01:50.00]In my ear
[01:55.00]Let me know
[02:00.00]That you're near
[02:05.00]
[02:10.00]Together forever
[02:15.00]That's what we are
[02:20.00]My shining star"""
    },
    {
        "title": "Morning Coffee",
        "artist": "Acoustic Soul",
        "album": "Daily Rituals",
        "cover_url": "https://picsum.photos/seed/song5/400/400",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
        "duration": 260,
        "tags": ["平静", "早晨", "放松"],
        "lyrics": """[00:00.00]Morning Coffee
[00:05.00]Acoustic Soul
[00:10.00]
[00:15.00]Wake up slowly
[00:20.00]The sun is rising
[00:25.00]Fresh new day
[00:30.00]Surprises are arising
[00:40.00]
[00:45.00]Coffee brewing
[00:50.00]Aroma fills the air
[00:55.00]Morning peace
[01:00.00]Everything is fair
[01:10.00]
[01:15.00]Take a deep breath
[01:20.00]Feel the warmth
[01:25.00]Of this brand new day
[01:30.00]Embrace the calm
[01:40.00]
[01:45.00]Time moves slowly
[01:50.00]No need to rush
[01:55.00]Enjoy the moment
[02:00.00]Let the worries hush
[02:10.00]
[02:15.00]This is my time
[02:20.00]My peaceful place
[02:25.00]Morning coffee
[02:30.00]Such sweet grace"""
    },
    {
        "title": "Ocean Waves",
        "artist": "Nature Sounds",
        "album": "Calm Sea",
        "cover_url": "https://picsum.photos/seed/song6/400/400",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
        "duration": 350,
        "tags": ["平静", "自然", "放松"],
        "lyrics": """[00:00.00]Ocean Waves
[00:05.00]Nature Sounds
[00:10.00]
[00:20.00]Waves crashing softly
[00:30.00]On the sandy shore
[00:40.00]Nature's music
[00:50.00]Playing more and more
[01:00.00]
[01:10.00]Feel the salt air
[01:20.00]Blowing through your hair
[01:30.00]Let your worries
[01:40.00]Float away somewhere
[01:50.00]
[02:00.00]Ocean blue
[02:10.00]So vast and wide
[02:20.00]Peace inside
[02:30.00]Nature's tide
[02:40.00]
[02:50.00]Breathe in deep
[03:00.00]The salty air
[03:10.00]Feel so free
[03:20.00]Nothing to compare"""
    }
]

# 添加歌曲
for song_data in songs_data:
    song = Song(**song_data)
    db.add(song)

# 添加一个示例歌单
playlist = Playlist(
    name="我的收藏",
    songs=[
        {"song_id": 1, "order": 0},
        {"song_id": 2, "order": 1},
        {"song_id": 3, "order": 2},
    ]
)
db.add(playlist)

db.commit()
print(f"已添加 {len(songs_data)} 首歌曲和 1 个示例歌单")
db.close()
