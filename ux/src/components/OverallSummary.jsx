import { useMemo } from 'react'
import './OverallSummary.css'

function OverallSummary({ windowData, doorData, applianceData, selections }) {
  const metrics = useMemo(() => {
    const calculateCategoryMetrics = (data) => {
      let totalOriginalCost = 0
      let totalSelectedCost = 0
      let functionalScoreSum = 0
      let designScoreSum = 0
      let count = 0

      data.forEach(group => {
        const selected = selections[group.materialId]
        if (!selected) return

        const originalCost = parseFloat(selected.ORIGINAL_TOTAL_COST || selected.ORIGINAL_COST || 0)
        const selectedCost = parseFloat(selected.ALT_TOTAL_COST_TOTAL || selected.ALT_COST_TOTAL || 0)
        
        totalOriginalCost += originalCost
        totalSelectedCost += selectedCost
        
        functionalScoreSum += parseFloat(selected.FUNCTIONAL_SCORE || 5)
        designScoreSum += parseFloat(selected.DESIGN_SCORE || 5)
        
        count++
      })

      const avgFunctional = count > 0 ? functionalScoreSum / count : 0
      const avgDesign = count > 0 ? designScoreSum / count : 0
      const totalSavings = totalOriginalCost - totalSelectedCost
      const savingsPercent = totalOriginalCost > 0 
        ? (totalSavings / totalOriginalCost) * 100 
        : 0

      return { totalOriginalCost, totalSelectedCost, totalSavings, savingsPercent, avgFunctional, avgDesign }
    }

    const totalCount = windowData.length + doorData.length + applianceData.length
    const windows = calculateCategoryMetrics(windowData)
    const doors = calculateCategoryMetrics(doorData)
    const appliances = calculateCategoryMetrics(applianceData)

    const totalOriginalCost = windows.totalOriginalCost + doors.totalOriginalCost + appliances.totalOriginalCost
    const totalSelectedCost = windows.totalSelectedCost + doors.totalSelectedCost + appliances.totalSelectedCost
    const totalSavings = totalOriginalCost - totalSelectedCost
    const totalSavingsPercent = totalOriginalCost > 0 ? (totalSavings / totalOriginalCost) * 100 : 0

    const overallAvgFunctional = totalCount > 0
      ? (windows.avgFunctional * windowData.length + doors.avgFunctional * doorData.length + appliances.avgFunctional * applianceData.length) / totalCount : 0
    const overallAvgDesign = totalCount > 0
      ? (windows.avgDesign * windowData.length + doors.avgDesign * doorData.length + appliances.avgDesign * applianceData.length) / totalCount : 0

    return {
      totalOriginalCost,
      totalSelectedCost,
      totalSavings,
      totalSavingsPercent,
      avgFunctional: overallAvgFunctional,
      avgDesign: overallAvgDesign
    }
  }, [windowData, doorData, applianceData, selections])

  const formatCurrency = (value) => {
    return `$${value.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
  }

  const getScoreColor = (score) => {
    if (score >= 4.5) return '#10b981'
    if (score >= 3.5) return '#f59e0b'
    return '#ef4444'
  }

  return (
    <div className="overall-summary">
      <h3>Overall</h3>
      
      <div className="summary-content">
        <div className="summary-metric">
          <div className="summary-label">Baseline</div>
          <div className="summary-value">{formatCurrency(metrics.totalOriginalCost)}</div>
        </div>

        <div className="summary-metric">
          <div className="summary-label">Selected</div>
          <div className="summary-value selected">{formatCurrency(metrics.totalSelectedCost)}</div>
        </div>

        <div className="summary-metric highlight">
          <div className="summary-label">Savings</div>
          <div className="summary-value savings">
            {formatCurrency(metrics.totalSavings)}
            <div className="summary-percent">{metrics.totalSavingsPercent.toFixed(1)}%</div>
          </div>
        </div>

        <div className="summary-scores">
          <div className="score-item">
            <div className="score-label">Functional</div>
            <div className="score-value" style={{ color: getScoreColor(metrics.avgFunctional) }}>
              {metrics.avgFunctional.toFixed(1)}
            </div>
            <div className="score-bar">
              <div className="score-fill" style={{ 
                width: `${(metrics.avgFunctional / 5) * 100}%`,
                backgroundColor: getScoreColor(metrics.avgFunctional)
              }} />
            </div>
          </div>

          <div className="score-item">
            <div className="score-label">Design</div>
            <div className="score-value" style={{ color: getScoreColor(metrics.avgDesign) }}>
              {metrics.avgDesign.toFixed(1)}
            </div>
            <div className="score-bar">
              <div className="score-fill" style={{ 
                width: `${(metrics.avgDesign / 5) * 100}%`,
                backgroundColor: getScoreColor(metrics.avgDesign)
              }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OverallSummary

