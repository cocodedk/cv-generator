import { useState, useCallback, useEffect } from 'react'
import CVForm from './components/CVForm'
import CVList from './components/CVList'
import ProfileList from './components/ProfileList'
import ProfileManager from './components/ProfileManager'
import Introduction from './components/Introduction'
import Navigation from './components/Navigation'
import NotificationModal from './components/NotificationModal'
import Footer from './components/Footer'
import { useHashRouting } from './app_helpers/useHashRouting'
import { useTheme } from './app_helpers/useTheme'
import { useMessage } from './app_helpers/useMessage'
import { BRANDING } from './app_helpers/branding'
import './index.css'

function App() {
  const { viewMode, cvId } = useHashRouting()
  const { isDark, setIsDark } = useTheme()
  const { message, showMessage, clearMessage } = useMessage()
  const [, setLoading] = useState(false)

  useEffect(() => {
    document.title = `${BRANDING.appName} — ${BRANDING.ownerName} (${BRANDING.companyName})`
  }, [])

  const handleSuccess = useCallback(
    (message: string) => showMessage('success', message),
    [showMessage]
  )

  const handleError = useCallback(
    (message: string | string[]) => showMessage('error', message),
    [showMessage]
  )

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Navigation
        viewMode={viewMode}
        isDark={isDark}
        onThemeToggle={() => setIsDark(current => !current)}
      />

      <NotificationModal message={message} onClose={clearMessage} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {viewMode === 'introduction' ? (
          <Introduction onError={handleError} />
        ) : viewMode === 'form' || viewMode === 'edit' ? (
          <CVForm
            onSuccess={handleSuccess}
            onError={handleError}
            setLoading={setLoading}
            cvId={cvId}
          />
        ) : viewMode === 'list' ? (
          <CVList onError={handleError} />
        ) : viewMode === 'profile-list' ? (
          <ProfileList onError={handleError} />
        ) : (
          <ProfileManager onSuccess={handleSuccess} onError={handleError} setLoading={setLoading} />
        )}
      </main>
      <Footer />
    </div>
  )
}

export default App
