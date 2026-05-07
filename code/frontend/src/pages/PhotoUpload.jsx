import { useState } from 'react'
import { Camera, Upload, CheckCircle, Loader2 } from 'lucide-react'
import { uploadPhoto, getPhotos } from '../api/client'

export default function PhotoUpload() {
  const [uploading, setUploading] = useState({ front: false, side: false, back: false })
  const [uploaded, setUploaded] = useState({ front: null, side: null, back: null })
  const [error, setError] = useState('')

  const handleUpload = async (file, type) => {
    if (!file) return
    setUploading((prev) => ({ ...prev, [type]: true }))
    setError('')
    try {
      const result = await uploadPhoto(file, type)
      setUploaded((prev) => ({ ...prev, [type]: result }))
    } catch (e) {
      setError(`Upload failed: ${e.message}`)
    } finally {
      setUploading((prev) => ({ ...prev, [type]: false }))
    }
  }

  const handleDrop = (e, type) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      handleUpload(file, type)
    }
  }

  const handleFileSelect = (e, type) => {
    const file = e.target.files[0]
    if (file) handleUpload(file, type)
  }

  const allUploaded = uploaded.front && uploaded.side && uploaded.back

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Upload Your Photos</h1>
        <p className="mt-2 text-gray-600">
          Upload front, side, and back photos for AI analysis
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 text-red-800">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {['front', 'side', 'back'].map((type) => (
          <div
            key={type}
            onDrop={(e) => handleDrop(e, type)}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer"
          >
            <div className="flex flex-col items-center space-y-4">
              <div className={`p-4 rounded-full ${uploaded[type] ? 'bg-green-100' : 'bg-gray-100'}`}>
                {uploaded[type] ? (
                  <CheckCircle size={32} className="text-green-600" />
                ) : (
                  <Camera size={32} className="text-gray-500" />
                )}
              </div>
              <div>
                <p className="font-medium capitalize">{type} View</p>
                <p className="text-sm text-gray-500">
                  {uploaded[type] ? 'Uploaded!' : 'Drop image or click to upload'}
                </p>
              </div>
              {uploading[type] && <Loader2 size={20} className="animate-spin text-blue-600" />}
              <label className="cursor-pointer inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                <Upload size={16} className="mr-2" />
                Choose File
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => handleFileSelect(e, type)}
                />
              </label>
            </div>
          </div>
        ))}
      </div>

      {allUploaded && (
        <div className="flex justify-center">
          <a
            href="/analysis"
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
          >
            View Analysis
          </a>
        </div>
      )}
    </div>
  )
}
