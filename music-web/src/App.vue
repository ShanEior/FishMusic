<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePlayerStore, type Song, type Playlist } from './stores/player'
import { getSongs, getTags, getPlaylists, getPlaylist, createPlaylist, updatePlaylist, deletePlaylist, uploadSong, updateSong, deleteSong, parseBilibiliVideo, downloadBilibiliVideo } from './services/api'

const player = usePlayerStore()

const showPlaylist = ref(false)
const showAllSongs = ref(false)
const showQueue = ref(false)
const showUploadModal = ref(false)
const showEditModal = ref(false)
const showDeleteConfirm = ref(false)
const editingSong = ref<Song | null>(null)
const deletingSong = ref<Song | null>(null)
const editForm = ref({
  title: '',
  artist: '',
  album: '',
  tags: [] as string[],
})
const uploading = ref(false)
const tagInput = ref('')
const uploadForm = ref({
  title: '',
  artist: '',
  album: '',
  tags: [] as string[],
  lyrics: '',
})
let audioFile: File | null = null
let coverFile: File | null = null

// B站解析相关状态
const bilibiliUrl = ref('')
const bilibiliMode = ref(false)
const parsingBiliBili = ref(false)
const parsedBiliBiliInfo = ref<{
  bvid: string
  title: string
  author: string
  cover_url?: string
  duration?: number
} | null>(null)
const downloadingBiliBili = ref(false)
const downloadProgress = ref(0)

const addTag = () => {
  const tag = tagInput.value.trim()
  if (tag && !uploadForm.value.tags.includes(tag)) {
    uploadForm.value.tags.push(tag)
  }
  tagInput.value = ''
}

const removeTag = (index: number) => {
  uploadForm.value.tags.splice(index, 1)
}

// 解析B站视频
const parseBiliBiliVideo = async () => {
  if (!bilibiliUrl.value.trim()) {
    alert('请输入B站视频URL')
    return
  }
  parsingBiliBili.value = true
  try {
    const res = await parseBilibiliVideo(bilibiliUrl.value)
    parsedBiliBiliInfo.value = res.data
    // 自动填充表单
    uploadForm.value.title = res.data.title
    uploadForm.value.artist = res.data.author
  } catch (e: any) {
    console.error('解析失败:', e)
    const msg = e.response?.data?.detail || e.message || '解析失败，请检查URL是否正确'
    alert(typeof msg === 'object' ? JSON.stringify(msg) : msg)
  } finally {
    parsingBiliBili.value = false
  }
}

// 下载B站视频
const downloadBiliBiliVideo = async () => {
  if (!parsedBiliBiliInfo.value || !bilibiliUrl.value) {
    alert('请先解析视频')
    return
  }
  downloadingBiliBili.value = true
  downloadProgress.value = 0

  // 模拟进度条
  const progressInterval = setInterval(() => {
    if (downloadProgress.value < 90) {
      downloadProgress.value += Math.random() * 15
    }
  }, 500)

  try {
    const res = await downloadBilibiliVideo({
      url: bilibiliUrl.value,
      title: uploadForm.value.title,
      artist: uploadForm.value.artist,
      album: uploadForm.value.album || undefined,
      tags: uploadForm.value.tags,
      lyrics: uploadForm.value.lyrics || undefined,
      cover_url: parsedBiliBiliInfo.value?.cover_url
    })
    downloadProgress.value = 100
    alert('下载并上传成功！')
    showUploadModal.value = false
    // 重置表单
    bilibiliUrl.value = ''
    parsedBiliBiliInfo.value = null
    uploadForm.value = { title: '', artist: '', album: '', tags: [], lyrics: '' }
    // 刷新歌曲列表
    const songsRes = await getSongs()
    player.songs = songsRes.data
  } catch (e: any) {
    console.error('下载失败:', e)
    alert(e.response?.data?.detail || '下载失败，请重试')
  } finally {
    clearInterval(progressInterval)
    downloadingBiliBili.value = false
    downloadProgress.value = 0
  }
}

// 切换到本地上传模式
const switchToLocalUpload = () => {
  bilibiliMode.value = false
  bilibiliUrl.value = ''
  parsedBiliBiliInfo.value = null
}

// 切换到B站模式
const switchToBiliBiliUpload = () => {
  bilibiliMode.value = true
  audioFile = null
  coverFile = null
}

const handleAudioFile = (e: Event) => {
  const target = e.target as HTMLInputElement
  audioFile = target.files?.[0] || null
}

const handleCoverFile = (e: Event) => {
  const target = e.target as HTMLInputElement
  coverFile = target.files?.[0] || null
}

