import { useState } from 'react'
import { api } from '../api.js'

const STAGES = [
  { id: 'scrape', label: 'Scrape links (Apify)', hint: '~$0.005/vaga · pontua automático' },
  { id: 'boards', label: 'Boards grátis', hint: 'Greenhouse/Ashby/Lever/RSS — $0 · pontua automático' },
  { id: 'score', label: 'Re-pontuar vagas', hint: 'match vs perfil — $0' },
]

export default function PipelinePanel({ notify, refresh }) {
  const [running, setRunning] = useState(null)
  const [search, setSearch] = useState({ keywords: 'data engineer', location: 'United States', max_jobs: 50 })

  const run = async (stage, body) => {
    setRunning(stage)
    try {
      const res = await api.runStage(stage, body)
      notify(`${stage}: ${JSON.stringify(res)}`)
      await refresh()
    } catch (e) {
      notify(`${stage} falhou: ${e.message}`, true)
    } finally {
      setRunning(null)
    }
  }

  return (
    <section className="panel">
      <h2>Pipeline</h2>
      {STAGES.map((s) => (
        <div className="stage" key={s.id}>
          <button disabled={!!running} onClick={() => run(s.id)}>
            {running === s.id ? '⏳ rodando…' : s.label}
          </button>
          <small>{s.hint}</small>
        </div>
      ))}
      <div className="stage search">
        <input value={search.keywords} placeholder="keywords"
          onChange={(e) => setSearch({ ...search, keywords: e.target.value })} />
        <input value={search.location} placeholder="location"
          onChange={(e) => setSearch({ ...search, location: e.target.value })} />
        <button disabled={!!running} onClick={() => run('search', search)}>
          {running === 'search' ? '⏳ rodando…' : 'Buscar LinkedIn (actor próprio)'}
        </button>
        <small>compute units · pontua automático · a busca traz só a listagem — use 🔍 Detalhar na tabela para descrição + modalidade remote/híbrida</small>
      </div>
    </section>
  )
}
