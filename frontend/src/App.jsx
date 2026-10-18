import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'

import Login from './pages/Login'
import RegisterStudent from './pages/RegisterStudent'
import RegisterCompany from './pages/RegisterCompany'

import JobBoard from './pages/student/JobBoard'
import MyApplications from './pages/student/MyApplications'
import StudentProfile from './pages/student/StudentProfile'

import CompanyDashboard from './pages/company/CompanyDashboard'
import CompanyJobs from './pages/company/CompanyJobs'
import CompanyProfile from './pages/company/CompanyProfile'

import AdminOverview from './pages/admin/AdminOverview'
import AdminStudents from './pages/admin/AdminStudents'
import AdminCompanies from './pages/admin/AdminCompanies'

function RoleRoute({ role, children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="empty-state">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  if (user.role !== role) return <Navigate to="/" replace />
  return children
}

function HomeRedirect() {
  const { user, loading } = useAuth()
  if (loading) return <div className="empty-state">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  if (user.role === 'student') return <Navigate to="/student" replace />
  if (user.role === 'company') return <Navigate to="/company" replace />
  return <Navigate to="/admin" replace />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register/student" element={<RegisterStudent />} />
      <Route path="/register/company" element={<RegisterCompany />} />

      <Route path="/student" element={<RoleRoute role="student"><JobBoard /></RoleRoute>} />
      <Route path="/student/applications" element={<RoleRoute role="student"><MyApplications /></RoleRoute>} />
      <Route path="/student/profile" element={<RoleRoute role="student"><StudentProfile /></RoleRoute>} />

      <Route path="/company" element={<RoleRoute role="company"><CompanyDashboard /></RoleRoute>} />
      <Route path="/company/jobs" element={<RoleRoute role="company"><CompanyJobs /></RoleRoute>} />
      <Route path="/company/profile" element={<RoleRoute role="company"><CompanyProfile /></RoleRoute>} />

      <Route path="/admin" element={<RoleRoute role="admin"><AdminOverview /></RoleRoute>} />
      <Route path="/admin/students" element={<RoleRoute role="admin"><AdminStudents /></RoleRoute>} />
      <Route path="/admin/companies" element={<RoleRoute role="admin"><AdminCompanies /></RoleRoute>} />

      <Route path="/" element={<HomeRedirect />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}
