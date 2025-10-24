import { useMemo } from 'react'
import './SummaryPanel.css'

function SummaryPanel({ windowData, doorData, applianceData, selections }) {
  const metrics = useMemo(() => {
    const calculateCategoryMetrics = (data) => {
      let totalOriginalCost = 0
      let totalSelectedCost = 0
      let functionalScoreSum = 0
      let designScoreSum = 0
      let costReductionSum = 0
      let count = 0

      data.forEach(group => {
        const selected = selections[group.materialId]
        if (!selected) return

        // Use TOTAL costs (unit cost * quantity), not unit costs
        const originalCost = parseFloat(selected.ORIGINAL_TOTAL_COST || selected.ORIGINAL_COST || 0)
        const selectedCost = parseFloat(selected.ALT_TOTAL_COST_TOTAL || selected.ALT_COST_TOTAL || 0)
        
        totalOriginalCost += originalCost
        totalSelectedCost += selectedCost
        
        functionalScoreSum += parseFloat(selected.FUNCTIONAL_SCORE || 5)
        designScoreSum += parseFloat(selected.DESIGN_SCORE || 5)
        
        const reduction = parseFloat(selected.COST_REDUCTION_PCT || 0)
        costReductionSum += reduction
        
        count++
      })

      const avgFunctional = count > 0 ? functionalScoreSum / count : 0
      const avgDesign = count > 0 ? designScoreSum / count : 0
      const avgCostReduction = count > 0 ? costReductionSum / count : 0
      const totalSavings = totalOriginalCost - totalSelectedCost
      const savingsPercent = totalOriginalCost > 0 
        ? (totalSavings / totalOriginalCost) * 100 
        : 0

      return {
        totalOriginalCost,
        totalSelectedCost,
        totalSavings,
        savingsPercent,
        avgFunctional,
        avgDesign,
        avgCostReduction,
        count
      }
    }

    const windows = calculateCategoryMetrics(windowData)
    const doors = calculateCategoryMetrics(doorData)
    const appliances = calculateCategoryMetrics(applianceData)

    // Overall totals
    const totalOriginalCost = windows.totalOriginalCost + doors.totalOriginalCost + appliances.totalOriginalCost
    const totalSelectedCost = windows.totalSelectedCost + doors.totalSelectedCost + appliances.totalSelectedCost
    const totalSavings = totalOriginalCost - totalSelectedCost
    const totalSavingsPercent = totalOriginalCost > 0 ? (totalSavings / totalOriginalCost) * 100 : 0
    const totalCount = windows.count + doors.count + appliances.count

    const overallAvgFunctional = totalCount > 0
      ? (windows.avgFunctional * windows.count + 
         doors.avgFunctional * doors.count + 
         appliances.avgFunctional * appliances.count) / totalCount
      : 0

    const overallAvgDesign = totalCount > 0
      ? (windows.avgDesign * windows.count + 
         doors.avgDesign * doors.count + 
         appliances.avgDesign * appliances.count) / totalCount
      : 0

    const overallAvgCostReduction = totalCount > 0
      ? (windows.avgCostReduction * windows.count + 
         doors.avgCostReduction * doors.count + 
         appliances.avgCostReduction * appliances.count) / totalCount
      : 0

    return {
      windows,
      doors,
      appliances,
      overall: {
        totalOriginalCost,
        totalSelectedCost,
        totalSavings,
        totalSavingsPercent,
        avgFunctional: overallAvgFunctional,
        avgDesign: overallAvgDesign,
        avgCostReduction: overallAvgCostReduction
      }
    }
  }, [windowData, doorData, applianceData, selections])

  const formatCurrency = (value) => {
    return `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  const formatScore = (value) => {
    return value.toFixed(2)
  }

  const formatPercent = (value) => {
    return `${value.toFixed(1)}%`
  }

  const getScoreColor = (score) => {
    if (score >= 4.5) return '#10b981'
    if (score >= 3.5) return '#f59e0b'
    return '#ef4444'
  }

  return (
    <div className="summary-panel">
      <div className="summary-header">
        <h2>Overall Summary</h2>
      </div>

      {/* Overall Metrics */}
      <div className="overall-section">
        <div className="overall-grid">
          <div className="overall-card cost-card">
            <div className="overall-label">Total Original Cost</div>
            <div className="overall-value">{formatCurrency(metrics.overall.totalOriginalCost)}</div>
          </div>
          <div className="overall-card cost-card">
            <div className="overall-label">Total Selected Cost</div>
            <div className="overall-value cost-selected">{formatCurrency(metrics.overall.totalSelectedCost)}</div>
          </div>
          <div className="overall-card savings-card">
            <div className="overall-label">Total Savings</div>
            <div className="overall-value savings-value">
              {formatCurrency(metrics.overall.totalSavings)}
              <span className="savings-percent"> ({formatPercent(metrics.overall.totalSavingsPercent)})</span>
            </div>
          </div>
        </div>

        <div className="scores-grid">
          <div className="score-card">
            <div className="score-label">Avg Functional Deviation</div>
            <div className="score-value" style={{ color: getScoreColor(metrics.overall.avgFunctional) }}>
              {formatScore(metrics.overall.avgFunctional)} / 5.0
            </div>
            <div className="score-bar">
              <div 
                className="score-fill"
                style={{ 
                  width: `${(metrics.overall.avgFunctional / 5) * 100}%`,
                  backgroundColor: getScoreColor(metrics.overall.avgFunctional)
                }}
              />
            </div>
          </div>

          <div className="score-card">
            <div className="score-label">Avg Design Deviation</div>
            <div className="score-value" style={{ color: getScoreColor(metrics.overall.avgDesign) }}>
              {formatScore(metrics.overall.avgDesign)} / 5.0
            </div>
            <div className="score-bar">
              <div 
                className="score-fill"
                style={{ 
                  width: `${(metrics.overall.avgDesign / 5) * 100}%`,
                  backgroundColor: getScoreColor(metrics.overall.avgDesign)
                }}
              />
            </div>
          </div>

          <div className="score-card">
            <div className="score-label">Avg Cost Reduction</div>
            <div className="score-value" style={{ color: '#667eea' }}>
              {formatPercent(metrics.overall.avgCostReduction)}
            </div>
            <div className="score-bar">
              <div 
                className="score-fill"
                style={{ 
                  width: `${Math.min((metrics.overall.avgCostReduction / 30) * 100, 100)}%`,
                  backgroundColor: '#667eea'
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Category Breakdown */}
      <div className="category-breakdown">
        <h3>By Category</h3>
        
        <div className="category-metrics">
          {/* Windows */}
          <div className="category-metric-card">
            <div className="category-metric-header">
              <span className="category-icon">🪟</span>
              <span className="category-name">Windows</span>
            </div>
            <div className="category-metric-row">
              <span className="metric-label">Savings:</span>
              <span className="metric-value savings">{formatCurrency(metrics.windows.totalSavings)} ({formatPercent(metrics.windows.savingsPercent)})</span>
            </div>
            <div className="category-metric-row">
              <span className="metric-label">Functional:</span>
              <span className="metric-value">{formatScore(metrics.windows.avgFunctional)} / 5</span>
            </div>
            <div className="category-metric-row">
              <span className="metric-label">Design:</span>
              <span className="metric-value">{formatScore(metrics.windows.avgDesign)} / 5</span>
            </div>
          </div>

          {/* Doors */}
          <div className="category-metric-card">
            <div className="category-metric-header">
              <span className="category-icon">🚪</span>
              <span className="category-name">Doors</span>
            </div>
            <div className="category-metric-row">
              <span className="metric-label">Savings:</span>
              <span className="metric-value savings">{formatCurrency(metrics.doors.totalSavings)} ({formatPercent(metrics.doors.savingsPercent)})</span>
            </div>
            <div className="category-metric-row">
              <span className="metric-label">Functional:</span>
              <span className="metric-value">{formatScore(metrics.doors.avgFunctional)} / 5</span>
            </div>
            <div className="category-metric-row">
              <span className="metric-label">Design:</span>
              <span className="metric-value">{formatScore(metrics.doors.avgDesign)} / 5</span>
            </div>
          </div>

          {/* Appliances */}
          <div className="category-metric-card">
            <div className="category-metric-header">
              <span className="category-icon">🍳</span>
              <span className="category-name">Appliances</span>
            </div>
            <div className="category-metric-row">
              <span className="metric-label">Savings:</span>
              <span className="metric-value savings">{formatCurrency(metrics.appliances.totalSavings)} ({formatPercent(metrics.appliances.savingsPercent)})</span>
            </div>
            <div className="category-metric-row">
              <span className="metric-label">Functional:</span>
              <span className="metric-value">{formatScore(metrics.appliances.avgFunctional)} / 5</span>
            </div>
            <div className="category-metric-row">
              <span className="metric-label">Design:</span>
              <span className="metric-value">{formatScore(metrics.appliances.avgDesign)} / 5</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SummaryPanel

