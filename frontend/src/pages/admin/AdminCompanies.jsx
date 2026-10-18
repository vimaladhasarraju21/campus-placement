import { useEffect, useState } from 'react'
import api, { fmtDate } from '../../api'
import Layout from '../../components/Layout'

const BADGE = { approved: 'selected', pending: 'shortlisted', rejected: 'rejected' }

export default function AdminCompanies() {
  const [companies, setCompanies] = useState([])
  const [rejecting, setRejecting] = useState(null) // company being rejected
  const [reason, setReason] = useState('')
  const [error, setError] = useState('')

  const load = () => api.get('/admin/companies/').then((res) => setCompanies(res.data))
  useEffect(() => { load() }, [])

  const approve = async (c) => {
    await api.patch(`/admin/companies/${c.id}/review/`, { decision: 'approved' })
    load()
  }

  const reject = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.patch(`/admin/companies/${rejecting.id}/review/`, { decision: 'rejected', reason })
      setRejecting(null)
      setReason('')
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not reject.')
    }
  }

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Recruiters</div>
          <h1>Companies</h1>
        </div>
      </div>
      <div className="card">
        {companies.length === 0 ? (
          <p className="empty-state">No companies registered yet.</p>
        ) : (
          <table>
            <thead>
              <tr><th>Company</th><th>HR contact</th><th>Status</th><th>Reviewed on</th><th>Reason (if rejected)</th><th></th></tr>
            </thead>
            <tbody>
              {companies.map((c) => (
                <tr key={c.id}>
                  <td>
                    <strong>{c.company_name}</strong>
                    {c.website && <div className="small-text"><a href={c.website} target="_blank" rel="noreferrer">{c.website}</a></div>}
                  </td>
                  <td>{c.hr_contact_name || '—'}</td>
                  <td><span className={`badge ${BADGE[c.approval_status]}`}>{c.approval_status}</span></td>
                  <td>
                    {c.reviewed_on ? fmtDate(c.reviewed_on) : '—'}
                    {c.reviewed_by_name && <div className="muted small-text">by {c.reviewed_by_name}</div>}
                  </td>
                  <td className="small-text">{c.rejection_reason || '—'}</td>
                  <td style={{ whiteSpace: 'nowrap' }}>
                    {c.approval_status !== 'approved' && (
                      <button className="btn brass small" onClick={() => approve(c)}>Approve</button>
                    )}{' '}
                    {c.approval_status !== 'rejected' && (
                      <button className="btn outline small" onClick={() => { setRejecting(c); setReason(''); setError('') }}>Reject</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {rejecting && (
        <div className="modal-backdrop" onClick={() => setRejecting(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Reject {rejecting.company_name}</h2>
            <p className="auth-sub">The company will see this reason when they log in.</p>
            <form onSubmit={reject}>
              <div className="field">
                <label>Reason for rejection</label>
                <textarea rows={3} value={reason} onChange={(e) => setReason(e.target.value)} required autoFocus />
              </div>
              {error && <p className="error-msg">{error}</p>}
              <div className="modal-actions">
                <button type="button" className="btn outline" onClick={() => setRejecting(null)}>Cancel</button>
                <button type="submit" className="btn">Reject company</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Layout>
  )
}
