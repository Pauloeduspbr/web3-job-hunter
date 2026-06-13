import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api.js'
import Icon from './Icon.jsx'

export default function InputsPanel({ notify, refresh, status }) {
  const [links, setLinks] = useState('')
  const [uploaded, setUploaded] = useState([])
  const [drag, setDrag] = useState(false)
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
      notify(`${res.added} link(s) adicionados — rode "Scrape links" no pipeline`)
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
    <section className="card card-pad">
      <div className="card-head">
        <div className="ico"><Icon name="upload" size={15} /></div>
        <span className="ttl">Entradas</span>
        {status?.base_resume && <span className="sub">base: {status.base_resume}</span>}
      </div>

      <label className="label">Currículo base (.pdf · .md · .docx · .txt)</label>
      <div
        className={`dropzone ${drag ? 'drag' : ''}`}
        role="button"
        tabIndex={0}
        aria-label="Enviar currículo base"
        onDragOver={(e) => { e.preventDefault(); setDrag(true) }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); upload(e.dataTransfer.files[0]) }}
        onClick={() => fileRef.current?.click()}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileRef.current?.click() } }}
      >
        <span className="dz-ico"><Icon name="upload" size={22} /></span>
        <strong>Arraste aqui</strong> ou clique para escolher
        <input
          ref={fileRef} type="file" hidden accept=".pdf,.md,.docx,.txt"
          onChange={(e) => { upload(e.target.files[0]); e.target.value = '' }}
        />
      </div>
      {uploaded.length > 0 && (
        <ul className="file-list">
          {uploaded.map((f) => (
            <li className="file-row" key={f.name}>
              <span className="fname"><span className="fdoc"><Icon name="file" size={13} /></span>{f.name}</span>
              <span className="meta">{(f.size / 1024).toFixed(0)} KB</span>
            </li>
          ))}
        </ul>
      )}

      <div className="field" style={{ marginTop: 18 }}>
        <label className="label">Links de vagas (1 por linha)</label>
        <textarea
          className="textarea" rows={4} value={links}
          placeholder="https://www.linkedin.com/jobs/view/1234567890/"
          onChange={(e) => setLinks(e.target.value)}
        />
        <button className="btn btn-soft btn-block" style={{ marginTop: 10 }} onClick={submitLinks} disabled={!links.trim()}>
          <Icon name="plus" size={15} /> Adicionar links
        </button>
      </div>
    </section>
  )
}
