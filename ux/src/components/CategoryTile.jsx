import './CategoryTile.css'

function CategoryTile({ icon, title, count, metrics, isExpanded, onClick }) {
  const formatCurrency = (value) => {
    return `$${value.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
  }

  const formatScore = (value) => {
    return value.toFixed(2)
  }

  const formatPercent = (value) => {
    return `${value.toFixed(1)}%`
  }

  return (
    <div 
      className={`category-tile ${isExpanded ? 'expanded' : ''}`}
      onClick={onClick}
    >
      <div className="tile-header">
        <div className="tile-left">
          <span className="tile-icon">{icon}</span>
          <div className="tile-title-group">
            <h3 className="tile-title">{title}</h3>
            <span className="tile-count">{count} types</span>
          </div>
        </div>
        <div className="tile-expand-icon">
          {isExpanded ? '▼' : '▶'}
        </div>
      </div>

      <div className="tile-metrics">
        <div className="tile-metric">
          <div className="tile-metric-label">Savings</div>
          <div className="tile-metric-value savings">
            {formatCurrency(metrics.totalSavings)}
            <span className="tile-metric-percent">{formatPercent(metrics.savingsPercent)}</span>
          </div>
        </div>

        <div className="tile-metric-row">
          <div className="tile-metric-small">
            <div className="tile-metric-label">Functional</div>
            <div className="tile-metric-value">{formatScore(metrics.avgFunctional)}/5</div>
          </div>
          <div className="tile-metric-small">
            <div className="tile-metric-label">Design</div>
            <div className="tile-metric-value">{formatScore(metrics.avgDesign)}/5</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CategoryTile


