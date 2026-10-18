import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NAV_BY_ROLE = {
  student: [
    { to: '/student', label: 'Companies' },
    { to: '/student/applications', label: 'My Applications' },
    { to: '/student/profile', label: 'My Profile' },
  ],
  company: [
    { to: '/company', label: 'My Status' },
    { to: '/company/jobs', label: 'My Job Postings' },
    { to: '/company/profile', label: 'Company Profile' },
  ],
  admin: [
    { to: '/admin', label: 'Dashboard & Reports' },
    { to: '/admin/students', label: 'Students' },
    { to: '/admin/companies', label: 'Companies' },
  ],
}

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const links = NAV_BY_ROLE[user?.role] || []

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          Placement Register
          <span>CAMPUS PLACEMENT SYSTEM</span>
        </div>
        <nav>
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === '/student' || l.to === '/company' || l.to === '/admin'}
              className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          Signed in as<br /><strong>{user?.username}</strong>
          <button className="logout-btn" onClick={logout}>Log out</button>
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  )
}
