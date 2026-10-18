import { Fragment, useEffect, useState } from 'react'
import api, { downloadCsv, fmtDate } from '../../api'
import Layout from '../../components/Layout'
import StatusBadge from '../../components/StatusBadge'

export default function AdminOverview() {
  const [stats, setStats] = useState(null)
  const [tab, setTab] = useState('overall')

  useEffect(() => {
    api.get('/admin/stats/').then((res) => setStats(res.data))
  }, [])

  if (!stats) return <Layout><p className="empty-state">Loading…</p></Layout>

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Placement Cell</div>
          <h1>Dashboard &amp; Reports</h1>
        </div>
      </div>

      <div className="stat-strip">
        <div className="stat-cell"><div className="num">{stats.total_students}</div><div className="label">Students</div></div>
        <div className="stat-cell"><div className="num">{stats.placed_students}</div><div className="label">Placed</div></div>
        <div className="stat-cell"><div className="num">{stats.placement_rate}%</div><div className="label">Placement rate</div></div>
        <div className="stat-cell"><div className="num">{stats.total_companies}</div><div className="label">Approved companies</div></div>
        <div className="stat-cell"><div className="num">{stats.total_jobs}</div><div className="label">Jobs posted</div></div>
        <div className="stat-cell"><div className="num">{stats.total_applications}</div><div className="label">Applications</div></div>
      </div>

      <div className="tabs">
        <button className={'tab' + (tab === 'overall' ? ' active' : '')} onClick={() => setTab('overall')}>
          Report 1 · Overall (company-wise)
        </button>
        <button className={'tab' + (tab === 'students' ? ' active' : '')} onClick={() => setTab('students')}>
          Report 2 · Student-wise applications
        </button>
      </div>

      {tab === 'overall' ? <OverallReport /> : <StudentReport />}
    </Layout>
  )
}

function ReportToolbar({ generatedOn, csvPath, csvName }) {
  return (
    <div className="report-toolbar">
      <span className="muted">Generated {generatedOn}</span>
      <span>
        <button className="btn outline small" onClick={() => downloadCsv(csvPath, csvName)}>Download CSV</button>{' '}
        <button className="btn outline small" onClick={() => window.print()}>Print</button>
      </span>
    </div>
  )
}

