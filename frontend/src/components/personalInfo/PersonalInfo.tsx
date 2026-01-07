import { UseFormRegister, FieldErrors, Control } from 'react-hook-form'
import { CVData } from '../../types/cv'
import BasicFields from './BasicFields'
import AddressFields from './AddressFields'
import PhotoUpload from './PhotoUpload'
import SummaryField from './SummaryField'

interface PersonalInfoProps {
  register: UseFormRegister<CVData>
  errors: FieldErrors<CVData>
  control: Control<CVData>
  showAiAssist?: boolean
}

export default function PersonalInfo({
  register,
  errors,
  control,
  showAiAssist,
}: PersonalInfoProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
        Personal Information
      </h3>

      <BasicFields register={register} errors={errors} />

      <AddressFields register={register} />

      <PhotoUpload control={control} />

      <SummaryField control={control} showAiAssist={showAiAssist} />
    </div>
  )
}
