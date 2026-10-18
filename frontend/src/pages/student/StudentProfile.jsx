import { useEffect, useState } from 'react'
import api from '../../api'
import Layout from '../../components/Layout'

export default function StudentProfile() {
  const [profile, setProfile] = useState(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.get('/students/me/').then((res) => setProfile(res.data))
  }, [])

  const update = (key) => (e) => setProfile({ ...profile, [key]: e.target.value })

  const save = async (e) => {
    e.preventDefault()
    const { data } = await api.put('/students/me/', profile)
    setProfile(data)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  if (!profile) return <Layout><p className="empty-state">Loading…</p></Layout>

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Keep This Current</div>
          <h1>My Profile</h1>
        </div>
      </div>
      <div className="card">
        <form onSubmit={save}>
          <div className="form-grid">
            <div className="field"><label>Full name</label><input value={profile.full_name} onChange={update('full_name')} /></div>
            <div className="field"><label>Roll number</label><input value={profile.roll_number} disabled /></div>
            <div className="field"><label>Branch</label><input value={profile.branch} onChange={update('branch')} /></div>
            <div className="field"><label>Graduation year</label><input type="number" value={profile.graduation_year} onChange={update('graduation_year')} /></div>
            <div className="field"><label>CGPA</label><input type="number" step="0.01" value={profile.cgpa} onChange={update('cgpa')} /></div>
            <div className="field"><label>Phone</label><input value={profile.phone} onChange={update('phone')} /></div>
          </div>
          <div className="field"><label>Resume link (Drive/Dropbox URL)</label><input value={profile.resume_link} onChange={update('resume_link')} /></div>
          <div className="field"><label>Skills (comma separated)</label><textarea rows={2} value={profile.skills} onChange={update('skills')} /></div>
          <button className="btn brass" type="submit">Save changes</button>
          {saved && <span style={{ marginLeft: 12, fontSize: 13, color: 'var(--good)' }}>Saved.</span>}
        </form>
      </div>
    </Layout>
  )
}
