import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Song {
  id: number
  title: string
  artist: string
  album?: string
  cover_url?: string
  audio_url: string
  duration: number
  tags: string[]
  lyrics?: string
  created_at: string
}

export interface Playlist {
  id: number
  name: string
  songs: { song_id: number; order: number }[]
  created_at: string
  song_details?: Song[]
}

export const usePlayerStore = defineStore('player', () => {
  // 状态
  const songs = ref<Song[]>([])
  const playlists = ref<Playlist[]>([])
  const tags = ref<string[]>([])
  const currentTag = ref<string | null>(null)
  const currentSong = ref<Song | null>(null)
  const queue = ref<Song[]>([])
  const queueIndex = ref(0)
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const duration = ref(0)
  const volume = ref(0.8)
  const isMuted = ref(false)
  const currentPlaylist = ref<Playlist | null>(null)
  const playMode = ref<'顺序' | '随机' | '循环'>('顺序')

  const audio = new Audio()

  // 计算属性
  const currentLyrics = computed(() => {
    if (!currentSong.value?.lyrics) return []
    return parseLyrics(currentSong.value.lyrics)
  })

  const filteredSongs = computed(() => {
    if (!currentTag.value) return songs.value
    return songs.value.filter(s => s.tags?.includes(currentTag.value!))
  })

  // 方法
  function parseLyrics(lrc: string) {
    const lines: { time: number; text: string }[] = []
    const regex = /\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)/g
    let match
    while ((match = regex.exec(lrc)) !== null) {
      const min = parseInt(match[1])
      const sec = parseInt(match[2])
      const ms = parseInt(match[3].padEnd(3, '0'))
      const time = min * 60 + sec + ms / 1000
      lines.push({ time, text: match[4] })
    }
    return lines.sort((a, b) => a.time - b.time)
  }

  function setSongs(list: Song[]) {
    songs.value = list
    if (list.length > 0 && !currentSong.value) {
      playSong(list[0])
    }
  }

  function setTags(list: string[]) {
    tags.value = list
  }

  function setPlaylists(list: Playlist[]) {
    playlists.value = list
  }

  function selectTag(tag: string | null) {
    currentTag.value = tag
  }

  const API_BASE = 'http://localhost:8000'

  function playSong(song: Song) {
    currentSong.value = song
    // 拼接完整URL
    const fullUrl = song.audio_url.startsWith('http')
      ? song.audio_url
      : `${API_BASE}${song.audio_url}`
    console.log('Playing:', fullUrl)
    audio.src = fullUrl
    audio.play().then(() => {
      isPlaying.value = true
    }).catch((err) => {
      console.error('播放失败:', err)
      isPlaying.value = false
    })
  }

  function togglePlay() {
    if (!currentSong.value) return
    if (isPlaying.value) {
      audio.pause()
    } else {
      audio.play()
    }
    isPlaying.value = !isPlaying.value
  }

  function next() {
    // 单曲循环模式：重复播放当前歌曲
    if (playMode.value === '循环') {
      if (currentSong.value) {
        playSong(currentSong.value)
      }
      return
    }

    // 随机播放模式
    if (playMode.value === '随机') {
      const list = queue.value.length > 0 ? queue.value : filteredSongs.value
      if (list.length <= 1) return
      let randomIdx = Math.floor(Math.random() * list.length)
      // 确保随机播放的不是同一首
      while (list.length > 1 && list[randomIdx].id === currentSong.value?.id) {
        randomIdx = Math.floor(Math.random() * list.length)
      }
      if (queue.value.length > 0) {
        queueIndex.value = randomIdx
      }
      playSong(list[randomIdx])
      return
    }

    // 顺序播放模式
    if (queue.value.length === 0) {
      // 使用过滤后的歌曲
      const list = filteredSongs.value
      const idx = list.findIndex(s => s.id === currentSong.value?.id)
      const nextIdx = (idx + 1) % list.length
      playSong(list[nextIdx])
    } else {
      // 使用播放队列
      if (queueIndex.value < queue.value.length - 1) {
        queueIndex.value++
        playSong(queue.value[queueIndex.value])
      }
    }
  }

  function prev() {
    // 随机播放和单曲循环模式下，上一首也是随机
    if (playMode.value === '随机' || playMode.value === '循环') {
      const list = queue.value.length > 0 ? queue.value : filteredSongs.value
      if (list.length <= 1) return
      let randomIdx = Math.floor(Math.random() * list.length)
      while (list.length > 1 && list[randomIdx].id === currentSong.value?.id) {
        randomIdx = Math.floor(Math.random() * list.length)
      }
      if (queue.value.length > 0) {
        queueIndex.value = randomIdx
      }
      playSong(list[randomIdx])
      return
    }

    // 顺序播放
    const list = queue.value.length > 0 ? queue.value : filteredSongs.value
    const idx = list.findIndex(s => s.id === currentSong.value?.id)
    const prevIdx = idx === 0 ? list.length - 1 : idx - 1
    if (queue.value.length > 0) {
      queueIndex.value = prevIdx
    }
    playSong(list[prevIdx])
  }

  function seek(time: number) {
    audio.currentTime = time
    currentTime.value = time
  }

  function setVolume(val: number) {
    volume.value = val
    audio.volume = val
    isMuted.value = val === 0
  }

  function toggleMute() {
    if (isMuted.value) {
      audio.volume = volume.value || 0.8
      isMuted.value = false
    } else {
      audio.volume = 0
      isMuted.value = true
    }
  }

  function playPlaylist(playlist: Playlist) {
    if (playlist.song_details && playlist.song_details.length > 0) {
      queue.value = playlist.song_details
      currentPlaylist.value = playlist
      queueIndex.value = 0
      playSong(playlist.song_details[0])
    }
  }

  // 音频事件
  audio.ontimeupdate = () => {
    currentTime.value = audio.currentTime
  }

  audio.onloadedmetadata = () => {
    duration.value = audio.duration
  }

  audio.onended = () => {
    next()
  }

  return {
    songs, tags, currentTag, currentSong, queue, queueIndex,
    isPlaying, currentTime, duration, volume, isMuted,
    currentPlaylist, playMode, currentLyrics, filteredSongs,
    setSongs, setTags, setPlaylists, selectTag, playSong,
    togglePlay, next, prev, seek, setVolume, toggleMute, playPlaylist
  }
})
