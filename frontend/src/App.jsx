import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from './api.js'
import PipelinePanel from './components/PipelinePanel.jsx'
import InputsPanel from './components/InputsPanel.jsx'
import JobTable from './components/JobTable.jsx'
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

  return (
    <div className="app">
      <header>
        <h1>🎯 Web3 Job Hunter</h1>
        {status && (
          <div className="stats">
            <span>{status.scored_jobs} vagas pontuadas</span>
            <span>{status.resumes} CVs gerados</span>
            <span className={status.llm_mode === 'api' ? 'badge api' : 'badge manual'}>
              LLM: {status.llm_mode === 'api' ? 'Claude API' : 'Claude Code (manual)'}
            </span>
          </div>
        )}
      </header>

      {toast && <div className={toast.isError ? 'toast error' : 'toast'}>{toast.msg}</div>}

      <main>
        <div className="row">
          <InputsPanel notify={notify} refresh={refresh} />
          <PipelinePanel notify={notify} refresh={refresh} />
        </div>
        <JobTable jobs={jobs} notify={notify} refresh={refresh} />
        <OutputsPanel resumes={resumes} briefs={briefs} notify={notify} />
      </main>
    </div>
  )
}
