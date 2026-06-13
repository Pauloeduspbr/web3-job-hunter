import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from './api.js'
import Icon from './components/Icon.jsx'
import StatCards from './components/StatCards.jsx'
import InputsPanel from './components/InputsPanel.jsx'
import PipelinePanel from './components/PipelinePanel.jsx'
import JobsBoard from './components/JobsBoard.jsx'
import OutputsPanel from './components/OutputsPanel.jsx'

export default function App() {
  const [status, setStatus] = useState(null)
  const [jobs, setJobs] = useState([])
  const [resumes, setResumes] = useState([])
  const [briefs, setBriefs] = useState([])
  const [toast, setToast] = useState(null)
  const toastTimer = useRef(null)

  const notify = useCallback((msg, isError = false) => {
    setToast({ msg, isError })
    clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setToast(null), 6000)
  }, [])

  const refresh = useCallback(async () => {
    try {
      const [s, j, r, b] = await Promise.all([api.status(), api.jobs(), api.resumes(), api.briefs()])
      setStatus(s); setJobs(j); setResumes(r); setBriefs(b)
    } catch (e) {
      notify(`Erro ao carregar: ${e.message}`, true)
    }
  }, [notify])

  useEffect(() => { refresh() }, [refresh])

  const apiMode = status?.llm_mode === 'api'

  return (
    <div className="app-shell">
      <header className="appbar">
        <div className="appbar-in">
          <div className="brand">
            <div className="brand-mark"><Icon name="target" size={22} /></div>
            <div className="brand-text">
              <h1>Web3 Job Hunter</h1>
              <p><span className="who">Paulo Eduardo</span> · Senior Data Engineer · CV otimizado por vaga</p>
            </div>
          </div>
          <div className="appbar-spacer" />
          <div className="appbar-pills">
            <span className="pill brand-pill"><Icon name="briefcase" size={13} /> <b>{status?.scored_jobs ?? 0}</b> vagas</span>
            <span className="pill"><Icon name="file" size={13} /> <b>{status?.resumes ?? 0}</b> CVs</span>
            <span className={`pill ${apiMode ? 'api' : 'manual'}`}>
              <span className="dot" /> {apiMode ? 'Claude API' : 'Claude Code'}
            </span>
          </div>
        </div>
      </header>

      <main>
        <div className="container">
          <StatCards jobs={jobs} status={status} />

          <div className="section-head">
            <h2>Workspace</h2>
            <span className="sub">Suba o currículo, cole links e rode o funil de busca</span>
          </div>
          <div className="workspace">
            <InputsPanel notify={notify} refresh={refresh} status={status} />
            <PipelinePanel notify={notify} refresh={refresh} running={status?.running_stages || []} />
          </div>

          <JobsBoard jobs={jobs} notify={notify} refresh={refresh} />

          <OutputsPanel resumes={resumes} briefs={briefs} notify={notify} />
        </div>
      </main>

      {toast && (
        <div className={`toast ${toast.isError ? 'error' : 'ok'}`}>
          <span className="t-ico"><Icon name={toast.isError ? 'zap' : 'check'} size={16} /></span>
          <span>{toast.msg}</span>
        </div>
      )}
    </div>
  )
}
