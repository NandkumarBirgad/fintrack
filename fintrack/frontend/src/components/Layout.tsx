import { useAuth } from '../context/AuthContext';
import { NavLink, useNavigate, Outlet } from 'react-router-dom';
import { Activity, Wallet, TrendingUp, Users, LogOut, User } from 'lucide-react';
import './Layout.css';

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="layout-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar glass-panel">
        <div className="brand">
          <div className="brand-icon"><Activity size={24}/></div>
          <h2>FinTrack</h2>
        </div>
        
        <nav className="nav-menu">
          <NavLink to="/dashboard" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
            <Wallet size={20}/> Dashboard
          </NavLink>
          <NavLink to="/transactions" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
            <TrendingUp size={20}/> Transactions
          </NavLink>
          {user.role !== 'viewer' && (
            <NavLink to="/analytics" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <Activity size={20}/> Analytics
            </NavLink>
          )}
          {user.role === 'admin' && (
            <NavLink to="/users" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <Users size={20}/> Connect Users
            </NavLink>
          )}
        </nav>
        
        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="avatar"><User size={20} /></div>
            <div className="user-info">
              <span className="user-name">{user.name}</span>
              <span className="user-role">{user.role}</span>
            </div>
          </div>
          <button onClick={handleLogout} className="logout-btn" title="Logout">
            <LogOut size={18}/>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="layout-content">
        <Outlet />
      </main>
    </div>
  );
}
