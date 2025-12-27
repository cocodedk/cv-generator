import { useEffect, useRef } from 'react'
import { UseFormHandleSubmit } from 'react-hook-form'
import { CVData } from '../../types/cv'

interface UseKeyboardShortcutProps {
  handleSubmit: UseFormHandleSubmit<CVData>
  onSubmit: (data: CVData) => void | Promise<void>
  isLoadingCv: boolean
  isSubmitting: boolean
  showAiModal: boolean
  showProfileLoader: boolean
}

/**
 * Hook to handle Ctrl+S / Cmd+S keyboard shortcut for form submission.
 * Uses refs to avoid stale closures and ensure the event listener stays attached.
 */
export function useKeyboardShortcut({
  handleSubmit,
  onSubmit,
  isLoadingCv,
  isSubmitting,
  showAiModal,
  showProfileLoader,
}: UseKeyboardShortcutProps) {
  // Use refs to store stable references for keyboard handler
  const handleSubmitRef = useRef(handleSubmit)
  const onSubmitRef = useRef(onSubmit)
  const isLoadingCvRef = useRef(isLoadingCv)
  const isSubmittingRef = useRef(isSubmitting)
  const showAiModalRef = useRef(showAiModal)
  const showProfileLoaderRef = useRef(showProfileLoader)

  // Update refs immediately and when values change
  // Initialize refs with current values on first render
  handleSubmitRef.current = handleSubmit
  onSubmitRef.current = onSubmit
  isLoadingCvRef.current = isLoadingCv
  isSubmittingRef.current = isSubmitting
  showAiModalRef.current = showAiModal
  showProfileLoaderRef.current = showProfileLoader

  // Also update refs in useEffect to catch any changes
  useEffect(() => {
    handleSubmitRef.current = handleSubmit
    onSubmitRef.current = onSubmit
    isLoadingCvRef.current = isLoadingCv
    isSubmittingRef.current = isSubmitting
    showAiModalRef.current = showAiModal
    showProfileLoaderRef.current = showProfileLoader
  }, [handleSubmit, onSubmit, isLoadingCv, isSubmitting, showAiModal, showProfileLoader])

  // Keyboard shortcut handler for Ctrl+S / Cmd+S
  useEffect(() => {
    console.debug('[Ctrl+S] Keyboard shortcut handler attached')
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check for Ctrl+S (Windows/Linux) or Cmd+S (Mac)
      if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) {
        e.preventDefault() // Prevent browser save dialog
        e.stopPropagation() // Prevent event from bubbling

        // Use refs to get current values (avoid stale closures)
        if (isLoadingCvRef.current) {
          console.debug('[Ctrl+S] Blocked: Form is loading CV data')
          return
        }

        if (isSubmittingRef.current) {
          console.debug('[Ctrl+S] Blocked: Form is already submitting')
          return
        }

        if (showAiModalRef.current) {
          console.debug('[Ctrl+S] Blocked: AI modal is open')
          return
        }

        if (showProfileLoaderRef.current) {
          console.debug('[Ctrl+S] Blocked: Profile loader modal is open')
          return
        }

        // Trigger form submission using refs to ensure we use latest functions
        // Note: Ctrl+S works from anywhere, including while typing in fields
        console.debug('[Ctrl+S] Triggering form submission')
        handleSubmitRef.current(onSubmitRef.current)()
      }
    }

    document.addEventListener('keydown', handleKeyDown, true) // Use capture phase
    return () => {
      document.removeEventListener('keydown', handleKeyDown, true)
    }
  }, []) // Empty deps - refs are updated separately, handler never needs to re-run
}
