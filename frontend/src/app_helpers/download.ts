export const buildDownloadUrl = (filename: string) => {
  // Normalize filename: strip leading "../" or "/" to prevent path traversal
  const normalized = filename.replace(/^\.\.\/+/, '').replace(/^\/+/, '')
  // URL-encode the filename to handle special characters
  const encoded = encodeURIComponent(normalized)
  return `/api/download-docx/${encoded}?t=${Date.now()}`
}

export const openDownload = (filename: string) => {
  window.open(buildDownloadUrl(filename), '_blank')
}
