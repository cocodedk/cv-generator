/**
 * Component that displays a loading state while CV data is being loaded.
 */
export default function CVFormLoading() {
  return (
    <div className="bg-white shadow rounded-lg dark:bg-gray-900 dark:border dark:border-gray-800 p-6">
      <p className="text-gray-600 dark:text-gray-400">Loading CV data...</p>
    </div>
  )
}
