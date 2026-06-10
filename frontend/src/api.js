const json = async (r) => {
  if (!r.ok) {
    // error body may be JSON ({detail: string|array}), plain text or HTML
    const raw = await r.text()
    let detail
    try {
      detail = JSON.parse(raw).detail
    } catch {
      detail = raw
    }
    const msg = typeof detail === 'string' ? detail : JSON.stringify(detail)
    throw new Error(msg || r.statusText)
  }
  return r.json()
}

export const api = {
  status: () => fetch('/api/status').then(json),
  jobs: () => fetch('/api/jobs').then(json),
  briefs: () => fetch('/api/briefs').then(json),
  resumes: () => fetch('/api/resumes').then(json),
  resumeFiles: () => fetch('/api/resume/files').then(json),

  runStage: (stage, body) =>
    fetch(`/api/pipeline/${stage}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    }).then(json),

  addLinks: (urls) =>
    fetch('/api/links', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ urls }),
    }).then(json),

  uploadResume: (file) => {
    const fd = new FormData()
    fd.append('file', file)
    return fetch('/api/resume/upload', { method: 'POST', body: fd }).then(json)
  },

  setJobStatus: (jobId, status) =>
    fetch('/api/jobs/status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: String(jobId), status }),
    }).then(json),

  enrich: (jobIds) =>
    fetch('/api/jobs/enrich', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_ids: jobIds.map(String) }),
    }).then(json),

  // identity contract: job_id, never positional index (list reorders on re-score)
  generateCv: (jobId) =>
    fetch('/api/cv/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: String(jobId) }),
    }).then(json),

  downloadResumeUrl: (name, fmt) => `/api/download/resume/${encodeURIComponent(name)}?fmt=${fmt}`,
  downloadBriefUrl: (name) => `/api/download/brief/${encodeURIComponent(name)}`,

  // checked download: surfaces conversion/404 errors instead of saving an error body
  downloadFile: async (url, filename) => {
    const r = await fetch(url)
    if (!r.ok) {
      const raw = await r.text()
      let detail
      try { detail = JSON.parse(raw).detail } catch { detail = r.statusText }
      throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    }
    const blob = await r.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = filename
    a.click()
    URL.revokeObjectURL(a.href)
  },
}
