import { useState, useEffect } from 'react'
import { Play, Search } from 'lucide-react'
import { getRecommendedVideos, searchVideos } from '../api/client'

export default function VideoLearning() {
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])

  useEffect(() => {
    getRecommendedVideos().then((data) => {
      setVideos(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    try {
      const results = await searchVideos(query)
      setSearchResults(results)
    } catch (e) {
      console.error('Search failed:', e)
    }
  }

  const displayVideos = searchResults.length > 0 ? searchResults : videos

  if (loading) {
    return <div className="text-center py-20">Loading videos...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Video Learning</h1>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search videos (gua sha, massage, skincare...)"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
        >
          <Search size={16} />
          Search
        </button>
      </form>

      {searchResults.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-3 text-sm text-blue-800">
          Found {searchResults.length} results for "{query}"
          <button
            onClick={() => { setSearchResults([]); setQuery('') }}
            className="ml-2 underline"
          >
            Clear
          </button>
        </div>
      )}

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {displayVideos.map((video, idx) => (
          <div key={idx} className="bg-white border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
            <a href={video.url} target="_blank" rel="noopener noreferrer">
              <div className="bg-gray-200 h-40 flex items-center justify-center">
                <Play size={48} className="text-gray-400" />
              </div>
            </a>
            <div className="p-4">
              <h3 className="font-semibold text-gray-900 mb-1 line-clamp-2">{video.title}</h3>
              <p className="text-sm text-gray-600 mb-2">{video.channel} • {video.duration}</p>
              <p className="text-xs text-gray-500 line-clamp-2">{video.description}</p>
              <a
                href={video.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center mt-3 text-sm text-blue-600 hover:text-blue-800"
              >
                <Play size={14} className="mr-1" />
                Watch on YouTube
              </a>
            </div>
          </div>
        ))}
      </div>

      {displayVideos.length === 0 && !loading && (
        <div className="text-center py-10 text-gray-500">
          No videos found. Try a different search term.
        </div>
      )}
    </div>
  )
}
