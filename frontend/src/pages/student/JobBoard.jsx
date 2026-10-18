import { useEffect, useState } from 'react'
import api, { fmtDate } from '../../api'
import Layout from '../../components/Layout'
import StatusBadge from '../../components/StatusBadge'

// Student home page: one card per approved company, each with an Apply button.
export default function JobBoard() {
  const [data, setData] = useState(null)
  const [applyFor, setApplyFor] = useState(null) // { company, role }
  const [message, setMessage] = useState('')

  const load = async () => {
    const res = await api.get('/student/board/')
    setData(res.data)
  }
  useEffect(() => { load() }, [])

  const done = (text) => {
    setApplyFor(null)
    setMessage(text)
    load()
  }

  if (!data) return <Layout><p className="empty-state">Loading companies…</p></Layout>

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Welcome, {data.student.full_name}</div>
          <h1>Companies hiring on campus</h1>
        </div>
      </div>

      {message && <div className="success-note">{message}</div>}

      {data.companies.length === 0 ? (
        <div className="empty-state">No approved companies yet. Check back soon.</div>
      ) : (
        <div className="company-grid">
          {data.companies.map((c) => (
            <div className="company-card" key={c.id}>
              <div className="company-card-head">
                <div className="company-logo">{c.company_name.slice(0, 1)}</div>
                <div>
                  <h3>{c.company_name}</h3>
                  {c.website && <a href={c.website} target="_blank" rel="noreferrer" className="company-link">{c.website.replace(/^https?:\/\//, '')}</a>}
                </div>
              </div>
              {c.description && <p className="job-desc">{c.description}</p>}

              {c.roles.length === 0 ? (
                <p className="muted">No open roles right now.</p>
              ) : (
                c.roles.map((r) => (
                  <div className="role-row" key={r.id}>
                    <div className="role-info">
                      <strong>{r.title}</strong>
                      <div className="job-meta">
                        <span>{r.package}</span>
                        {r.location && <span>{r.location}</span>}
                        <span>CGPA ≥ {r.min_cgpa}</span>
                        <span>{r.eligible_branches}</span>
                        <span>Apply by {fmtDate(r.deadline)}</span>
                      </div>
                    </div>
                    <div className="role-action">
                      {r.application_status ? (
                        <StatusBadge status={r.application_status} />
                      ) : r.eligible ? (
                        <button className="btn brass small" onClick={() => setApplyFor({ company: c, role: r })}>Apply</button>
                      ) : (
                        <span className="muted" title={r.not_eligible_reason}>Not eligible</span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          ))}
        </div>
      )}

      {applyFor && (
        <ApplyModal
          company={applyFor.company}
          role={applyFor.role}
          student={data.student}
          onClose={() => setApplyFor(null)}
          onDone={done}
        />
      )}
    </Layout>
  )
}

function ApplyModal({ company, role, student, onClose, onDone }) {
  const [form, setForm] = useState({
    phone: student.phone || '',
    resume_link: student.resume_link || '',
    cover_note: '',
  })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      await api.post(`/jobs/${role.id}/apply/`, form)
      onDone(`Applied to ${company.company_name} for ${role.title}. You can track it under My Applications.`)
    } catch (err) {
      const d = err.response?.data
      setError(d?.detail || (d ? Object.values(d).flat().join(' ') : 'Could not submit the application.'))
      setBusy(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Apply to {company.company_name}</h2>
        <p className="auth-sub">{role.title} · {role.package}</p>
        <form onSubmit={submit}>
          <div className="field"><label>Phone number</label><input value={form.phone} onChange={update('phone')} required maxLength={15} /></div>
          <div className="field"><label>Resume link (Google Drive / LinkedIn)</label><input type="url" value={form.resume_link} onChange={update('resume_link')} placeholder="https://" required /></div>
          <div className="field"><label>Why are you interested? (optional)</label><textarea rows={3} value={form.cover_note} onChange={update('cover_note')} /></div>
          {error && <p className="error-msg">{error}</p>}
          <div className="modal-actions">
            <button type="button" className="btn outline" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn brass" disabled={busy}>{busy ? 'Submitting…' : 'Submit application'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}
