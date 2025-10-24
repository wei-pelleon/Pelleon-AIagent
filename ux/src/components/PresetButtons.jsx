import './PresetButtons.css'

function PresetButtons({ onApplyPreset, activePreset }) {
  const presets = [
    {
      key: 'best_functional_cost',
      label: 'Functional + Cost',
      description: 'Max functional with cost savings',
      icon: '🎯'
    },
    {
      key: 'best_cost_only',
      label: 'Max Savings',
      description: 'Highest cost reduction',
      icon: '💰'
    },
    {
      key: 'best_design_cost',
      label: 'Design + Cost',
      description: 'Max design with cost savings',
      icon: '🎨'
    },
    {
      key: 'balanced',
      label: 'Balanced',
      description: 'Equal weight (1/3 each)',
      icon: '⚖️'
    }
  ]

  return (
    <div className="preset-buttons-container">
      <div className="preset-buttons-header">
        <h3>Quick Presets</h3>
        <p>Auto-select optimized alternatives</p>
      </div>
      
      <div className="preset-buttons-grid">
        {presets.map(preset => (
          <button
            key={preset.key}
            className={`preset-button ${activePreset === preset.key ? 'active' : ''}`}
            onClick={() => onApplyPreset(preset.key)}
          >
            <div className="preset-icon">{preset.icon}</div>
            <div className="preset-content">
              <div className="preset-label">{preset.label}</div>
              <div className="preset-description">{preset.description}</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

export default PresetButtons

