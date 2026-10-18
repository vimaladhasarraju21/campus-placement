import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api'
import { useAuth } from '../context/AuthContext'

const BLANK = {
  username: '', password: '', email: '',
  company_name: '', website: '', description: '', hr_contact_name: '', hr_contact_phone: '',
}

export default function RegisterCompany() {
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
      const { data } = await api.post('/auth/register/company/', form)
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
        <h1>Company registration</h1>
        <p className="auth-sub">
          Recruiter accounts need placement-cell approval before job posts go live.
        </p>
        <form onSubmit={submit}>
          <div className="form-grid">
            <div className="field"><label>Company name</label><input value={form.company_name} onChange={update('company_name')} required /></div>
            <div className="field"><label>Website</label><input value={form.website} onChange={update('website')} /></div>
            <div className="field"><label>HR contact name</label><input value={form.hr_contact_name} onChange={update('hr_contact_name')} /></div>
            <div className="field"><label>HR contact phone</label><input value={form.hr_contact_phone} onChange={update('hr_contact_phone')} /></div>
            <div className="field"><label>Username</label><input value={form.username} onChange={update('username')} required /></div>
            <div className="field"><label>Email</label><input type="email" value={form.email} onChange={update('email')} /></div>
          </div>
          <div className="field"><label>About the company</label><textarea rows={3} value={form.description} onChange={update('description')} /></div>
          <div className="field"><label>Password</label><input type="password" value={form.password} onChange={update('password')} required /></div>
          {error && <p className="error-msg">{error}</p>}
          <button className="btn brass" type="submit" disabled={busy} style={{ width: '100%', marginTop: 8 }}>
            {busy ? 'Creating account…' : 'Create company account'}
          </button>
        </form>
        <p className="auth-switch">Already registered? <Link to="/login">Sign in</Link></p>
      </div>
    </div>
  )
}
