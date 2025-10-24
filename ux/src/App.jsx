import { useState, useEffect, useMemo } from 'react'
import Papa from 'papaparse'
import './App.css'
import MaterialCard from './components/MaterialCard'
import PresetButtons from './components/PresetButtons'
import Header from './components/Header'
import OverallSummary from './components/OverallSummary'
import CategoryTile from './components/CategoryTile'
import ProjectInfo from './components/ProjectInfo'
import Chat from './components/Chat'

function App() {
  const [windowData, setWindowData] = useState([])
  const [doorData, setDoorData] = useState([])
  const [applianceData, setApplianceData] = useState([])
  const [selections, setSelections] = useState({})
  const [loading, setLoading] = useState(true)
  const [presets, setPresets] = useState(null)
  const [activePreset, setActivePreset] = useState(null)
  const [expandedSections, setExpandedSections] = useState({
    windows: true,
    doors: true,
    appliances: true
  })
  const [user] = useState({ username: 'User' })

  useEffect(() => {
    loadData()
    loadPresets()
  }, [])

  const handleLogout = () => {
    // Logout disabled for now
    console.log('Logout clicked')
  }

  const loadData = async () => {
    try {
      console.log('Starting to load CSV files...')
      
      // Load all three categories from public folder
      const [windows, doors, appliances] = await Promise.all([
        loadCSV('/window_alternatives_scored.csv'),
        loadCSV('/door_alternatives_scored.csv'),
        loadCSV('/appliance_alternatives_scored.csv')
      ])

      console.log('Windows data:', windows.length, 'rows')
      console.log('Doors data:', doors.length, 'rows')
      console.log('Appliances data:', appliances.length, 'rows')

      // Group by MATERIAL_ID
      const windowGroups = groupByMaterialId(windows)
      const doorGroups = groupByMaterialId(doors)
      const applianceGroups = groupByMaterialId(appliances)

      console.log('Window groups:', windowGroups.length)
      console.log('Door groups:', doorGroups.length)
      console.log('Appliance groups:', applianceGroups.length)

      setWindowData(windowGroups)
      setDoorData(doorGroups)
      setApplianceData(applianceGroups)

      // Initialize selections with originals (rank 0)
      const initialSelections = {}
      windowGroups.forEach(group => {
        initialSelections[group.materialId] = group.alternatives.find(alt => alt.ALT_RANK === '0')
      })
      doorGroups.forEach(group => {
        initialSelections[group.materialId] = group.alternatives.find(alt => alt.ALT_RANK === '0')
      })
      applianceGroups.forEach(group => {
        initialSelections[group.materialId] = group.alternatives.find(alt => alt.ALT_RANK === '0')
      })

      setSelections(initialSelections)
      setLoading(false)
    } catch (error) {
      console.error('Error loading data:', error)
      alert('Error loading data: ' + error.message)
      setLoading(false)
    }
  }

  const loadCSV = (path) => {
    return new Promise((resolve, reject) => {
      Papa.parse(path, {
        download: true,
        header: true,
        complete: (results) => resolve(results.data),
        error: (error) => reject(error)
      })
    })
  }

  const groupByMaterialId = (data) => {
    const groups = {}
    data.forEach(row => {
      if (!row.MATERIAL_ID) return
      
      if (!groups[row.MATERIAL_ID]) {
        groups[row.MATERIAL_ID] = {
          materialId: row.MATERIAL_ID,
          materialType: row.MATERIAL_TYPE,
          alternatives: []
        }
      }
      groups[row.MATERIAL_ID].alternatives.push(row)
    })

    // Sort alternatives by rank
    Object.values(groups).forEach(group => {
      group.alternatives.sort((a, b) => 
        parseInt(a.ALT_RANK || 0) - parseInt(b.ALT_RANK || 0)
      )
    })

    return Object.values(groups)
  }

  const loadPresets = async () => {
    try {
      const response = await fetch('/optimization_presets.json')
      const data = await response.json()
      setPresets(data)
      console.log('Presets loaded:', data)
    } catch (error) {
      console.error('Error loading presets:', error)
    }
  }

  const applyPreset = (presetName) => {
    if (!presets || !presets[presetName]) {
      console.error('Preset not found:', presetName)
      return
    }

    const presetSelections = presets[presetName]
    const newSelections = {}

    // Apply preset to all materials
    const allData = [...windowData, ...doorData, ...applianceData]
    allData.forEach(group => {
      const materialId = group.materialId
      const targetRank = presetSelections[materialId] || '0'
      
      // Find the alternative with this rank
      const alternative = group.alternatives.find(alt => alt.ALT_RANK === targetRank)
      if (alternative) {
        newSelections[materialId] = alternative
      }
    })

    setSelections(newSelections)
    setActivePreset(presetName)
    console.log('Applied preset:', presetName, 'Selections:', Object.keys(newSelections).length)
  }

  const handleSelectionChange = (materialId, alternative) => {
    setSelections(prev => ({
      ...prev,
      [materialId]: alternative
    }))
    setActivePreset(null) // Clear active preset when manual change
  }

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const categoryMetrics = useMemo(() => {
    const calculateMetrics = (data) => {
      let totalOriginalCost = 0
      let totalSelectedCost = 0
      let functionalSum = 0
      let designSum = 0
      let count = 0

      data.forEach(group => {
        const selected = selections[group.materialId]
        if (!selected) return

        totalOriginalCost += parseFloat(selected.ORIGINAL_TOTAL_COST || selected.ORIGINAL_COST || 0)
        totalSelectedCost += parseFloat(selected.ALT_TOTAL_COST_TOTAL || selected.ALT_COST_TOTAL || 0)
        functionalSum += parseFloat(selected.FUNCTIONAL_SCORE || 5)
        designSum += parseFloat(selected.DESIGN_SCORE || 5)
        count++
      })

      return {
        totalOriginalCost,
        totalSelectedCost,
        totalSavings: totalOriginalCost - totalSelectedCost,
        savingsPercent: totalOriginalCost > 0 ? ((totalOriginalCost - totalSelectedCost) / totalOriginalCost * 100) : 0,
        avgFunctional: count > 0 ? functionalSum / count : 0,
        avgDesign: count > 0 ? designSum / count : 0
      }
    }

    return {
      windows: calculateMetrics(windowData),
      doors: calculateMetrics(doorData),
      appliances: calculateMetrics(applianceData)
    }
  }, [windowData, doorData, applianceData, selections])

  if (loading) {
    return (
      <div className="app">
        <Header user={user} onLogout={handleLogout} />
        <div className="loading">
          <div className="loading-spinner"></div>
          <p>Loading materials data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <Header user={user} onLogout={handleLogout} />
      
      <Chat />

      <div className="app-container">
        {/* Sidebar */}
        <div className="sidebar">
          <ProjectInfo />
          
          <PresetButtons 
            onApplyPreset={applyPreset}
            activePreset={activePreset}
          />
        </div>

        {/* Main Content - Materials */}
        <div className="main-panel">
          <OverallSummary
            windowData={windowData}
            doorData={doorData}
            applianceData={applianceData}
            selections={selections}
          />
          
          <main className="materials-section">
          {/* Windows */}
          <CategoryTile
            icon="🪟"
            title="Windows"
            count={windowData.length}
            metrics={categoryMetrics.windows}
            isExpanded={expandedSections.windows}
            onClick={() => toggleSection('windows')}
          />
          {expandedSections.windows && (
            <div className="materials-grid">
              {windowData.map(group => (
                <MaterialCard
                  key={group.materialId}
                  group={group}
                  selected={selections[group.materialId]}
                  onSelect={(alt) => handleSelectionChange(group.materialId, alt)}
                />
              ))}
            </div>
          )}

          {/* Doors */}
          <CategoryTile
            icon="🚪"
            title="Doors"
            count={doorData.length}
            metrics={categoryMetrics.doors}
            isExpanded={expandedSections.doors}
            onClick={() => toggleSection('doors')}
          />
          {expandedSections.doors && (
            <div className="materials-grid">
              {doorData.map(group => (
                <MaterialCard
                  key={group.materialId}
                  group={group}
                  selected={selections[group.materialId]}
                  onSelect={(alt) => handleSelectionChange(group.materialId, alt)}
                />
              ))}
            </div>
          )}

          {/* Appliances */}
          <CategoryTile
            icon="🍳"
            title="Appliances"
            count={applianceData.length}
            metrics={categoryMetrics.appliances}
            isExpanded={expandedSections.appliances}
            onClick={() => toggleSection('appliances')}
          />
          {expandedSections.appliances && (
            <div className="materials-grid">
              {applianceData.map(group => (
                <MaterialCard
                  key={group.materialId}
                  group={group}
                  selected={selections[group.materialId]}
                  onSelect={(alt) => handleSelectionChange(group.materialId, alt)}
                />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  </div>
  )
}

export default App

