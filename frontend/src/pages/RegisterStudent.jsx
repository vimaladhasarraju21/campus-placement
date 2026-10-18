import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api'
import { useAuth } from '../context/AuthContext'

const BLANK = {
  username: '', password: '', email: '',
  full_name: '', roll_number: '', branch: '', graduation_year: 2026, cgpa: '', phone: '',
}

export default function RegisterStudent() {
  const [form, setForm] = useState(BLANK)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const { refresh } = useAuth()
  const navigate = useNavigate()

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      const { data } = await api.post('/auth/register/student/', form)
      localStorage.setItem('access', data.tokens.access)
      localStorage.setItem('refresh', data.tokens.refresh)
      await refresh()
      navigate('/')
    } catch (err) {
      setError(err.response?.data ? JSON.stringify(err.response.data) : 'Registration failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card" style={{ maxWidth: 560 }}>
        <h1>Student registration</h1>
        <p className="auth-sub">Create your placement profile.</p>
        <form onSubmit={submit}>
          <div className="form-grid">
            <div className="field"><label>Full name</label><input value={form.full_name} onChange={update('full_name')} required /></div>
            <div className="field"><label>Roll number</label><input value={form.roll_number} onChange={update('roll_number')} required /></div>
            <div className="field"><label>Branch</label><input placeholder="CSE / IT / ECE…" value={form.branch} onChange={update('branch')} required /></div>
            <div className="field"><label>Graduation year</label><input type="number" value={form.graduation_year} onChange={update('graduation_year')} required /></div>
            <div className="field"><label>CGPA</label><input type="number" step="0.01" value={form.cgpa} onChange={update('cgpa')} required /></div>
            <div className="field"><label>Phone</label><input value={form.phone} onChange={update('phone')} /></div>
            <div className="field"><label>Username</label><input value={form.username} onChange={update('username')} required /></div>
            <div className="field"><label>Email</label><input type="email" value={form.email} onChange={update('email')} /></div>
          </div>
          <div className="field"><label>Password</label><input type="password" value={form.password} onChange={update('password')} required /></div>
          {error && <p className="error-msg">{error}</p>}
          <button className="btn brass" type="submit" disabled={busy} style={{ width: '100%', marginTop: 8 }}>
            {busy ? 'Creating account…' : 'Create student account'}
          </button>
        </form>
        <p className="auth-switch">Already registered? <Link to="/login">Sign in</Link></p>
      </div>
    </div>
  )
}
