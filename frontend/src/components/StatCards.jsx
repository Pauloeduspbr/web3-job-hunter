import { useMemo } from 'react'
import Icon from './Icon.jsx'

// KPI overview — all derived from real data (jobs + /api/status). No invented numbers.
export default function StatCards({ jobs, status }) {
  const k = useMemo(() => {
    const total = jobs.length
    const strong = jobs.filter((j) => (j.score || 0) >= 80).length
    const remote = jobs.filter((j) => j.workplace === 'remote').length
    const applied = jobs.filter((j) => j.status === 'applied').length
    const avg = total ? jobs.reduce((s, j) => s + (j.score || 0), 0) / total : 0
    return { total, strong, remote, applied, avg }
  }, [jobs])

  const cards = [
    { ico: 'list', cls: 'i-brand', val: k.total, label: 'Vagas pontuadas', foot: k.total ? `score médio ${k.avg.toFixed(0)}` : 'rode o pipeline' },
    { ico: 'trophy', cls: 'i-ok', val: k.strong, label: 'Matches fortes', foot: 'score ≥ 80' },
    { ico: 'home', cls: 'i-info', val: k.remote, label: 'Remotas', foot: 'modalidade remote' },
    { ico: 'check', cls: 'i-violet', val: k.applied, label: 'Aplicadas', foot: 'CV enviado' },
    { ico: 'file', cls: 'i-warn', val: status?.resumes ?? 0, label: 'CVs gerados', foot: `${status?.briefs ?? 0} briefings` },
  ]

  return (
    <div className="kpi-grid">
      {cards.map((c) => (
        <div className="kpi" key={c.label}>
          <div className={`kpi-ico ${c.cls}`}><Icon name={c.ico} size={18} /></div>
          <div className="kpi-val">{c.val}</div>
          <div className="kpi-label">{c.label}</div>
          <div className="kpi-foot">{c.foot}</div>
        </div>
      ))}
    </div>
  )
}
