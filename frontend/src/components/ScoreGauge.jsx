import { scoreTier, TIER_COLOR, TIER_LABEL } from '../skills.js'

// Conic-gradient ring gauge. Score 0–100 → arc fill + tier color.
// caption=false renders just the dial (used in compact spots).
export default function ScoreGauge({ score, caption = true }) {
  const value = Math.max(0, Math.min(100, Number(score) || 0))
  const tier = scoreTier(value)
  return (
    <div>
      <div className="gauge" style={{ '--p': value, '--c': TIER_COLOR[tier] }}>
        <div className="ring" />
        <div className="num">
          <b>{value.toFixed(0)}</b>
          <span>/100</span>
        </div>
      </div>
      {caption && (
        <div className="gauge-cap" style={{ color: TIER_COLOR[tier] }}>
          {TIER_LABEL[tier]}
        </div>
      )}
    </div>
  )
}
