import { useMemo, useState } from 'react'
import { api } from '../api.js'
import Icon from './Icon.jsx'
import ScoreGauge from './ScoreGauge.jsx'
import { prettySkill, scoreTier } from '../skills.js'

const WORKPLACE = {
  remote: { label: 'Remote', ico: 'home' },
  hybrid: { label: 'Híbrida', ico: 'building' },
  onsite: { label: 'Presencial', ico: 'pin' },
  unknown: { label: 'Sem detalhe', ico: 'briefcase' },
}

function Chip({ kind, children }) {
  return <span className={`chip chip-${kind}`}>{children}</span>
}

// score tier (high/mid/low) -> bar color class (ok/warn/danger)
const TONE = { high: 'ok', mid: 'warn', low: 'danger' }
function Bar({ pct }) {
  const tone = TONE[scoreTier(pct)]
  return <div className={`bar ${tone}`}><i style={{ width: `${Math.max(0, Math.min(100, pct))}%` }} /></div>
}

// Splits "remote (+5)" / "hybrid (-15)" into label + signed text for evidence rows.
function evidence(items, dir) {
  return (items || []).map((t, i) => (
    <div className={`evid ${dir}`} key={i}>
      <span className="ei">{dir === 'up' ? '+' : '−'}</span>
      <span>{t}</span>
    </div>
  ))
}

