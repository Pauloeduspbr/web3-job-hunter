import { api } from '../api.js'
import Icon from './Icon.jsx'

function FileList({ items, empty, renderActions }) {
  if (!items.length) {
    return (
      <div className="empty" style={{ padding: '26px 16px' }}>
        <span className="e-ico"><Icon name="file" size={28} /></span>
        <span className="small">{empty}</span>
      </div>
    )
  }
  return (
    <ul className="file-list">
      {items.map((f) => (
        <li className="file-row" key={f.name}>
          <span className="fname"><span className="fdoc"><Icon name="file" size={13} /></span>{f.name}</span>
          <span className="dl-chips">{renderActions(f)}</span>
        </li>
      ))}
    </ul>
  )
}

export default function OutputsPanel({ resumes, briefs, notify }) {
  const download = async (url, filename) => {
    try { await api.downloadFile(url, filename) }
    catch (e) { notify(`Download falhou: ${e.message}`, true) }
  }

  return (
    <section>
      <div className="section-head">
        <h2>Saídas</h2>
        <span className="sub">CVs tailorizados e briefings de tailoring</span>
      </div>

      <div className="workspace">
        <div className="card card-pad">
          <div className="card-head">
            <div className="ico"><Icon name="sparkles" size={15} /></div>
            <span className="ttl">CVs gerados</span>
            <span className="sub">{resumes.length}</span>
          </div>
          <FileList
            items={resumes}
            empty="Nenhum CV gerado ainda — clique “Gerar CV” numa vaga."
            renderActions={(r) => (
              <>
                <a className="dl-chip" href="#md" onClick={(e) => { e.preventDefault(); download(api.downloadResumeUrl(r.name, 'md'), r.name) }}>MD</a>
                <a className="dl-chip" href="#docx" onClick={(e) => { e.preventDefault(); download(api.downloadResumeUrl(r.name, 'docx'), r.name.replace(/\.md$/, '.docx')) }}>DOCX</a>
                <a className="dl-chip" href="#pdf" onClick={(e) => { e.preventDefault(); download(api.downloadResumeUrl(r.name, 'pdf'), r.name.replace(/\.md$/, '.pdf')) }}>PDF</a>
              </>
            )}
          />
        </div>

        <div className="card card-pad">
          <div className="card-head">
            <div className="ico"><Icon name="list" size={15} /></div>
            <span className="ttl">Briefings</span>
            <span className="sub">{briefs.length}</span>
          </div>
          <FileList
            items={briefs}
            empty="Nenhum briefing ainda."
            renderActions={(b) => (
              <a className="dl-chip" href="#md" onClick={(e) => { e.preventDefault(); download(api.downloadBriefUrl(b.name), b.name) }}>
                <Icon name="download" size={12} /> MD
              </a>
            )}
          />
        </div>
      </div>
    </section>
  )
}
