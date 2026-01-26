import { render } from '@testing-library/react'
import ProfileManager from '../../../components/ProfileManager'

export interface ProfileManagerProps {
  onSuccess: (message: string) => void
  onError: (message: string) => void
  setLoading: (loading: boolean) => void
}

export const renderProfileManager = (props: ProfileManagerProps) => {
  const result = render(
    <ProfileManager
      onSuccess={props.onSuccess}
      onError={props.onError}
      setLoading={props.setLoading}
    />
  )
  return {
    ...result,
  }
}