function JobCard({ job, busy, enriching, onStatus, onEnrich, onGenerate, onOpen }) {
  const [open, setOpen] = useState(false)
  const st = job.status || 'new'
  const wp = WORKPLACE[job.workplace || 'unknown'] || WORKPLACE.unknown
  const tier = scoreTier(job.score || 0)
  const enrichable = job.needs_detail && /^\d+$/.test(String(job.job_id))

  const matched = job.matched_skills || []
  const gaps = job.gap_skills || []
  const demanded = job.demanded_skills || []
  const coverage = demanded.length ? Math.round((matched.length / demanded.length) * 100) : 0
  const salary = typeof job.salary === 'string' && job.salary.trim() ? job.salary.trim() : null

  // a job only gets a real ATS analysis once its description was fetched.
  // listing-only jobs (needs_detail) would otherwise show a misleading
  // "analysis" built only from the title — so we gate everything on this.
  const hasDetail = !job.needs_detail && demanded.length > 0

  return (
    <article className={`job-card ${st === 'applied' ? 'is-applied' : ''} ${(job.score || 0) < 60 || job.off_target ? 'is-low' : ''}`}>
      <div className="job-top">
        <ScoreGauge score={job.score || 0} />

        <div className="job-mid">
          <div className="job-title-row">
            {job.url
              ? <a className="job-title" href={job.url} target="_blank" rel="noreferrer" onClick={() => onOpen(job)}>{job.title}</a>
              : <span className="job-title">{job.title}</span>}
            <span className={`tier-tag ${tier}`}>{job.score?.toFixed(0)}</span>
            {job.off_target && (
              <span className="off-target-tag" title="Fora de alvo: provavelmente não é engenharia de dados de software">
                <Icon name="filter" size={11} /> fora de alvo
              </span>
            )}
            {st === 'applied' && (
              <span className="applied-flag">
                <Icon name="check" size={11} /> CV enviado{job.status_updated_at ? ` · ${new Date(job.status_updated_at).toLocaleDateString('pt-BR')}` : ''}
              </span>
            )}
          </div>

          <div className="job-meta">
            <span className="job-company"><Icon name="building" size={13} /> {job.company || '—'}</span>
            <span className={`badge ${job.workplace || 'unknown'}`}><Icon name={wp.ico} size={11} /> {wp.label}</span>
            {job.location && <span className="mi"><Icon name="pin" size={13} /> {job.location}</span>}
            {salary && <span className="mi"><Icon name="trophy" size={13} /> {salary}</span>}
          </div>

          {hasDetail ? (
            <div className="chips">
              {matched.map((s) => <Chip kind="match" key={`m-${s}`}><Icon name="check" size={11} /> {prettySkill(s)}</Chip>)}
              {gaps.map((s) => <Chip kind="gap" key={`g-${s}`}>{prettySkill(s)}</Chip>)}
            </div>
          ) : (
            <div className="chips">
              <Chip kind="more">
                {job.needs_detail
                  ? 'Detalhe pendente — clique “Detalhar” para extrair os requisitos'
                  : 'Nenhum requisito reconhecido na descrição'}
              </Chip>
            </div>
          )}
        </div>

        <div className="job-actions">
          <div className="flag-row">
            <button
              className={`flag ${st === 'viewed' ? 'on' : ''}`}
              title={st === 'viewed' ? 'Vista — clique p/ desmarcar' : 'Marcar como vista'}
              onClick={() => onStatus(job, 'viewed')}
            ><Icon name="eye" size={15} /></button>
            <button
              className={`flag ${st === 'applied' ? 'on applied' : ''}`}
              title={st === 'applied' ? 'CV enviado — clique p/ desmarcar' : 'Marcar: já enviei meu CV'}
              onClick={() => onStatus(job, 'applied')}
            ><Icon name="check" size={15} /></button>
          </div>
          {enrichable && (
            <button className="btn btn-ghost btn-sm" disabled={enriching}
              title="Busca descrição completa + modalidade ($0.005)" onClick={() => onEnrich([job.job_id])}>
              <Icon name="search" size={14} /> Detalhar
            </button>
          )}
          <button className="btn btn-primary btn-sm" disabled={busy !== null} onClick={() => onGenerate(job.job_id)}>
            {busy === job.job_id ? <><span className="spin"><Icon name="refresh" size={14} /></span></> : <><Icon name="sparkles" size={14} /> Gerar CV</>}
          </button>
        </div>
      </div>

      {hasDetail && (
        <>
          <button className={`analysis-toggle ${open ? 'open' : ''}`} onClick={() => setOpen((v) => !v)}>
            <Icon name="target" size={15} /> {open ? 'Ocultar análise ATS' : `Ver análise ATS · ${demanded.length} requisitos`}
            <span className="chev"><Icon name="chevron" size={16} /></span>
          </button>
          {open && (
            <div className="analysis">
              <div className="analysis-grid">
                <div className="an-block">
                  <h4><Icon name="filter" size={13} /> Composição da nota</h4>
                  <div className="compo">
                    <div className="compo-row">
                      <div className="compo-top"><span className="k">Cobertura de requisitos</span><span className="v">{matched.length}/{demanded.length}</span></div>
                      <Bar pct={coverage} />
                    </div>
                    <div className="compo-row">
                      <div className="compo-top"><span className="k">Match ponderado de skills <small style={{ color: 'var(--muted)' }}>· 80% do score</small></span><span className="v">{(job.skill_score ?? 0).toFixed(0)}</span></div>
                      <Bar pct={job.skill_score ?? 0} />
                    </div>
                    <div className="compo-row">
                      <div className="compo-top"><span className="k">Score final</span><span className="v">{(job.score ?? 0).toFixed(0)}/100</span></div>
                      <Bar pct={job.score ?? 0} />
                    </div>
                  </div>

                  {(job.bonuses?.length || job.penalties?.length) ? (
                    <div style={{ marginTop: 16 }}>
                      <h4><Icon name="zap" size={13} /> Ajustes aplicados</h4>
                      <div className="evid-list">
                        {evidence(job.bonuses, 'up')}
                        {evidence(job.penalties, 'down')}
                      </div>
                    </div>
                  ) : null}
                </div>

                <div className="an-block">
                  <h4><Icon name="list" size={13} /> Requisitos da vaga · {demanded.length} detectados · você cobre {matched.length}</h4>
                  <div className="kw-group">
                    <h4 style={{ color: 'var(--ok-700)' }}><Icon name="check" size={13} /> Skills encontradas ({matched.length})</h4>
                    <div className="chips">
                      {matched.length
                        ? matched.map((s) => <Chip kind="match" key={s}>{prettySkill(s)}</Chip>)
                        : <Chip kind="more">nenhuma do perfil identificada</Chip>}
                    </div>
                  </div>
                  <div className="kw-group">
                    <h4 style={{ color: 'var(--danger-700)' }}><Icon name="target" size={13} /> Gaps — exigidas que faltam ({gaps.length})</h4>
                    <div className="chips">
                      {gaps.length
                        ? gaps.map((s) => <Chip kind="gap" key={s}>{prettySkill(s)}</Chip>)
                        : <Chip kind="match"><Icon name="check" size={11} /> nenhum gap</Chip>}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </article>
  )
}

export default function JobsBoard({ jobs, notify, refresh }) {
  const [busy, setBusy] = useState(null)
  const [enriching, setEnriching] = useState(false)
  const [wpFilter, setWpFilter] = useState('all')
  const [stFilter, setStFilter] = useState('all')
  const [minScore, setMinScore] = useState(0)
  const [query, setQuery] = useState('')
  const [hideOffTarget, setHideOffTarget] = useState(true)

  const filtered = useMemo(() => jobs.filter((j) => {
    if (hideOffTarget && j.off_target) return false
    if (wpFilter !== 'all' && (j.workplace || 'unknown') !== wpFilter) return false
    const st = j.status || 'new'
    if (stFilter === 'pending' && st === 'applied') return false
    if (stFilter !== 'all' && stFilter !== 'pending' && st !== stFilter) return false
    if ((j.score || 0) < minScore) return false
    if (query) {
      const text = `${j.title} ${j.company} ${j.location}`.toLowerCase()
      if (!text.includes(query.toLowerCase())) return false
    }
    return true
  }), [jobs, wpFilter, stFilter, minScore, query, hideOffTarget])

  const enrichable = filtered.filter((j) => j.needs_detail && /^\d+$/.test(String(j.job_id)))
  const appliedCount = jobs.filter((j) => j.status === 'applied').length
  const offTargetCount = jobs.filter((j) => j.off_target).length
  const hiddenOffTarget = hideOffTarget ? offTargetCount : 0

  const onStatus = async (job, status) => {
    const next = (job.status === status) ? 'new' : status
    try { await api.setJobStatus(job.job_id, next); await refresh() }
    catch (e) { notify(`Falha ao salvar status: ${e.message}`, true) }
  }

  const onOpen = (job) => {
    if ((job.status || 'new') === 'new') {
      api.setJobStatus(job.job_id, 'viewed').then(refresh).catch(() => {})
    }
  }

  const onGenerate = async (jobId) => {
    setBusy(jobId)
    try {
      const res = await api.generateCv(jobId)
      notify(res.message || `Brief: ${res.brief}${res.resume ? ` · CV: ${res.resume}` : ''}`)
      await refresh()
    } catch (e) {
      notify(`Geração falhou: ${e.message}`, true)
    } finally { setBusy(null) }
  }

  const onEnrich = async (jobIds) => {
    setEnriching(true)
    try {
      const res = await api.enrich(jobIds)
      notify(`${res.enriched} vaga(s) enriquecidas com descrição + modalidade — re-pontuadas`)
      await refresh()
    } catch (e) {
      notify(`Enriquecimento falhou: ${e.message}`, true)
    } finally { setEnriching(false) }
  }

  return (
    <section>
      <div className="section-head">
        <h2>Vagas pontuadas</h2>
        <span className="sub">
          {jobs.length
            ? `${filtered.length} de ${jobs.length}${appliedCount ? ` · ${appliedCount} aplicadas` : ''}${hiddenOffTarget ? ` · ${hiddenOffTarget} fora de alvo ocultas` : ''}`
            : 'nenhuma vaga ainda'}
        </span>
      </div>

      {!jobs.length ? (
        <div className="card empty">
          <span className="e-ico"><Icon name="briefcase" size={34} /></span>
          <strong>Nenhuma vaga pontuada ainda</strong>
          <span className="small">Rode o pipeline ou cole links de vagas no workspace acima.</span>
        </div>
      ) : (
        <>
          <div className="toolbar">
            <select className="select" style={{ width: 'auto' }} value={stFilter} onChange={(e) => setStFilter(e.target.value)}>
              <option value="all">Status: todos</option>
              <option value="pending">Não aplicadas</option>
              <option value="new">Novas</option>
              <option value="viewed">Vistas</option>
              <option value="applied">Aplicadas</option>
            </select>
            <select className="select" style={{ width: 'auto' }} value={wpFilter} onChange={(e) => setWpFilter(e.target.value)}>
              <option value="all">Modalidade: todas</option>
              <option value="remote">Remote</option>
              <option value="hybrid">Híbrida</option>
              <option value="onsite">Presencial</option>
              <option value="unknown">Sem detalhe</option>
            </select>
            <label className="score-min">Score ≥ <input type="number" min="0" max="100" value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value) || 0)} /></label>
            <label className="toggle-chk" title="Esconde vagas marcadas como fora de alvo (papel não-DE de software)">
              <input type="checkbox" checked={hideOffTarget} onChange={(e) => setHideOffTarget(e.target.checked)} />
              Ocultar fora de alvo{offTargetCount ? ` (${offTargetCount})` : ''}
            </label>
            <div className="search-wrap">
              <span className="s-ico"><Icon name="search" size={15} /></span>
              <input className="input" placeholder="filtrar por título, empresa ou local…" value={query}
                onChange={(e) => setQuery(e.target.value)} />
            </div>
            {enrichable.length > 0 && (
              <button className="btn btn-soft btn-sm" disabled={enriching} onClick={() => onEnrich(enrichable.map((j) => j.job_id))}>
                {enriching
                  ? <><span className="spin"><Icon name="refresh" size={14} /></span> enriquecendo…</>
                  : <><Icon name="search" size={14} /> Detalhar {enrichable.length} (~${(enrichable.length * 0.005).toFixed(2)})</>}
              </button>
            )}
          </div>

          <div className="jobs">
            {filtered.map((j) => (
              <JobCard
                key={j.job_id}
                job={j}
                busy={busy}
                enriching={enriching}
                onStatus={onStatus}
                onEnrich={onEnrich}
                onGenerate={onGenerate}
                onOpen={onOpen}
              />
            ))}
          </div>
        </>
      )}
    </section>
  )
}
