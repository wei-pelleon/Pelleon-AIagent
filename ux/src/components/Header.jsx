import './Header.css'

function Header({ user, onLogout }) {
  return (
    <header className="app-header">
      <div className="header-content">
        <div className="header-left">
          <h1>VE Agent</h1>
          <p className="subtitle">Value Engineering Optimizer</p>
        </div>
        
        {user && (
          <div className="header-right">
            <div className="user-info">
              <span className="user-icon">👤</span>
              <span className="user-name">{user.username || user.email}</span>
            </div>
            <button className="logout-button" onClick={onLogout}>
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header


