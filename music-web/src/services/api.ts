import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
})

// 歌曲 API
export const getSongs = (tag?: string) => {
  const params = tag ? { tag } : {}
  return api.get('/songs', { params })
}

export const getSong = (id: number) => api.get(`/songs/${id}`)

export const getTags = () => api.get('/songs/tags')

export const uploadSong = (formData: FormData) => {
  return api.post('/songs/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const updateSong = (id: number, data: any) => {
  return api.put(`/songs/${id}`, data)
}

export const deleteSong = (id: number) => {
  return api.delete(`/songs/${id}`)
}

// 歌单 API
export const getPlaylists = () => api.get('/playlists')

export const getPlaylist = (id: number) => api.get(`/playlists/${id}`)

export const createPlaylist = (data: { name: string, songs: any[] }) => {
  return api.post('/playlists', data)
}

export const updatePlaylist = (id: number, data: any) => {
  return api.put(`/playlists/${id}`, data)
}

export const deletePlaylist = (id: number) => {
  return api.delete(`/playlists/${id}`)
}

// B站视频解析 API
export interface BiliBiliParseResult {
  bvid: string
  title: string
  author: string
  cover_url?: string
  duration?: number
  description?: string
}

export const parseBilibiliVideo = (url: string) => {
  const formData = new FormData()
  formData.append('url', url)
  return api.post<BiliBiliParseResult>('/bilibili/parse', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const downloadBilibiliVideo = (data: {
  url: string
  title: string
  artist: string
  album?: string
  tags?: string[]
  lyrics?: string
  cover_url?: string
}) => {
  const formData = new FormData()
  formData.append('url', data.url)
  formData.append('title', data.title)
  formData.append('artist', data.artist)
  if (data.album) formData.append('album', data.album)
  formData.append('tags', JSON.stringify(data.tags || []))
  if (data.lyrics) formData.append('lyrics', data.lyrics)
  if (data.cover_url) formData.append('cover_url_from_parse', data.cover_url)

  return api.post('/bilibili/download', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export default api
