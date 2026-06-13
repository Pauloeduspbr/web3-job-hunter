import { useState } from 'react'
import { api } from '../api.js'
import Icon from './Icon.jsx'

const STAGES = [
  { id: 'scrape', ico: 'link', label: 'Scrape de links', hint: 'Apify · pontua automático', cost: 'paid', costLabel: '~$0.005/vaga' },
  { id: 'boards', ico: 'layers', label: 'Boards grátis', hint: 'Greenhouse · Ashby · Lever · RemoteOK · RSS', cost: 'free', costLabel: '$0' },
  { id: 'score', ico: 'refresh', label: 'Re-pontuar vagas', hint: 'match vs perfil', cost: 'free', costLabel: '$0' },
]

function summarize(stage, res) {
  if (res == null || typeof res !== 'object') return `${stage} concluído`
  if ('scraped' in res) return `${res.scraped} vaga(s) coletada(s) · ${res.scored} pontuada(s)`
  if ('found' in res) return `${res.found} vaga(s) encontrada(s) · ${res.scored} pontuada(s)`
  if ('scored' in res) return `${res.scored} vaga(s) re-pontuada(s)`
  return JSON.stringify(res)
}

export default function PipelinePanel({ notify, refresh, running = [] }) {
  const [local, setLocal] = useState(null)
  const [search, setSearch] = useState({ keywords: 'data engineer', location: 'United States', max_jobs: 50, include_description: true })
  const busy = local || (running.length ? running[0] : null)

  const run = async (stage, body) => {
    setLocal(stage)
    try {
      const res = await api.runStage(stage, body)
      notify(`${stage}: ${summarize(stage, res)}`)
      await refresh()
    } catch (e) {
      notify(`${stage} falhou: ${e.message}`, true)
    } finally {
      setLocal(null)
    }
  }

  const Loading = ({ on }) => on
    ? <><span className="spin"><Icon name="refresh" size={14} /></span> rodando…</>
    : null

  return (
    <section className="card card-pad">
      <div className="card-head">
        <div className="ico"><Icon name="zap" size={15} /></div>
        <span className="ttl">Pipeline de busca</span>
      </div>

      <div className="stage-list">
        {STAGES.map((s) => (
          <div className="stage-row" key={s.id}>
            <div className="kpi-ico i-brand" style={{ width: 34, height: 34 }}><Icon name={s.ico} size={15} /></div>
            <div className="s-meta">
              <div className="s-name">{s.label} <span className={`cost ${s.cost}`}>{s.costLabel}</span></div>
              <div className="s-hint">{s.hint}</div>
            </div>
            <button className="btn btn-ghost btn-sm" disabled={!!busy} onClick={() => run(s.id)}>
              {busy === s.id ? <Loading on /> : <>Rodar</>}
            </button>
          </div>
        ))}
      </div>

      <div className="search-box">
        <div className="card-head" style={{ marginBottom: 10 }}>
          <Icon name="search" size={15} style={{ color: 'var(--brand-700)' }} />
          <span className="ttl" style={{ fontSize: '0.92rem' }}>Buscar no LinkedIn</span>
          <span className="cost" style={{ marginLeft: 'auto' }}>compute units</span>
        </div>
        <div className="search-grid">
          <div className="field">
            <label className="label">Palavras-chave</label>
            <input className="input" value={search.keywords} placeholder="data engineer"
              onChange={(e) => setSearch({ ...search, keywords: e.target.value })} />
          </div>
          <div className="field">
            <label className="label">Localização</label>
            <input className="input" value={search.location} placeholder="United States"
              onChange={(e) => setSearch({ ...search, location: e.target.value })} />
          </div>
        </div>
        <label className="toggle-chk" style={{ marginBottom: 10, width: '100%', justifyContent: 'flex-start' }}>
          <input type="checkbox" checked={search.include_description}
            onChange={(e) => setSearch({ ...search, include_description: e.target.checked })} />
          Trazer descrição completa na busca (mais lento, sem custo de Detalhar)
        </label>
        <button className="btn btn-primary btn-block" disabled={!!busy} onClick={() => run('search', search)}>
          {busy === 'search' ? <Loading on /> : <><Icon name="search" size={15} /> Buscar vagas</>}
        </button>
        <p className="hint">{search.include_description
          ? 'Com isso, cada vaga já vem com requisitos e modalidade (remote/híbrida) e pontuada — sem precisar do Detalhar pago.'
          : 'A busca traz só a listagem — use Detalhar em cada vaga para descrição + modalidade (remote/híbrida) e re-score.'}</p>
      </div>
    </section>
  )
}
