import './ProjectInfo.css'

function ProjectInfo() {
  return (
    <div className="project-info">
      <div className="project-header">
        <div className="project-icon">🏢</div>
        <h3>Project Information</h3>
      </div>
      
      <div className="project-details">
        <div className="project-field">
          <div className="field-label">Project Name</div>
          <div className="field-value">Kushner Building 5</div>
        </div>

        <div className="project-field">
          <div className="field-label">Building Type</div>
          <div className="field-value">Multi-Family Residential</div>
        </div>

        <div className="project-field">
          <div className="field-label">Total Units</div>
          <div className="field-value">168 Units</div>
        </div>

        <div className="project-field">
          <div className="field-label">Total Area</div>
          <div className="field-value">135,963 sq ft</div>
        </div>

        <div className="project-field">
          <div className="field-label">Floors</div>
          <div className="field-value">Ground + 5 Floors</div>
        </div>
      </div>
    </div>
  )
}

export default ProjectInfo


