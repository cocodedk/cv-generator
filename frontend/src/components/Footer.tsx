import { BRANDING } from '../app_helpers/branding'

export default function Footer() {
  return (
    <footer className="border-t border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center justify-between gap-4">
          <span>
            © {new Date().getFullYear()} {BRANDING.ownerName}
          </span>
          <a
            href={BRANDING.companyUrl}
            target="_blank"
            rel="noreferrer"
            className="hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
          >
            {BRANDING.companyName}
          </a>
        </div>
      </div>
    </footer>
  )
}
