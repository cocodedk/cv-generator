import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { CVListResponse, CVListItem } from '../types/cv'
import { openDownload } from '../app_helpers/download'
import { downloadPdf } from '../app_helpers/pdfDownload'

interface CVListProps {
  onError: (message: string) => void
}

export default function CVList({ onError }: CVListProps) {
  const [cvs, setCvs] = useState<CVListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [total, setTotal] = useState(0)
  const [isGeneratingPdf, setIsGeneratingPdf] = useState<{ [key: string]: boolean }>({})
  const searchRef = useRef(search)

  // Keep search ref in sync
  useEffect(() => {
    searchRef.current = search
  }, [search])

  const fetchCVs = async (searchTerm?: string) => {
    setLoading(true)
    try {
      const params: any = { limit: 50, offset: 0 }
      if (searchTerm) {
        params.search = searchTerm
      }
      const response = await axios.get<CVListResponse>('/api/cvs', { params })
      setCvs(response.data.cvs)
      setTotal(response.data.total)
    } catch (error: any) {
      onError(error.response?.data?.detail || 'Failed to load CVs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCVs()
  }, [])

  // Refresh list when navigating back from edit mode
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash
      // Refresh when navigating to list view
      if (hash === '#list' || hash === '' || hash === '#') {
        // Use current search value from ref to avoid stale closure
        fetchCVs(searchRef.current || undefined)
      }
    }

    // Check initial hash
    handleHashChange()

    // Listen for hash changes
    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, []) // Only run once on mount

  const handleSearch = () => {
    fetchCVs(search || undefined)
  }

  const handleDelete = async (cvId: string) => {
    if (!confirm('Are you sure you want to delete this CV?')) {
      return
    }
    try {
      await axios.delete(`/api/cv/${cvId}`)
      fetchCVs(search || undefined)
    } catch (error: any) {
      onError(error.response?.data?.detail || 'Failed to delete CV')
    }
  }

  const handleDownload = (filename?: string) => {
    if (!filename) {
      return
    }
    openDownload(filename)
  }

  const handleGenerateFile = async (cvId: string) => {
    try {
      await axios.post(`/api/cv/${cvId}/generate-html`)
      // Refresh the list to show the download button
      fetchCVs(search || undefined)
    } catch (error: any) {
      onError(error.response?.data?.detail || 'Failed to generate CV file')
    }
  }

  const handleDownloadPdf = async (cvId: string) => {
    // Prevent multiple simultaneous requests for same CV
    if (isGeneratingPdf[cvId]) {
      return
    }

    setIsGeneratingPdf(prev => ({ ...prev, [cvId]: true }))
    try {
      await downloadPdf(cvId)
    } catch (error: any) {
      onError(error.message || 'Failed to download PDF')
    } finally {
      setIsGeneratingPdf(prev => ({ ...prev, [cvId]: false }))
    }
  }

  const handleEdit = (cvId: string) => {
    window.location.hash = `#edit/${cvId}`
  }

  return (
    <div className="bg-white shadow rounded-lg dark:bg-gray-900 dark:border dark:border-gray-800">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">My CVs ({total})</h2>
          <div className="flex space-x-2">
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && handleSearch()}
              placeholder="Search CVs..."
              className="px-4 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-900 shadow-sm text-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder:text-gray-500 dark:focus:border-blue-400 dark:focus:ring-blue-400"
            />
            <button
              onClick={handleSearch}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:hover:bg-blue-500"
            >
              Search
            </button>
          </div>
        </div>
      </div>

      <div className="p-6">
        {loading ? (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">Loading CVs...</p>
          </div>
        ) : cvs.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">No CVs found.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {cvs.map(cv => (
              <div
                key={cv.cv_id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-gray-800/60"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                      {(() => {
                        const name = cv.person_name || 'Unnamed CV'
                        const parts: string[] = []
                        if (cv.target_role) {
                          parts.push(cv.target_role)
                        }
                        if (cv.target_company) {
                          parts.push(`@ ${cv.target_company}`)
                        }
                        if (parts.length > 0) {
                          return `${name} - ${parts.join(' ')}`
                        }
                        return name
                      })()}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1 dark:text-gray-400">
                      Created: {new Date(cv.created_at).toLocaleDateString()}
                    </p>
                    <p className="text-xs text-gray-400 mt-1 dark:text-gray-500">ID: {cv.cv_id}</p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(cv.cv_id)}
                      className="px-3 py-1 text-sm font-medium text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300"
                    >
                      Edit
                    </button>
                    {cv.filename ? (
                      <button
                        onClick={() => handleDownload(cv.filename)}
                        className="px-3 py-1 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                      >
                        Download
                      </button>
                    ) : (
                      <button
                        onClick={() => handleGenerateFile(cv.cv_id)}
                        className="px-3 py-1 text-sm font-medium text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300"
                      >
                        Generate File
                      </button>
                    )}
                    <button
                      onClick={() => handleDownloadPdf(cv.cv_id)}
                      disabled={isGeneratingPdf[cv.cv_id]}
                      className="px-3 py-1 text-sm font-medium text-orange-600 hover:text-orange-700 dark:text-orange-400 dark:hover:text-orange-300 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isGeneratingPdf[cv.cv_id] ? 'Generating...' : 'Download PDF'}
                    </button>
                    <button
                      onClick={() => handleDelete(cv.cv_id)}
                      className="px-3 py-1 text-sm font-medium text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