const handleUpload = async () => {
  if (!uploadForm.value.title || !uploadForm.value.artist || !audioFile) {
    alert('请填写标题、艺术家并选择音频文件')
    return
  }
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('title', uploadForm.value.title)
    formData.append('artist', uploadForm.value.artist)
    if (uploadForm.value.album) formData.append('album', uploadForm.value.album)
    formData.append('tags', JSON.stringify(uploadForm.value.tags))
    if (uploadForm.value.lyrics) formData.append('lyrics', uploadForm.value.lyrics)
    formData.append('audio', audioFile!)
    if (coverFile) formData.append('cover', coverFile)

    await uploadSong(formData)
    alert('上传成功！')
    showUploadModal.value = false
    // 重置表单
    uploadForm.value = { title: '', artist: '', album: '', tags: [], lyrics: '' }
    audioFile = null
    coverFile = null
    // 刷新歌曲列表
    const res = await getSongs()
    player.songs = res.data
  } catch (e) {
    console.error('上传失败:', e)
    alert('上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

const openEditModal = (song: Song) => {
  editingSong.value = song
  editForm.value = {
    title: song.title,
    artist: song.artist,
    album: song.album || '',
    tags: [...song.tags],
  }
  showEditModal.value = true
}

const handleEdit = async () => {
  if (!editingSong.value) return
  try {
    await updateSong(editingSong.value.id, editForm.value)
    showEditModal.value = false
    // 刷新列表
    const res = await getSongs()
    player.songs = res.data
    // 如果正在播放这首歌，更新当前歌曲信息
    if (player.currentSong?.id === editingSong.value.id) {
      player.currentSong = { ...player.currentSong, ...editForm.value }
    }
  } catch (e) {
    console.error('更新失败:', e)
    alert('更新失败，请重试')
  }
}

const confirmDelete = (song: Song) => {
  deletingSong.value = song
  showDeleteConfirm.value = true
}

const handleDelete = async () => {
  if (!deletingSong.value) return
  try {
    await deleteSong(deletingSong.value.id)
    showDeleteConfirm.value = false
    // 如果删除的是当前播放的歌曲，停止播放
    if (player.currentSong?.id === deletingSong.value.id) {
      player.currentSong = null
      player.isPlaying = false
    }
    // 刷新列表
    const res = await getSongs()
    player.songs = res.data
  } catch (e) {
    console.error('删除失败:', e)
    alert('删除失败，请重试')
  }
}

const showCreateModal = ref(false)
const showAddSongModal = ref(false)
const editingPlaylist = ref<Playlist | null>(null)
const newPlaylistName = ref('')
const loading = ref(true)

// 加载数据
onMounted(async () => {
  try {
    const [songsRes, tagsRes, playlistsRes] = await Promise.all([
      getSongs(),
      getTags(),
      getPlaylists()
    ])
    player.setSongs(songsRes.data)
    player.setTags(tagsRes.data)

    const playlists = playlistsRes.data
    for (const p of playlists) {
      const detail = await getPlaylist(p.id)
      p.song_details = detail.data.song_details
    }
    player.playlists = playlists
  } catch (e) {
    console.error('加载数据失败:', e)
  } finally {
    loading.value = false
  }
})

const formatTime = (s: number) => {
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

const playModeText = computed(() => {
  const mode = player.playMode
  if (mode === '顺序') return '顺序播放'
  if (mode === '随机') return '随机播放'
  return '单曲循环'
})

const togglePlayMode = () => {
  const modes: ('顺序' | '随机' | '循环')[] = ['顺序', '随机', '循环']
  const currentIndex = modes.indexOf(player.playMode)
  const nextIndex = (currentIndex + 1) % modes.length
  player.playMode = modes[nextIndex]
}

const getFullUrl = (url: string | undefined) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `http://localhost:8000${url}`
}

const playQueueSong = (song: Song, index: number) => {
  player.queue = player.filteredSongs
  player.queueIndex = index
  player.playSong(song)
}

const selectTag = (tag: string | null) => {
  player.selectTag(tag)
}

// 音量拖拽
const volumeSlider = ref<HTMLElement | null>(null)
const isDragging = ref(false)

const startDrag = (e: MouseEvent) => {
  isDragging.value = true
  updateVolume(e)
  document.addEventListener('mousemove', updateVolume)
  document.addEventListener('mouseup', stopDrag)
}

const updateVolume = (e: MouseEvent) => {
  if (!volumeSlider.value) return
  const rect = volumeSlider.value.getBoundingClientRect()
  const y = e.clientY - rect.top
  const height = rect.height
  let vol = 1 - (y / height)
  vol = Math.max(0, Math.min(1, vol))
  player.setVolume(vol)
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', updateVolume)
  document.removeEventListener('mouseup', stopDrag)
}

// 创建歌单
const handleCreatePlaylist = async () => {
  if (!newPlaylistName.value.trim()) return
  try {
    await createPlaylist({ name: newPlaylistName.value, songs: [] })
    // 重新获取歌单列表
    const res = await getPlaylists()
    const playlists = res.data
    for (const p of playlists) {
      const detail = await getPlaylist(p.id)
      p.song_details = detail.data.song_details
    }
    player.playlists = playlists
    newPlaylistName.value = ''
    showCreateModal.value = false
    showPlaylist.value = true
  } catch (e) {
    console.error('创建失败:', e)
  }
}

// 删除歌单
const handleDeletePlaylist = async (id: number, e: Event) => {
  e.stopPropagation()
  if (!confirm('确定删除这个歌单？')) return
  try {
    await deletePlaylist(id)
    player.playlists = (player.playlists || []).filter(p => p.id !== id)
  } catch (e) {
    console.error('删除失败:', e)
  }
}

// 添加歌曲到歌单
const handleAddSong = async (playlist: Playlist) => {
  editingPlaylist.value = playlist
  showAddSongModal.value = true
}

const addSongToPlaylist = async (song: Song) => {
  if (!editingPlaylist.value) return
  try {
    const currentSongs = editingPlaylist.value.songs || []
    currentSongs.push({ song_id: song.id, order: currentSongs.length })
    await updatePlaylist(editingPlaylist.value.id, { songs: currentSongs })

    // 更新本地状态
    const updated = await getPlaylist(editingPlaylist.value.id)
    const index = player.playlists.findIndex(p => p.id === editingPlaylist.value!.id)
    if (index !== -1) {
      player.playlists[index] = { ...player.playlists[index], ...updated.data }
    }
    showAddSongModal.value = false
    editingPlaylist.value = null
  } catch (e) {
    console.error('添加失败:', e)
  }
}

// 从歌单移除歌曲
const removeSongFromPlaylist = async (playlist: Playlist, songId: number, e: Event) => {
  e.stopPropagation()
  try {
    const currentSongs = (playlist.songs || []).filter((s: any) => s.song_id !== songId)
    await updatePlaylist(playlist.id, { songs: currentSongs })

    const updated = await getPlaylist(playlist.id)
    const index = player.playlists.findIndex(p => p.id === playlist.id)
    if (index !== -1) {
      player.playlists[index] = { ...player.playlists[index], ...updated.data }
    }
  } catch (e) {
    console.error('移除失败:', e)
  }
}

// 播放歌单
const playPlaylistItem = (playlist: Playlist) => {
  if (!playlist.song_details || playlist.song_details.length === 0) {
    alert('歌单内没有歌曲，无法播放')
    return
  }
  player.playPlaylist(playlist)
  showPlaylist.value = false
}

// 重命名歌单
const renamePlaylist = async (playlist: Playlist) => {
  const newName = prompt('输入新名称:', playlist.name)
  if (!newName || newName === playlist.name) return
  try {
    await updatePlaylist(playlist.id, { name: newName })
    const index = player.playlists.findIndex(p => p.id === playlist.id)
    if (index !== -1) {
      player.playlists[index].name = newName
    }
  } catch (e) {
    console.error('重命名失败:', e)
  }
}
</script>

<template>
  <div class="app-container">
    <!-- 极光背景 -->
    <div class="aurora-bg"></div>
    <div class="aurora aurora-1"></div>
    <div class="aurora aurora-2"></div>
    <div class="aurora aurora-3"></div>

    <div class="main-content">
      <!-- 顶部按钮 -->
      <div class="top-bar">
        <div class="top-left-actions">
          <button class="upload-btn" @click="showUploadModal = true; bilibiliMode = true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            识别URL
          </button>
          <button class="upload-btn" @click="showUploadModal = true; bilibiliMode = false">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            上传歌曲
          </button>
        </div>
        <div class="top-actions">
          <button class="all-songs-btn" @click="showAllSongs = !showAllSongs">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
            </svg>
            全部歌曲
          </button>
          <button class="create-btn" @click="showCreateModal = true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            新建歌单
          </button>
          <button class="playlist-btn" @click="showPlaylist = !showPlaylist">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18V5l12-2v13"></path>
              <circle cx="6" cy="18" r="3"></circle>
              <circle cx="18" cy="16" r="3"></circle>
            </svg>
            歌单
          </button>
        </div>
      </div>

      <!-- 左侧播放器 -->
      <div class="player-left">
        <!-- 圆形封面 -->
        <div class="album-wrapper">
          <div class="album-cover" :class="{ playing: player.isPlaying }">
            <img
              :src="getFullUrl(player.currentSong?.cover_url) || 'https://picsum.photos/400?random=1'"
              alt="封面"
            />
          </div>
          <div class="album-ring"></div>
        </div>

        <!-- 歌曲信息 -->
        <div class="song-info">
          <h1>{{ player.currentSong?.title || '未选择歌曲' }}</h1>
          <p>{{ player.currentSong?.artist || '点击播放' }}</p>
        </div>

        <!-- 进度条 -->
        <div class="progress">
          <span class="time">{{ formatTime(player.currentTime) }}</span>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: (player.currentTime / player.duration * 100) + '%' }"
            ></div>
            <input
              type="range"
              :value="player.currentTime"
              :max="player.duration || 100"
              @input="player.seek(Number(($event.target as HTMLInputElement).value))"
            />
          </div>
          <span class="time">{{ formatTime(player.duration) }}</span>
          <!-- 播放模式按钮 -->
          <button class="playmode-btn" @click="togglePlayMode" :title="playModeText">
            <svg v-if="player.playMode === '顺序'" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 5v14h18V5H3zm10 10H5V7h8v8zm-2-10v8h2V5h-2z"/>
            </svg>
            <svg v-else-if="player.playMode === '随机'" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M10.59 9.17L5.41 4 4 5.41l5.17 5.17 1.42-1.41zM14.5 4l2.04 2.04L4 18.59 5.41 20 17.96 7.46 20 9.5V4h-5.5zm.33 9.41l-1.41 1.41 3.13 3.13L14.5 20H20v-5.5l-2.04 2.04-3.13-3.13z"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
            </svg>
          </button>
        </div>

        <!-- 控制按钮 -->
        <div class="controls">
          <button class="control-btn" @click="player.prev">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
            </svg>
          </button>
          <button class="play-btn" @click="player.togglePlay">
            <svg v-if="!player.isPlaying" width="36" height="36" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
            <svg v-else width="36" height="36" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
            </svg>
          </button>
          <button class="control-btn" @click="player.next">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 右侧竖直音量条 -->
      <div class="volume-vertical">
        <button @click="player.toggleMute" class="volume-btn">
          <svg v-if="player.isMuted || player.volume === 0" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
          </svg>
          <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
          </svg>
        </button>
        <div
          class="volume-slider"
          @mousedown="startDrag"
          ref="volumeSlider"
        >
          <div class="volume-track">
            <div class="volume-fill" :style="{ height: ((player.isMuted ? 0 : player.volume) * 100) + '%' }"></div>
            <div class="volume-thumb" :style="{ bottom: ((player.isMuted ? 0 : player.volume) * 100) + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- 右侧全部歌曲 -->
      <div class="all-songs-panel" :class="{ open: showAllSongs }">
        <div class="panel-header">
          <h3>全部歌曲</h3>
          <button @click="showAllSongs = false">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="all-songs-list">
          <div
            v-for="(song, i) in player.songs"
            :key="song.id"
            :class="['all-song-item', { playing: player.currentSong?.id === song.id }]"
            @click="playQueueSong(song, i)"
          >
            <img :src="getFullUrl(song.cover_url) || 'https://picsum.photos/50?random=' + song.id" />
            <div class="song-info">
              <div>{{ song.title }}</div>
              <small>{{ song.artist }}</small>
            </div>
            <div v-if="player.currentSong?.id === song.id" class="playing-indicator">
              <span></span><span></span><span></span>
            </div>
            <div class="song-actions" @click.stop>
              <button class="action-btn edit-btn" @click="openEditModal(song)" title="编辑">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </button>
              <button class="action-btn delete-btn" @click="confirmDelete(song)" title="删除">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧播放队列 -->
      <div class="queue-panel" :class="{ open: showQueue }">
        <div class="queue-header">
          <h3>播放队列</h3>
          <button @click="showQueue = false">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="queue-list">
          <div
            v-for="(song, i) in (player.queue.length > 0 ? player.queue : player.filteredSongs)"
            :key="song.id"
            :class="['queue-item', { playing: player.currentSong?.id === song.id }]"
            @click="player.queue.length > 0 ? player.queueIndex = i : playQueueSong(song, i); player.playSong(song)"
          >
            <img :src="getFullUrl(song.cover_url) || 'https://picsum.photos/50?random=' + song.id" />
            <div class="queue-info">
              <div>{{ song.title }}</div>
              <small>{{ song.artist }}</small>
            </div>
            <div v-if="player.currentSong?.id === song.id" class="playing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 左侧展开按钮 -->
      <button v-if="!showQueue" class="queue-toggle-btn" @click="showQueue = true">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="8" y1="6" x2="21" y2="6"></line>
          <line x1="8" y1="12" x2="21" y2="12"></line>
          <line x1="8" y1="18" x2="21" y2="18"></line>
          <line x1="3" y1="6" x2="3.01" y2="6"></line>
          <line x1="3" y1="12" x2="3.01" y2="12"></line>
          <line x1="3" y1="18" x2="3.01" y2="18"></line>
        </svg>
      </button>
    </div>

    <!-- 上传歌曲弹窗 -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal upload-modal">
        <h3>上传歌曲</h3>
        <!-- 模式切换 -->
        <div class="upload-mode-tabs">
          <button :class="{ active: !bilibiliMode }" @click="switchToLocalUpload">本地上传</button>
          <button :class="{ active: bilibiliMode }" @click="switchToBiliBiliUpload">B站视频</button>
        </div>

        <!-- B站模式 -->
        <div v-if="bilibiliMode" class="upload-form">
          <div class="form-group">
            <label>B站视频URL</label>
            <input v-model="bilibiliUrl" type="text" placeholder="输入B站视频链接，如: https://www.bilibili.com/video/BV1xx411c7mD" />
          </div>
          <button class="parse-btn" @click="parseBiliBiliVideo" :disabled="parsingBiliBili">
            <svg v-if="!parsingBiliBili" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
            <span class="spinner" v-if="parsingBiliBili"></span>
            {{ parsingBiliBili ? '解析中...' : '解析视频' }}
          </button>

          <!-- 解析结果 -->
          <div v-if="parsedBiliBiliInfo" class="bilibili-preview">
            <div class="preview-cover">
              <img v-if="parsedBiliBiliInfo.cover_url" :src="parsedBiliBiliInfo.cover_url" alt="封面" />
              <div v-else class="no-cover">无封面</div>
            </div>
            <div class="preview-info">
              <h4>{{ parsedBiliBiliInfo.title }}</h4>
              <p>作者: {{ parsedBiliBiliInfo.author }}</p>
              <p v-if="parsedBiliBiliInfo.duration">时长: {{ Math.floor(parsedBiliBiliInfo.duration / 60) }}:{{ String(parsedBiliBiliInfo.duration % 60).padStart(2, '0') }}</p>
            </div>
          </div>

          <div v-if="parsedBiliBiliInfo" class="form-group">
            <label>歌曲标题（可修改）</label>
            <input v-model="uploadForm.title" type="text" />
          </div>
          <div v-if="parsedBiliBiliInfo" class="form-group">
            <label>艺术家（可修改）</label>
            <input v-model="uploadForm.artist" type="text" />
          </div>
          <div v-if="parsedBiliBiliInfo" class="form-group">
            <label>专辑</label>
            <input v-model="uploadForm.album" type="text" placeholder="输入专辑名称（可选）" />
          </div>
          <div v-if="parsedBiliBiliInfo" class="form-group">
            <label>标签</label>
            <div class="tags-input">
              <span v-for="(tag, i) in uploadForm.tags" :key="i" class="tag-item">
                {{ tag }}
                <button @click="removeTag(i)">×</button>
              </span>
              <input v-model="tagInput" type="text" placeholder="输入标签后按回车" @keyup.enter="addTag" />
            </div>
          </div>
        </div>

        <!-- 本地上传模式 -->
        <div v-else class="upload-form">
          <div class="form-group">
            <label>歌曲标题</label>
            <input v-model="uploadForm.title" type="text" placeholder="输入歌曲标题" />
          </div>
          <div class="form-group">
            <label>艺术家</label>
            <input v-model="uploadForm.artist" type="text" placeholder="输入艺术家名称" />
          </div>
          <div class="form-group">
            <label>专辑</label>
            <input v-model="uploadForm.album" type="text" placeholder="输入专辑名称（可选）" />
          </div>
          <div class="form-group">
            <label>标签</label>
            <div class="tags-input">
              <span v-for="(tag, i) in uploadForm.tags" :key="i" class="tag-item">
                {{ tag }}
                <button @click="removeTag(i)">×</button>
              </span>
              <input
                v-model="tagInput"
                type="text"
                placeholder="输入标签后按回车"
                @keyup.enter="addTag"
              />
            </div>
          </div>
          <div class="form-group">
            <label>歌词（LRC格式）</label>
            <textarea v-model="uploadForm.lyrics" placeholder="输入LRC格式歌词（可选）" rows="4"></textarea>
          </div>
          <div class="form-group">
            <label>音频文件</label>
            <input type="file" accept="audio/*" @change="handleAudioFile" />
          </div>
          <div class="form-group">
            <label>封面图片</label>
            <input type="file" accept="image/*" @change="handleCoverFile" />
          </div>
        </div>
        <!-- 下载进度条 -->
        <div v-if="downloadingBiliBili" class="download-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: downloadProgress + '%' }"></div>
          </div>
          <span class="progress-text">{{ downloadProgress }}%</span>
        </div>
        <div class="modal-actions">
          <button @click="showUploadModal = false">取消</button>
          <button v-if="bilibiliMode" class="primary" @click="downloadBiliBiliVideo" :disabled="downloadingBiliBili || !parsedBiliBiliInfo">
            {{ downloadingBiliBili ? '下载中...' : '下载并上传' }}
          </button>
          <button v-else class="primary" @click="handleUpload" :disabled="uploading">
            {{ uploading ? '上传中...' : '上传' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑歌曲弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal">
        <h3>编辑歌曲</h3>
        <div class="form-group">
          <label>歌曲标题</label>
          <input v-model="editForm.title" type="text" />
        </div>
        <div class="form-group">
          <label>艺术家</label>
          <input v-model="editForm.artist" type="text" />
        </div>
        <div class="form-group">
          <label>专辑</label>
          <input v-model="editForm.album" type="text" />
        </div>
        <div class="form-group">
          <label>标签</label>
          <div class="tags-input">
            <span v-for="(tag, i) in editForm.tags" :key="i" class="tag-item">
              {{ tag }}
              <button @click="editForm.tags.splice(i, 1)">×</button>
            </span>
            <input
              v-model="tagInput"
              type="text"
              placeholder="输入标签后按回车"
              @keyup.enter="editForm.tags.push(tagInput.trim()) || (tagInput = '')"
            />
          </div>
        </div>
        <div class="modal-actions">
          <button @click="showEditModal = false">取消</button>
          <button class="primary" @click="handleEdit">保存</button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="showDeleteConfirm = false">
      <div class="modal">
        <h3>确认删除</h3>
        <p>确定要删除歌曲 "{{ deletingSong?.title }}" 吗？</p>
        <div class="modal-actions">
          <button @click="showDeleteConfirm = false">取消</button>
          <button class="danger" @click="handleDelete">删除</button>
        </div>
      </div>
    </div>

    <!-- 歌单抽屉 -->
    <div :class="['playlist-drawer', { open: showPlaylist }]">
      <div class="drawer-header">
        <h2>我的歌单</h2>
        <button @click="showPlaylist = false">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <!-- 歌单列表 -->
      <div class="playlists">
        <template v-if="player.playlists && player.playlists.length > 0">
          <div
            v-for="p in player.playlists"
            :key="p.id"
            class="playlist-item"
          >
            <div class="playlist-main" @click="player.playPlaylist(p)">
              <div class="playlist-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                </svg>
              </div>
              <div class="playlist-info">
                <div class="playlist-name">{{ p.name }}</div>
                <div class="playlist-songs">{{ p.song_details?.length || 0 }} 首</div>
              </div>
            </div>
            <div class="playlist-actions">
              <button @click="handleAddSong(p)" title="添加歌曲">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
              </button>
              <button @click="renamePlaylist(p)" title="重命名">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </button>
              <button @click="handleDeletePlaylist(p.id, $event)" class="delete-btn" title="删除">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
              <button
                @click="playPlaylistItem(p)"
                title="播放歌单"
                class="play-single-btn"
                :disabled="!p.song_details || p.song_details.length === 0"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </button>
            </div>
          </div>
        </template>
        <div v-else class="empty-playlists">
          <p>暂无歌单</p>
          <button @click="showCreateModal = true">创建歌单</button>
        </div>
      </div>
    </div>

    <div v-if="showPlaylist" class="overlay" @click="showPlaylist = false"></div>

    <!-- 创建歌单弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <h3>新建歌单</h3>
        <input
          v-model="newPlaylistName"
          type="text"
          placeholder="输入歌单名称"
          @keyup.enter="handleCreatePlaylist"
        />
        <div class="modal-actions">
          <button @click="showCreateModal = false">取消</button>
          <button class="primary" @click="handleCreatePlaylist">创建</button>
        </div>
      </div>
    </div>

    <!-- 添加歌曲弹窗 -->
    <div v-if="showAddSongModal" class="modal-overlay" @click.self="showAddSongModal = false">
      <div class="modal add-song-modal">
        <h3>添加到歌单: {{ editingPlaylist?.name }}</h3>
        <div class="song-list">
          <div
            v-for="song in player.songs"
            :key="song.id"
            class="song-option"
            @click="addSongToPlaylist(song)"
          >
            <img :src="getFullUrl(song.cover_url) || 'https://picsum.photos/50?random=' + song.id" />
            <div>
              <div>{{ song.title }}</div>
              <small>{{ song.artist }}</small>
            </div>
          </div>
        </div>
        <button class="close-btn" @click="showAddSongModal = false">关闭</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

/* 极光背景 */
.aurora-bg {
  position: fixed;
  inset: 0;
  background: linear-gradient(180deg, #0a0a1a 0%, #1a1a3a 50%, #0d1b2a 100%);
  z-index: 0;
}

.aurora {
  position: fixed;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: aurora 15s ease-in-out infinite;
}

.aurora-1 {
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, #00ff88, #00ccff);
  top: -200px;
  left: -100px;
}

.aurora-2 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #ff00ff, #8800ff);
  bottom: -100px;
  right: -100px;
  animation-delay: -5s;
}

.aurora-3 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #00ffff, #00ff88);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -10s;
}

@keyframes aurora {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(50px, -30px) scale(1.1); }
  50% { transform: translate(-30px, 50px) scale(0.9); }
  75% { transform: translate(40px, 20px) scale(1.05); }
}

.main-content {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 30px 20px 30px 400px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  flex-wrap: wrap;
  gap: 15px;
}

.tags {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.tag {
  padding: 10px 20px;
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 25px;
  background: rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.tag:hover {
  background: rgba(255,255,255,0.1);
  color: white;
}

.tag.active {
  background: rgba(255,255,255,0.2);
  border-color: rgba(255,255,255,0.4);
  color: white;
  box-shadow: 0 0 20px rgba(255,255,255,0.1);
}

.top-actions {
  display: flex;
  gap: 12px;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 25px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.create-btn:hover {
  background: rgba(255,255,255,0.2);
}

.playlist-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  background: linear-gradient(135deg, rgba(0,255,136,0.2), rgba(0,204,255,0.2));
  border: 1px solid rgba(0,255,136,0.3);
  border-radius: 25px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.playlist-btn:hover {
  background: linear-gradient(135deg, rgba(0,255,136,0.3), rgba(0,204,255,0.3));
  box-shadow: 0 0 30px rgba(0,255,136,0.2);
}

.player-left {
  position: fixed;
  left: 240px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.album-wrapper {
  position: relative;
  width: 320px;
  height: 320px;
}

.album-cover {
  width: 280px;
  height: 280px;
  border-radius: 50%;
  overflow: hidden;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 60px rgba(0,0,0,0.5), inset 0 0 30px rgba(0,0,0,0.3);
  z-index: 2;
}

.album-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.album-cover.playing img {
  animation: rotate 8s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.album-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 300px;
  height: 300px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.1);
  z-index: 1;
}

.album-ring::before {
  content: '';
  position: absolute;
  inset: -15px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.05);
}

.song-info {
  text-align: center;
}

.song-info h1 {
  font-size: 2.5rem;
  font-weight: 300;
  margin-bottom: 15px;
  background: linear-gradient(135deg, #fff, rgba(255,255,255,0.7));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.song-info p {
  color: rgba(255,255,255,0.5);
  font-size: 1.1rem;
}

/* 进度条 */
.progress {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 280px;
}

.time {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  min-width: 40px;
}

.progress-bar {
  flex: 1;
  position: relative;
  height: 4px;
  background: rgba(255,255,255,0.15);
  border-radius: 2px;
}

.progress-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: linear-gradient(90deg, #00ff88, #00ccff);
  border-radius: 2px;
}

.progress-bar input {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

/* 播放模式按钮 */
.playmode-btn {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.playmode-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 控制按钮 */
.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 30px;
}

.control-btn {
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  padding: 10px;
  transition: all 0.3s;
  border-radius: 50%;
}

.control-btn:hover {
  color: white;
  background: rgba(255,255,255,0.1);
}

.play-btn {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00ff88, #00ccff);
  border: none;
  color: #0a0a1a;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  box-shadow: 0 0 40px rgba(0,255,136,0.3);
}

.play-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 0 60px rgba(0,255,136,0.5);
}

/* 右侧竖直音量条 */
.volume-vertical {
  position: fixed;
  right: 30px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  z-index: 10;
}

.volume-vertical .volume-btn {
  background: rgba(255,255,255,0.1);
  border: none;
  color: rgba(255,255,255,0.8);
  cursor: pointer;
  padding: 12px;
  border-radius: 50%;
  transition: all 0.3s;
}

.volume-vertical .volume-btn:hover {
  background: rgba(255,255,255,0.2);
  color: white;
}

.volume-slider {
  position: relative;
  height: 150px;
  width: 40px;
  cursor: pointer;
}

.volume-track {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 100%;
  background: rgba(255,255,255,0.15);
  border-radius: 3px;
  overflow: visible;
}

.volume-fill {
  position: absolute;
  bottom: 0;
  width: 100%;
  background: linear-gradient(to top, #00ff88, #00ccff);
  border-radius: 3px;
  transition: height 0.05s;
}

.volume-thumb {
  position: absolute;
  left: 50%;
  transform: translateX(-50%) translateY(50%);
  width: 16px;
  height: 16px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(0,255,136,0.5);
  transition: bottom 0.05s;
}

/* 右侧全部歌曲面板 */
.all-songs-panel {
  position: fixed;
  right: 30px;
  top: 80px;
  width: 500px;
  max-height: calc(100vh - 160px);
  background: rgba(10, 10, 26, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 20px;
  z-index: 10;
  opacity: 0;
  transform: translateX(30px);
  pointer-events: none;
  transition: all 0.3s ease;
}

.all-songs-panel.open {
  opacity: 1;
  transform: translateX(0);
  pointer-events: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-header h3 {
  font-size: 1.1rem;
  color: rgba(255,255,255,0.9);
}

.panel-header button {
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.5);
  cursor: pointer;
  padding: 4px;
}

.all-songs-list {
  max-height: calc(100vh - 240px);
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.all-song-item {
  display: flex;
  flex-direction: column;
  padding: 12px;
  cursor: pointer;
  border-radius: 16px;
  background: rgba(255,255,255,0.05);
  transition: all 0.2s;
}

.all-song-item:hover {
  background: rgba(255,255,255,0.1);
  transform: translateY(-2px);
}

.all-song-item.playing {
  background: rgba(0,255,136,0.15);
  border: 1px solid rgba(0,255,136,0.3);
}

.all-song-item img {
  width: 100%;
  height: 140px;
  border-radius: 12px;
  object-fit: cover;
}

.all-song-item .song-info {
  flex: 1;
  min-width: 0;
  margin-top: 10px;
}

.all-song-item .song-info div {
  font-size: 0.95rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.all-song-item .song-info small {
  font-size: 0.8rem;
  color: rgba(255,255,255,0.5);
}

/* 顶部左侧按钮 */
.top-left-actions {
  display: flex;
  gap: 10px;
}

.upload-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, rgba(0,255,136,0.2), rgba(0,204,255,0.2));
  border: 1px solid rgba(0,255,136,0.3);
  border-radius: 25px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-btn:hover {
  background: linear-gradient(135deg, rgba(0,255,136,0.3), rgba(0,204,255,0.3));
  box-shadow: 0 0 20px rgba(0,255,136,0.2);
}

/* 上传弹窗 */
.upload-modal {
  max-width: 500px;
}

.upload-form {
  max-height: 60vh;
  overflow-y: auto;
}

/* 上传模式切换标签 */
.upload-mode-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.upload-mode-tabs button {
  flex: 1;
  padding: 12px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 10px;
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  transition: all 0.3s;
}

.upload-mode-tabs button.active {
  background: rgba(0,255,136,0.2);
  border-color: #00ff88;
  color: #00ff88;
}

/* 下载进度条 */
.download-progress {
  margin-bottom: 15px;
}

.progress-bar {
  height: 8px;
  background: rgba(255,255,255,0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00ff88, #00ccff);
  transition: width 0.3s ease;
}

.progress-text {
  display: block;
  text-align: center;
  font-size: 0.85rem;
  color: rgba(255,255,255,0.7);
  margin-top: 5px;
}

/* 解析视频按钮 */
.parse-btn {
  width: 100%;
  margin-top: 15px;
  padding: 14px 20px;
  background: linear-gradient(135deg, #00c6ff, #0072ff);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.parse-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 198, 255, 0.4);
}

.parse-btn:disabled {
  background: #555;
  cursor: not-allowed;
  opacity: 0.7;
}

.parse-btn svg {
  width: 18px;
  height: 18px;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* B站预览 */
.bilibili-preview {
  display: flex;
  gap: 15px;
  padding: 15px;
  background: rgba(255,255,255,0.1);
  border-radius: 12px;
  margin: 15px 0;
}

.preview-cover {
  width: 120px;
  height: 80px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: rgba(0,0,0,0.3);
}

.preview-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-cover {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.5);
  font-size: 0.8rem;
}

.preview-info {
  flex: 1;
  overflow: hidden;
}

.preview-info h4 {
  font-size: 0.95rem;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview-info p {
  font-size: 0.8rem;
  color: rgba(255,255,255,0.6);
  margin: 3px 0;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  color: rgba(255,255,255,0.7);
  margin-bottom: 8px;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 12px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 10px;
  color: white;
  font-size: 0.95rem;
  outline: none;
}

.form-group input[type="text"]:focus,
.form-group textarea:focus {
  border-color: #00ff88;
}

.form-group input[type="file"] {
  color: rgba(255,255,255,0.7);
}

.tags-input {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 10px;
}

.tags-input input {
  flex: 1;
  min-width: 120px;
  background: transparent;
  border: none;
  color: white;
  outline: none;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  background: rgba(0,255,136,0.2);
  border-radius: 15px;
  font-size: 0.85rem;
}

.tag-item button {
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  padding: 0;
  font-size: 1rem;
  line-height: 1;
}

/* 全部歌曲按钮 */
.all-songs-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 25px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.all-songs-btn:hover {
  background: rgba(255,255,255,0.2);
}

/* 右侧播放队列 */
.queue-panel {
  position: fixed;
  right: 80px;
  bottom: 30px;
  width: 280px;
  max-height: 300px;
  background: rgba(10, 10, 26, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  padding: 15px;
  z-index: 10;
  opacity: 0;
  transform: translateY(20px);
  pointer-events: none;
  transition: all 0.3s ease;
}

.queue-panel.open {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.queue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.queue-header h3 {
  font-size: 0.85rem;
  color: rgba(255,255,255,0.6);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.queue-header button {
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.5);
  cursor: pointer;
  padding: 4px;
}

.queue-list {
  max-height: 220px;
  overflow-y: auto;
}

.queue-panel .queue-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  cursor: pointer;
  border-radius: 10px;
  transition: background 0.2s;
}

.queue-panel .queue-item:hover {
  background: rgba(255,255,255,0.05);
}

.queue-panel .queue-item.playing {
  background: rgba(0,255,136,0.1);
}

.queue-panel .queue-item img {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  object-fit: cover;
}

.queue-panel .queue-info {
  flex: 1;
  min-width: 0;
}

.queue-panel .queue-info div {
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.queue-panel .queue-info small {
  font-size: 0.75rem;
  color: rgba(255,255,255,0.5);
}

/* 右侧展开按钮 */
.queue-toggle-btn {
  position: fixed;
  right: 20px;
  bottom: 30px;
  width: 50px;
  height: 50px;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: all 0.3s;
}

.queue-toggle-btn:hover {
  background: rgba(20, 20, 40, 0.95);
  border-color: rgba(0,255,136,0.3);
  box-shadow: 0 0 20px rgba(0,255,136,0.2);
}

/* 歌单抽屉 */
.playlist-drawer {
  position: fixed;
  right: -420px;
  top: 0;
  width: 420px;
  height: 100vh;
  background: rgba(10, 10, 26, 0.98);
  backdrop-filter: blur(20px);
  z-index: 100;
  transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 30px;
  overflow-y: auto;
}

.playlist-drawer.open {
  right: 0;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.drawer-header h2 {
  font-size: 1.5rem;
  font-weight: 300;
}

.drawer-header button {
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  padding: 5px;
}

.playlist-item {
  background: rgba(255,255,255,0.05);
  border-radius: 15px;
  margin-bottom: 12px;
  overflow: hidden;
}

.playlist-main {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  cursor: pointer;
  transition: background 0.3s;
}

.playlist-main:hover {
  background: rgba(255,255,255,0.05);
}

.playlist-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, #00ff88, #00ccff);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0a0a1a;
}

.playlist-info {
  flex: 1;
}

.playlist-name {
  font-size: 1rem;
  margin-bottom: 5px;
}

.playlist-songs {
  font-size: 0.8rem;
  color: rgba(255,255,255,0.5);
}

.playlist-actions {
  display: flex;
  gap: 8px;
  padding: 0 15px 15px;
}

.playlist-actions button {
  background: rgba(255,255,255,0.1);
  border: none;
  color: rgba(255,255,255,0.7);
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.playlist-actions button:hover {
  background: rgba(255,255,255,0.2);
  color: white;
}

.playlist-actions button:disabled,
.playlist-actions .disabled-btn {
  opacity: 0.3;
  cursor: not-allowed;
}

.playlist-actions button:disabled:hover,
.playlist-actions .disabled-btn:hover {
  background: rgba(255,255,255,0.1);
  color: inherit;
}

.playlist-actions .play-single-btn {
  width: 40px;
  height: 40px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #00ff88, #00ccff);
  color: #0a0a1a;
  border-radius: 50%;
}

.playlist-actions .play-single-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 0 20px rgba(0,255,136,0.4);
}

.playlist-actions .play-single-btn:disabled {
  background: rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.3);
}

.playlist-actions .delete-btn:hover {
  background: rgba(255,100,100,0.3);
  color: #ff6666;
}

.empty-playlists {
  text-align: center;
  padding: 40px 20px;
}

.empty-playlists p {
  color: rgba(255,255,255,0.5);
  margin-bottom: 20px;
}

.empty-playlists button {
  padding: 12px 30px;
  background: linear-gradient(135deg, rgba(0,255,136,0.2), rgba(0,204,255,0.2));
  border: 1px solid rgba(0,255,136,0.3);
  border-radius: 25px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.empty-playlists button:hover {
  background: linear-gradient(135deg, rgba(0,255,136,0.3), rgba(0,204,255,0.3));
}

.queue {
  margin-top: 30px;
}

.queue h3 {
  font-size: 0.9rem;
  color: rgba(255,255,255,0.5);
  margin-bottom: 15px;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.queue-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  border-radius: 12px;
  transition: all 0.3s;
}

.queue-item:hover {
  background: rgba(255,255,255,0.05);
}

.queue-item.playing {
  background: rgba(0,255,136,0.1);
}

.queue-item img {
  width: 45px;
  height: 45px;
  border-radius: 8px;
  object-fit: cover;
}

.queue-info {
  flex: 1;
}

.queue-info div {
  font-size: 0.95rem;
  margin-bottom: 3px;
}

.queue-info small {
  font-size: 0.8rem;
  color: rgba(255,255,255,0.5);
}

.playing-indicator {
  display: flex;
  gap: 3px;
  align-items: flex-end;
  height: 16px;
}

.playing-indicator span {
  width: 3px;
  background: #00ff88;
  border-radius: 2px;
  animation: eq 0.8s ease-in-out infinite;
}

.playing-indicator span:nth-child(1) { height: 8px; animation-delay: 0s; }
.playing-indicator span:nth-child(2) { height: 14px; animation-delay: 0.2s; }
.playing-indicator span:nth-child(3) { height: 10px; animation-delay: 0.4s; }

/* 歌曲操作按钮 */
.song-actions {
  display: flex;
  gap: 4px;
  margin-left: auto;
  opacity: 0;
  transition: opacity 0.2s;
}

.all-song-item:hover .song-actions {
  opacity: 1;
}

.action-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.edit-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.edit-btn:hover {
  background: rgba(59, 130, 246, 0.5);
}

.delete-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.5);
}

/* 危险按钮样式 */
button.danger {
  background: #ef4444;
  color: white;
}

button.danger:hover {
  background: #dc2626;
}

@keyframes eq {
  0%, 100% { transform: scaleY(0.5); }
  50% { transform: scaleY(1); }
}

.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 50;
  backdrop-filter: blur(5px);
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background: rgba(20, 20, 40, 0.95);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 30px;
  width: 90%;
  max-width: 400px;
}

.modal h3 {
  margin-bottom: 20px;
  font-weight: 300;
}

.modal input {
  width: 100%;
  padding: 15px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  outline: none;
}

.modal input:focus {
  border-color: #00ff88;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.modal-actions button {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
  background: rgba(255,255,255,0.1);
  color: white;
}

.modal-actions button.primary {
  background: linear-gradient(135deg, #00ff88, #00ccff);
  color: #0a0a1a;
  font-weight: 600;
}

.modal-actions button.primary:disabled {
  background: #555;
  color: #888;
  cursor: not-allowed;
}

.add-song-modal {
  max-width: 500px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
}

.song-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 15px;
}

.song-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  border-radius: 12px;
  transition: background 0.3s;
}

.song-option:hover {
  background: rgba(255,255,255,0.1);
}

.song-option img {
  width: 45px;
  height: 45px;
  border-radius: 8px;
  object-fit: cover;
}

.song-option div {
  flex: 1;
}

.song-option small {
  color: rgba(255,255,255,0.5);
}

.close-btn {
  width: 100%;
  padding: 12px;
  background: rgba(255,255,255,0.1);
  border: none;
  border-radius: 12px;
  color: white;
  cursor: pointer;
}
</style>
