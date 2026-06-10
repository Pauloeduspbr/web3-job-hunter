import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api.js'

export default function InputsPanel({ notify, refresh }) {
  const [links, setLinks] = useState('')
  const [uploaded, setUploaded] = useState([])
  const fileRef = useRef(null)

  const loadFiles = useCallback(async () => {
    try { setUploaded(await api.resumeFiles()) } catch { /* backend offline */ }
  }, [])

  useEffect(() => { loadFiles() }, [loadFiles])

  const submitLinks = async () => {
    const urls = links.split('\n').map((l) => l.trim()).filter(Boolean)
    if (!urls.length) return
    try {
      const res = await api.addLinks(urls)
      notify(`${res.added} link(s) adicionados — rode "Scrape links"`)
      setLinks('')
      await refresh()
    } catch (e) {
      notify(`Falha ao adicionar links: ${e.message}`, true)
    }
  }

  const upload = async (file) => {
    if (!file) return
    try {
      const res = await api.uploadResume(file)
      notify(`Currículo salvo: ${res.saved} (${(res.size / 1024).toFixed(0)} KB)`)
      await Promise.all([loadFiles(), refresh()])
    } catch (e) {
      notify(`Upload falhou: ${e.message}`, true)
    }
  }

  return (
    <section className="panel">
      <h2>Entradas</h2>

      <label className="label">📤 Upload de currículo (.pdf .md .docx .txt)</label>
      <div
        className="dropzone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => { e.preventDefault(); upload(e.dataTransfer.files[0]) }}
        onClick={() => fileRef.current?.click()}
      >
        Arraste o arquivo aqui ou clique para escolher
        <input
          ref={fileRef} type="file" hidden accept=".pdf,.md,.docx,.txt"
          onChange={(e) => { upload(e.target.files[0]); e.target.value = '' }}
        />
      </div>
      {uploaded.length > 0 && (
        <ul className="files">
          {uploaded.map((f) => (
            <li key={f.name}>
              <span className="fname">{f.name}</span>
              <span className="actions">{(f.size / 1024).toFixed(0)} KB</span>
            </li>
          ))}
        </ul>
      )}

      <label className="label">🔗 Links de vagas (1 por linha)</label>
      <textarea
        rows={4}
        value={links}
        placeholder="https://www.linkedin.com/jobs/view/1234567890/"
        onChange={(e) => setLinks(e.target.value)}
      />
      <button onClick={submitLinks}>Adicionar links</button>
    </section>
  )
}