// ---------------- Report 1 ----------------
function OverallReport() {
  const [r, setR] = useState(null)
  const [open, setOpen] = useState({})

  useEffect(() => {
    api.get('/admin/reports/overall/').then((res) => setR(res.data))
  }, [])

  if (!r) return <p className="empty-state">Loading report…</p>
  const s = r.summary
  const branches = Object.entries(r.branch_breakdown)

  return (
    <>
      <ReportToolbar generatedOn={r.generated_on} csvPath="/admin/reports/overall/" csvName="overall_placement_report.csv" />

      <div className="card">
        <h3>Summary</h3>
        <div className="summary-grid">
          <div><strong>{s.companies_total}</strong> companies — {s.companies_approved} approved, {s.companies_pending} pending, {s.companies_rejected} rejected</div>
          <div><strong>{s.total_jobs}</strong> jobs · <strong>{s.total_applications}</strong> applications</div>
          <div>Applied {s.applications_by_status.applied} · Shortlisted {s.applications_by_status.shortlisted} · Selected {s.applications_by_status.selected} · Rejected {s.applications_by_status.rejected}</div>
          <div><strong>{s.placed_students}</strong> of {s.total_students} students placed ({s.placement_rate}%)</div>
        </div>
      </div>

      <div className="card">
        <h3>Company-wise report</h3>
        {r.companies.length === 0 ? (
          <p className="empty-state">No companies registered yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Company</th><th>Status</th><th>Approved / reviewed on</th>
                <th>Jobs</th><th>Students applied</th><th>Shortlisted</th><th>Selected</th><th></th>
              </tr>
            </thead>
            <tbody>
              {r.companies.map((c) => (
                <Fragment key={c.id}>
                  <tr>
                    <td><strong>{c.company_name}</strong></td>
                    <td>
                      <span className={`badge ${c.approval_status === 'approved' ? 'selected' : c.approval_status === 'rejected' ? 'rejected' : 'shortlisted'}`}>
                        {c.approval_status}
                      </span>
                    </td>
                    <td>
                      {c.reviewed_on ? fmtDate(c.reviewed_on) : '—'}
                      {c.reviewed_by && <div className="muted small-text">by {c.reviewed_by}</div>}
                    </td>
                    <td>{c.jobs_posted}</td>
                    <td>{c.total_applicants}</td>
                    <td>{c.shortlisted}</td>
                    <td>{c.selected}</td>
                    <td>
                      {(c.applicants.length > 0 || c.rejection_reason) && (
                        <button className="btn outline small" onClick={() => setOpen({ ...open, [c.id]: !open[c.id] })}>
                          {open[c.id] ? 'Hide' : 'Details'}
                        </button>
                      )}
                    </td>
                  </tr>
                  {open[c.id] && (
                    <tr className="detail-row">
                      <td colSpan={8}>
                        {c.rejection_reason && <p className="reason-line"><strong>Rejection reason:</strong> {c.rejection_reason}</p>}
                        {c.applicants.length > 0 && (
                          <table className="inner-table">
                            <thead><tr><th>Student</th><th>Roll no.</th><th>Branch</th><th>CGPA</th><th>Role</th><th>Status</th><th>Applied on</th></tr></thead>
                            <tbody>
                              {c.applicants.map((a, i) => (
                                <tr key={i}>
                                  <td>{a.student_name}</td><td>{a.roll_number}</td><td>{a.branch}</td><td>{a.cgpa}</td>
                                  <td>{a.job_title}</td><td><StatusBadge status={a.status} /></td><td>{fmtDate(a.applied_on)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        )}
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h3>Placement by branch</h3>
        {branches.length === 0 ? (
          <p className="empty-state">No student data yet.</p>
        ) : (
          <table>
            <thead><tr><th>Branch</th><th>Total students</th><th>Placed</th><th>Rate</th></tr></thead>
            <tbody>
              {branches.map(([branch, b]) => (
                <tr key={branch}>
                  <td>{branch}</td><td>{b.total}</td><td>{b.placed}</td>
                  <td>{b.total ? Math.round((b.placed / b.total) * 100) : 0}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  )
}

// ---------------- Report 2 ----------------
function StudentReport() {
  const [r, setR] = useState(null)
  const [open, setOpen] = useState({})
  const [q, setQ] = useState('')

  useEffect(() => {
    api.get('/admin/reports/students/').then((res) => setR(res.data))
  }, [])

  if (!r) return <p className="empty-state">Loading report…</p>
  const s = r.summary
  const rows = r.students.filter((x) =>
    (x.full_name + x.roll_number + x.branch).toLowerCase().includes(q.toLowerCase()))

  return (
    <>
      <ReportToolbar generatedOn={r.generated_on} csvPath="/admin/reports/students/" csvName="student_applications_report.csv" />

      <div className="card">
        <h3>Summary</h3>
        <div className="summary-grid">
          <div><strong>{s.total_students}</strong> students registered</div>
          <div><strong>{s.students_applied}</strong> have applied · <strong>{s.students_not_applied}</strong> have not applied yet</div>
          <div><strong>{s.placed_students}</strong> placed</div>
        </div>
      </div>

      <div className="card">
        <div className="report-toolbar" style={{ marginBottom: 12 }}>
          <h3 style={{ margin: 0 }}>Student → companies applied</h3>
          <input className="search" placeholder="Search name, roll no., branch" value={q} onChange={(e) => setQ(e.target.value)} />
        </div>
        {rows.length === 0 ? (
          <p className="empty-state">No students found.</p>
        ) : (
          <table>
            <thead><tr><th>Student</th><th>Roll no.</th><th>Branch</th><th>CGPA</th><th>Applied to</th><th>Placed?</th><th></th></tr></thead>
            <tbody>
              {rows.map((st) => (
                <Fragment key={st.id}>
                  <tr>
                    <td><strong>{st.full_name}</strong></td>
                    <td>{st.roll_number}</td><td>{st.branch}</td><td>{st.cgpa}</td>
                    <td>
                      {st.total_applications === 0
                        ? <span className="muted">Not applied yet</span>
                        : [...new Set(st.applications.map((a) => a.company_name))].join(', ')}
                    </td>
                    <td>{st.is_placed ? <span className="badge selected">placed</span> : <span className="badge applied">seeking</span>}</td>
                    <td>
                      {st.total_applications > 0 && (
                        <button className="btn outline small" onClick={() => setOpen({ ...open, [st.id]: !open[st.id] })}>
                          {open[st.id] ? 'Hide' : 'Details'}
                        </button>
                      )}
                    </td>
                  </tr>
                  {open[st.id] && (
                    <tr className="detail-row">
                      <td colSpan={7}>
                        <table className="inner-table">
                          <thead><tr><th>Company</th><th>Role</th><th>Package</th><th>Status</th><th>Applied on</th></tr></thead>
                          <tbody>
                            {st.applications.map((a, i) => (
                              <tr key={i}>
                                <td>{a.company_name}</td><td>{a.job_title}</td><td>{a.package}</td>
                                <td><StatusBadge status={a.status} /></td><td>{fmtDate(a.applied_on)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  )
}
