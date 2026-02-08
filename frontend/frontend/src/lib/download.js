import api from './api'

function _getFilenameFromDisposition(disposition) {
  if (!disposition) return ''
  // Content-Disposition: attachment; filename="..."
  const m = /filename\*=UTF-8''([^;]+)|filename="([^"]+)"|filename=([^;]+)/i.exec(disposition)
  const raw = (m && (m[1] || m[2] || m[3])) ? (m[1] || m[2] || m[3]) : ''
  try {
    return decodeURIComponent(raw).replace(/^"|"$/g, '')
  } catch {
    return String(raw).replace(/^"|"$/g, '')
  }
}

export async function downloadFile(url, fallbackName = 'file') {
  const res = await api.get(url, { responseType: 'blob' })
  const blob = res.data
  const disposition = res.headers?.['content-disposition']
  const filename = _getFilenameFromDisposition(disposition) || fallbackName

  const objectUrl = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = objectUrl
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(objectUrl)
}
