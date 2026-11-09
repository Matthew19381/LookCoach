import { useState, useEffect } from 'react'
import { Play, Search } from 'lucide-react'
import { getAllVideos, getRecommendedVideos, searchVideos } from '../api/client'

export default function VideoLearning() {
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])

  const [fromAnalysis, setFromAnalysis] = useState(true)

  useEffect(() => {
    // Without a photo analysis there is nothing to recommend; show every technique instead
    // of an empty page that says "nothing found".
    getRecommendedVideos()
      .then(async (data) => {
        if (data && data.length > 0) {
          setVideos(data)
        } else {
          setFromAnalysis(false)
          setVideos((await getAllVideos()) || [])
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false))
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
    return <div className="text-center py-20">Ładowanie...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Wideo</h1>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <input aria-label="Szukaj techniki"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Szukaj techniki (gua sha, masaż, włosy...)"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
        >
          <Search size={16} />
          Szukaj
        </button>
      </form>

      {searchResults.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-3 text-sm text-blue-800">
          Wyniki dla „{query}”: {searchResults.length}
          <button
            onClick={() => { setSearchResults([]); setQuery('') }}
            className="ml-2 underline"
          >
            Wyczyść
          </button>
        </div>
      )}

      {!fromAnalysis && searchResults.length === 0 && (
        <p className="text-sm text-gray-600">Brak analizy zdjęcia, więc pokazuję wszystkie techniki.</p>
      )}

      <p className="text-sm text-gray-600">
        Linki prowadzą do wyników wyszukiwania na YouTube, nie do sprawdzonych filmów. Przy każdej
        technice jest poziom dowodu: większość to [HIPOTEZA] bez badań klinicznych na wygląd.
      </p>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {displayVideos.map((video) => (
          <div key={video.id} className="bg-white border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
            <div className="p-4">
              <h3 className="font-semibold text-gray-900 mb-1 line-clamp-2">{video.title}</h3>
              <p className="text-xs text-gray-500 mb-2">{video.description}</p>
              <p className="text-xs text-amber-800 bg-amber-50 rounded p-2">
                {video.evidence_note}
                {video.study_url && (
                  <>
                    {' '}
                    <a href={video.study_url} target="_blank" rel="noopener noreferrer" className="underline">
                      Badanie
                    </a>
                  </>
                )}
              </p>
              <a
                href={video.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center mt-3 text-sm text-blue-600 hover:text-blue-800"
              >
                <Play size={14} className="mr-1" />
                Szukaj na YouTube
              </a>
            </div>
          </div>
        ))}
      </div>

      {displayVideos.length === 0 && !loading && (
        <div className="text-center py-10 text-gray-500">
          Nie znaleziono techniki. Spróbuj innej frazy.
        </div>
      )}
    </div>
  )
}
