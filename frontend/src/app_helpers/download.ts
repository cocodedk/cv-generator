export const buildDownloadUrl = (filename: string) => {
  return `/api/download-docx/${filename}?t=${Date.now()}`
}

export const openDownload = (filename: string) => {
  window.open(buildDownloadUrl(filename), '_blank')
}
