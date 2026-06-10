import { useMemo, useState } from 'react'
import { api } from '../api.js'

function ScoreBadge({ score }) {
  const cls = score >= 80 ? 'score high' : score >= 60 ? 'score mid' : 'score low'
  return <span className={cls}>{score.toFixed(1)}</span>
}

const WORKPLACE_LABEL = {
  remote: '🏠 Remote',
  hybrid: '🏢 Híbrida',
  onsite: '🏬 Presencial',
  unknown: '❔ Detalhar',
}

function WorkplaceBadge({ value }) {
  return <span className={`wp ${value}`}>{WORKPLACE_LABEL[value] || value}</span>
}

export default function JobTable({ jobs, notify, refresh }) {
  const [busy, setBusy] = useState(null)
  const [enriching, setEnriching] = useState(false)
  const [wpFilter, setWpFilter] = useState('all')
  const [stFilter, setStFilter] = useState('all')
  const [minScore, setMinScore] = useState(0)
  const [query, setQuery] = useState('')

  const filtered = useMemo(() => jobs.filter((j) => {
    if (wpFilter !== 'all' && (j.workplace || 'unknown') !== wpFilter) return false
    const st = j.status || 'new'
    if (stFilter === 'pending' && st === 'applied') return false
    if (stFilter !== 'all' && stFilter !== 'pending' && st !== stFilter) return false
    if (j.score < minScore) return false
    if (query) {
      const text = `${j.title} ${j.company} ${j.location}`.toLowerCase()
      if (!text.includes(query.toLowerCase())) return false
    }
    return true
  }), [jobs, wpFilter, stFilter, minScore, query])

  // listing-only LinkedIn jobs (numeric id, no description) can be detail-scraped
  const enrichable = filtered.filter((j) => j.needs_detail && /^\d+$/.test(String(j.job_id)))
  const appliedCount = jobs.filter((j) => j.status === 'applied').length

  const setStatus = async (job, status) => {
    // toggle: clicking the active status clears it back to "new"
    const next = (job.status === status) ? 'new' : status
    try {
      await api.setJobStatus(job.job_id, next)
      await refresh()
    } catch (e) {
      notify(`Falha ao salvar status: ${e.message}`, true)
    }
  }

  const markViewedOnOpen = (job) => {
    // opening the posting implies "viewed" — never downgrade an "applied"
    if ((job.status || 'new') === 'new') {
      api.setJobStatus(job.job_id, 'viewed').then(refresh).catch(() => {})
    }
  }

  const generate = async (jobId) => {
    setBusy(jobId)
    try {
      const res = await api.generateCv(jobId)
      notify(res.message || `Brief: ${res.brief}${res.resume ? ` | CV: ${res.resume}` : ''}`)
      await refresh()
    } catch (e) {
      notify(`Geração falhou: ${e.message}`, true)
    } finally {
      setBusy(null)
    }
  }

  const enrich = async (jobIds) => {
    setEnriching(true)
    try {
      const res = await api.enrich(jobIds)
      notify(`${res.enriched} vaga(s) enriquecidas com descrição + modalidade — re-pontuadas`)
      await refresh()
    } catch (e) {
      notify(`Enriquecimento falhou: ${e.message}`, true)
    } finally {
      setEnriching(false)
    }
  }

  if (!jobs.length) {
    return <section className="panel"><h2>Vagas</h2><p className="empty">Nenhuma vaga pontuada ainda — rode o pipeline.</p></section>
  }

  return (
    <section className="panel">
      <h2>Vagas pontuadas ({filtered.length} de {jobs.length}{appliedCount ? ` · ✅ ${appliedCount} aplicadas` : ''})</h2>

      <div className="filters">
        <select value={stFilter} onChange={(e) => setStFilter(e.target.value)}>
          <option value="all">Status: todos</option>
          <option value="pending">⏳ Não aplicadas</option>
          <option value="new">🆕 Novas</option>
          <option value="viewed">👁 Vistas</option>
          <option value="applied">✅ Aplicadas</option>
        </select>
        <select value={wpFilter} onChange={(e) => setWpFilter(e.target.value)}>
          <option value="all">Modalidade: todas</option>
          <option value="remote">🏠 Remote</option>
          <option value="hybrid">🏢 Híbrida</option>
          <option value="onsite">🏬 Presencial</option>
          <option value="unknown">❔ Sem detalhe</option>
        </select>
        <label>
          Score ≥ <input type="number" min="0" max="100" value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value) || 0)} style={{ width: 64 }} />
        </label>
        <input placeholder="filtrar por título/empresa/local…" value={query}
          onChange={(e) => setQuery(e.target.value)} style={{ flex: 1, minWidth: 180 }} />
        {enrichable.length > 0 && (
          <button className="small" disabled={enriching}
            onClick={() => enrich(enrichable.map((j) => j.job_id))}>
            {enriching ? '⏳ enriquecendo…' : `🔍 Detalhar ${enrichable.length} filtradas (~$${(enrichable.length * 0.005).toFixed(2)})`}
          </button>
        )}
      </div>

      <table>
        <thead>
          <tr><th>Status</th><th>Score</th><th>Vaga</th><th>Empresa</th><th>Modo</th><th>Local</th><th>Gaps</th><th>Ações</th></tr>
        </thead>
        <tbody>
          {filtered.map((j) => {
            const st = j.status || 'new'
            return (
              <tr key={j.job_id} className={`${j.score >= 60 ? '' : 'dim'} st-${st}`}>
                <td className="st-cell">
                  <button
                    className={`flag ${st === 'viewed' ? 'on' : ''}`}
                    title={st === 'viewed' ? 'Marcada como vista — clique para desmarcar' : 'Marcar como vista'}
                    onClick={() => setStatus(j, 'viewed')}
                  >👁</button>
                  <button
                    className={`flag ${st === 'applied' ? 'on applied' : ''}`}
                    title={st === 'applied' ? 'CV enviado — clique para desmarcar' : 'Marcar: já enviei meu currículo'}
                    onClick={() => setStatus(j, 'applied')}
                  >✅</button>
                </td>
                <td><ScoreBadge score={j.score} /></td>
                <td>
                  {j.url
                    ? <a href={j.url} target="_blank" rel="noreferrer" onClick={() => markViewedOnOpen(j)}>{j.title}</a>
                    : j.title}
                  {st === 'applied' && <span className="applied-tag">CV enviado{j.status_updated_at ? ` em ${new Date(j.status_updated_at).toLocaleDateString('pt-BR')}` : ''}</span>}
                </td>
                <td>{j.company}</td>
                <td><WorkplaceBadge value={j.workplace || 'unknown'} /></td>
                <td className="loc">{j.location || '—'}</td>
                <td className="gaps">{(j.gap_skills || []).join(', ') || '—'}</td>
                <td className="row-actions">
                  {j.needs_detail && /^\d+$/.test(String(j.job_id)) && (
                    <button className="small ghost" disabled={enriching}
                      title="Busca descrição completa + modalidade ($0.005)"
                      onClick={() => enrich([j.job_id])}>🔍</button>
                  )}
                  <button className="small" disabled={busy !== null} onClick={() => generate(j.job_id)}>
                    {busy === j.job_id ? '⏳' : '📄 Gerar CV'}
                  </button>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </section>
  )
}
