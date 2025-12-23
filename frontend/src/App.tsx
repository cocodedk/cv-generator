import { useState } from 'react'
import CVForm from './components/CVForm'
import CVList from './components/CVList'
import ProfileManager from './components/ProfileManager'
import Navigation from './components/Navigation'
import MessageDisplay from './components/MessageDisplay'
import { useHashRouting } from './app_helpers/useHashRouting'
import { useTheme } from './app_helpers/useTheme'
import { useMessage } from './app_helpers/useMessage'
import './index.css'

function App() {
  const { viewMode, cvId } = useHashRouting()
  const { isDark, setIsDark } = useTheme()
  const { message, showMessage } = useMessage()
  const [_loading, setLoading] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Navigation
        viewMode={viewMode}
        isDark={isDark}
        onThemeToggle={() => setIsDark(current => !current)}
      />

      <MessageDisplay message={message} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {viewMode === 'form' || viewMode === 'edit' ? (
          <CVForm
            onSuccess={message => showMessage('success', message)}
            onError={message => showMessage('error', message)}
            setLoading={setLoading}
            cvId={cvId}
          />
        ) : viewMode === 'list' ? (
          <CVList onError={message => showMessage('error', message)} />
        ) : (
          <ProfileManager
            onSuccess={message => showMessage('success', message)}
            onError={message => showMessage('error', message)}
            setLoading={setLoading}
          />
        )}
      </main>
    </div>
  )
}

export default App
