import { useState } from 'react'
import { useForm } from 'react-hook-form'
import CVForm from './components/CVForm'
import CVList from './components/CVList'
import { CVData } from './types/cv'
import './index.css'

type ViewMode = 'form' | 'list'

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('form')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 5000)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-gray-900">CV Generator</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setViewMode('form')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  viewMode === 'form'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Create CV
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  viewMode === 'list'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                My CVs
              </button>
            </div>
          </div>
        </div>
      </nav>

      {message && (
        <div className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4`}>
          <div
            className={`rounded-md p-4 ${
              message.type === 'success'
                ? 'bg-green-50 text-green-800 border border-green-200'
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}
          >
            {message.text}
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {viewMode === 'form' ? (
          <CVForm
            onSuccess={(message) => showMessage('success', message)}
            onError={(message) => showMessage('error', message)}
            setLoading={setLoading}
          />
        ) : (
          <CVList
            onError={(message) => showMessage('error', message)}
          />
        )}
      </main>
    </div>
  )
}

export default App
