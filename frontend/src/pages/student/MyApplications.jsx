import { useEffect, useState } from 'react'
import api from '../../api'
import Layout from '../../components/Layout'
import StatusBadge from '../../components/StatusBadge'

export default function MyApplications() {
  const [apps, setApps] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/applications/mine/').then((res) => {
      setApps(res.data)
      setLoading(false)
    })
  }, [])

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Track Progress</div>
          <h1>My Applications</h1>
        </div>
      </div>

      {loading ? (
        <p className="empty-state">Loading…</p>
      ) : apps.length === 0 ? (
        <div className="empty-state">You haven't applied to any jobs yet.</div>
      ) : (
        <div className="card">
          <table>
            <thead>
              <tr><th>Job</th><th>Company</th><th>Applied on</th><th>Status</th></tr>
            </thead>
            <tbody>
              {apps.map((a) => (
                <tr key={a.id}>
                  <td>{a.job_title}</td>
                  <td>{a.company_name}</td>
                  <td>{new Date(a.applied_on).toLocaleDateString()}</td>
                  <td><StatusBadge status={a.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Layout>
  )
}
