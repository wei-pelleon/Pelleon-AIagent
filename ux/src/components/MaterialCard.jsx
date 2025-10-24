import { useState } from 'react'
import './MaterialCard.css'

function MaterialCard({ group, selected, onSelect }) {
  const [isExpanded, setIsExpanded] = useState(false)

  if (!group || !group.alternatives || group.alternatives.length === 0) {
    return null
  }

  const original = group.alternatives.find(alt => alt.ALT_RANK === '0')
  const alternatives = group.alternatives.filter(alt => alt.ALT_RANK !== '0')

  const formatCurrency = (value) => {
    const num = parseFloat(value)
    return isNaN(num) ? '$0.00' : `$${num.toFixed(2)}`
  }

  const formatPercent = (value) => {
    const num = parseFloat(value)
    return isNaN(num) ? '0%' : `${num.toFixed(1)}%`
  }

  const getScoreColor = (score) => {
    const num = parseFloat(score)
    if (num >= 4.5) return '#10b981' // green
    if (num >= 3.5) return '#f59e0b' // amber
    return '#ef4444' // red
  }

  const getCostReductionColor = (percent) => {
    const num = parseFloat(percent)
    if (num >= 20) return '#10b981'
    if (num >= 10) return '#f59e0b'
    if (num > 0) return '#6366f1'
    return '#6c757d'
  }

  // Get full description
  const materialDesc = original?.MATERIAL_DESC || original?.ALT_DESC || group.materialId

  return (
    <div className="material-card">
      <div className="card-header">
        <div className="material-id-full">{materialDesc}</div>
        <div className="material-type">{group.materialType}</div>
      </div>

      {/* Original Material */}
      <div className="original-section">
        <div className="section-label">Original</div>
        <div className="original-desc">{original?.ALT_DESC || 'N/A'}</div>
        <div className="original-cost">
          {formatCurrency(original?.ALT_COST_TOTAL)}
        </div>
      </div>

      {/* Alternative Selector */}
      {alternatives.length > 0 && (
        <div className="alternative-section">
          <label className="section-label">Select Alternative</label>
          <select 
            className="alt-select"
            value={selected?.ALT_RANK || '0'}
            onChange={(e) => {
              const alt = group.alternatives.find(a => a.ALT_RANK === e.target.value)
              onSelect(alt)
              setIsExpanded(e.target.value !== '0')
            }}
          >
            <option value="0">Keep Original - {formatCurrency(original?.ALT_COST_TOTAL)}</option>
            {alternatives.map((alt, idx) => {
              const strategyLabel = alt.STRATEGY_LABEL || `Alt ${alt.ALT_RANK}`
              const brand = alt.PRODUCT_BRAND ? ` [${alt.PRODUCT_BRAND}${alt.PRODUCT_MODEL ? ' ' + alt.PRODUCT_MODEL : ''}]` : ''
              return (
                <option key={idx} value={alt.ALT_RANK}>
                  {strategyLabel}: {alt.ALT_DESC}{brand} - {formatCurrency(alt.ALT_COST_TOTAL)}
                  {alt.COST_REDUCTION_PCT && ` (${formatPercent(alt.COST_REDUCTION_PCT)} off)`}
                </option>
              )
            })}
          </select>
        </div>
      )}

      {/* Selected Alternative Details */}
      {selected && selected.ALT_RANK !== '0' && isExpanded && (
        <div className="alt-details">
          <div className="alt-description">
            {selected.ALT_DESC}
            {selected.PRODUCT_BRAND && (
              <div className="product-brand">
                <strong>{selected.PRODUCT_BRAND}</strong>
                {selected.PRODUCT_MODEL && ` ${selected.PRODUCT_MODEL}`}
                {selected.PRODUCT_NOTES && <span className="product-notes"> • {selected.PRODUCT_NOTES}</span>}
              </div>
            )}
          </div>

          <div className="metrics-grid">
            <div className="metric">
              <div className="metric-label">Functional</div>
              <div 
                className="metric-value"
                style={{ color: getScoreColor(selected.FUNCTIONAL_SCORE) }}
              >
                {selected.FUNCTIONAL_SCORE || 'N/A'} / 5
              </div>
            </div>

            <div className="metric">
              <div className="metric-label">Design</div>
              <div 
                className="metric-value"
                style={{ color: getScoreColor(selected.DESIGN_SCORE) }}
              >
                {selected.DESIGN_SCORE || 'N/A'} / 5
              </div>
            </div>

            <div className="metric">
              <div className="metric-label">Cost Reduction</div>
              <div 
                className="metric-value"
                style={{ color: getCostReductionColor(selected.COST_REDUCTION_PCT) }}
              >
                {formatPercent(selected.COST_REDUCTION_PCT)}
              </div>
            </div>
          </div>

          <div className="cost-comparison">
            <div className="cost-row">
              <span className="cost-label">Unit Cost (Original):</span>
              <span className="cost-amount">{formatCurrency(selected.ORIGINAL_COST)}</span>
            </div>
            <div className="cost-row">
              <span className="cost-label">Unit Cost (Alternative):</span>
              <span className="cost-amount cost-alt">{formatCurrency(selected.ALT_COST_TOTAL)}</span>
            </div>
            <div className="cost-row">
              <span className="cost-label">Quantity:</span>
              <span className="cost-amount">{selected.QUANTITY || 1}</span>
            </div>
            <div className="cost-row cost-total">
              <span className="cost-label">Total Original:</span>
              <span className="cost-amount">{formatCurrency(selected.ORIGINAL_TOTAL_COST || selected.ORIGINAL_COST)}</span>
            </div>
            <div className="cost-row cost-total">
              <span className="cost-label">Total Alternative:</span>
              <span className="cost-amount cost-alt">{formatCurrency(selected.ALT_TOTAL_COST_TOTAL || selected.ALT_COST_TOTAL)}</span>
            </div>
            <div className="cost-row cost-savings">
              <span className="cost-label">Total Savings:</span>
              <span className="cost-amount">
                {formatCurrency(parseFloat(selected.ORIGINAL_TOTAL_COST || selected.ORIGINAL_COST || 0) - parseFloat(selected.ALT_TOTAL_COST_TOTAL || selected.ALT_COST_TOTAL || 0))}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MaterialCard

