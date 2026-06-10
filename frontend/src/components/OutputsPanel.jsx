import { api } from '../api.js'

export default function OutputsPanel({ resumes, briefs, notify }) {
  const download = async (url, filename) => {
    try {
      await api.downloadFile(url, filename)
    } catch (e) {
      notify(`Download falhou: ${e.message}`, true)
    }
  }

  return (
    <div className="row">
      <section className="panel">
        <h2>📥 CVs gerados ({resumes.length})</h2>
        {!resumes.length && <p className="empty">Nenhum CV gerado ainda.</p>}
        <ul className="files">
          {resumes.map((r) => (
            <li key={r.name}>
              <span className="fname">{r.name}</span>
              <span className="actions">
                <a href="#md" onClick={(e) => { e.preventDefault(); download(api.downloadResumeUrl(r.name, 'md'), r.name) }}>.md</a>
                <a href="#docx" onClick={(e) => { e.preventDefault(); download(api.downloadResumeUrl(r.name, 'docx'), r.name.replace(/\.md$/, '.docx')) }}>.docx</a>
                <a href="#pdf" onClick={(e) => { e.preventDefault(); download(api.downloadResumeUrl(r.name, 'pdf'), r.name.replace(/\.md$/, '.pdf')) }}>.pdf</a>
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel">
        <h2>📋 Briefings ({briefs.length})</h2>
        {!briefs.length && <p className="empty">Nenhum briefing ainda.</p>}
        <ul className="files">
          {briefs.map((b) => (
            <li key={b.name}>
              <span className="fname">{b.name}</span>
              <span className="actions">
                <a href="#md" onClick={(e) => { e.preventDefault(); download(api.downloadBriefUrl(b.name), b.name) }}>.md</a>
              </span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
