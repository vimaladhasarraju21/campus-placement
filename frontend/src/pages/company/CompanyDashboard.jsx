import { useEffect, useState } from 'react'
import api, { fmtDate } from '../../api'
import Layout from '../../components/Layout'

// Company home: approval status first. If approved -> applicant numbers. If not -> the reason.
export default function CompanyDashboard() {
  const [d, setD] = useState(null)

  useEffect(() => {
    api.get('/companies/dashboard/').then((res) => setD(res.data))
  }, [])

  if (!d) return <Layout><p className="empty-state">Loading…</p></Layout>

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">{d.company_name}</div>
          <h1>Approval status</h1>
        </div>
      </div>

      {d.approval_status === 'pending' && (
        <div className="status-panel pending">
          <h3>Waiting for approval</h3>
          <p>The placement cell has not reviewed your company yet. Once approved you can post jobs and students can apply to you.</p>
        </div>
      )}

      {d.approval_status === 'rejected' && (
        <div className="status-panel rejected">
          <h3>Not approved</h3>
          <p><strong>Reason:</strong> {d.rejection_reason || 'No reason was recorded.'}</p>
          <p className="muted">Reviewed on {fmtDate(d.reviewed_on)}. Update your company profile and contact the placement cell to be reviewed again.</p>
        </div>
      )}

      {d.approval_status === 'approved' && (
        <>
          <div className="status-panel approved">
            <h3>Approved</h3>
            <p>Approved by the placement cell on <strong>{fmtDate(d.reviewed_on)}</strong>.</p>
          </div>

          <div className="stat-strip">
            <div className="stat-cell"><div className="num">{d.total_applicants}</div><div className="label">Students applied</div></div>
            <div className="stat-cell"><div className="num">{d.by_status.shortlisted}</div><div className="label">Shortlisted</div></div>
            <div className="stat-cell"><div className="num">{d.by_status.selected}</div><div className="label">Selected</div></div>
            <div className="stat-cell"><div className="num">{d.by_status.rejected}</div><div className="label">Rejected</div></div>
          </div>

          <div className="card">
            <h3>Applicants per job</h3>
            {d.jobs.length === 0 ? (
              <p className="empty-state">You have not posted any jobs yet. Go to “My Job Postings” to add one.</p>
            ) : (
              <table>
                <thead><tr><th>Job</th><th>Applicants</th></tr></thead>
                <tbody>{d.jobs.map((j) => <tr key={j.id}><td>{j.title}</td><td>{j.applicants}</td></tr>)}</tbody>
              </table>
            )}
          </div>
        </>
      )}
    </Layout>
  )
}
