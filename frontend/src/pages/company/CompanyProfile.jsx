import { useEffect, useState } from 'react'
import api from '../../api'
import Layout from '../../components/Layout'

export default function CompanyProfile() {
  const [profile, setProfile] = useState(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.get('/companies/me/').then((res) => setProfile(res.data))
  }, [])

  const update = (key) => (e) => setProfile({ ...profile, [key]: e.target.value })

  const save = async (e) => {
    e.preventDefault()
    const { data } = await api.put('/companies/me/', profile)
    setProfile(data)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  if (!profile) return <Layout><p className="empty-state">Loading…</p></Layout>

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Recruiter Details</div>
          <h1>Company Profile</h1>
        </div>
      </div>
      <div className="card">
        <p style={{ fontSize: 13, color: 'var(--slate)', marginBottom: 16 }}>
          Approval status: <strong style={{ color: profile.is_approved ? 'var(--good)' : profile.approval_status === 'rejected' ? 'var(--bad)' : 'var(--warn)' }}>
            {profile.is_approved ? 'Approved' : profile.approval_status === 'rejected' ? 'Not approved' : 'Pending review'}
          </strong>
        </p>
        <form onSubmit={save}>
          <div className="form-grid">
            <div className="field"><label>Company name</label><input value={profile.company_name} onChange={update('company_name')} /></div>
            <div className="field"><label>Website</label><input value={profile.website} onChange={update('website')} /></div>
            <div className="field"><label>HR contact name</label><input value={profile.hr_contact_name} onChange={update('hr_contact_name')} /></div>
            <div className="field"><label>HR contact phone</label><input value={profile.hr_contact_phone} onChange={update('hr_contact_phone')} /></div>
          </div>
          <div className="field"><label>About the company</label><textarea rows={3} value={profile.description} onChange={update('description')} /></div>
          <button className="btn brass" type="submit">Save changes</button>
          {saved && <span style={{ marginLeft: 12, fontSize: 13, color: 'var(--good)' }}>Saved.</span>}
        </form>
      </div>
    </Layout>
  )
}
