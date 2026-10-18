import { useEffect, useState } from 'react'
import api from '../../api'
import Layout from '../../components/Layout'
import { useAuth } from '../../context/AuthContext'
import StatusBadge from '../../components/StatusBadge'

const BLANK_JOB = {
  title: '', description: '', eligible_branches: '', min_cgpa: 0, package: '', location: '', deadline: '',
}

export default function CompanyJobs() {
  const { user, refresh } = useAuth()
  const [jobs, setJobs] = useState([])
  const [form, setForm] = useState(BLANK_JOB)
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')
  const [applicantsByJob, setApplicantsByJob] = useState({})
  const [openJobId, setOpenJobId] = useState(null)

  const isApproved = user?.profile?.is_approved

  const loadJobs = async () => {
    const { data } = await api.get('/jobs/')
    setJobs(data)
  }

  useEffect(() => { refresh(); loadJobs() }, [])

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  const submitJob = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/jobs/', form)
      setForm(BLANK_JOB)
      setShowForm(false)
      loadJobs()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not post job.')
    }
  }

  const toggleApplicants = async (jobId) => {
    if (openJobId === jobId) { setOpenJobId(null); return }
    setOpenJobId(jobId)
    if (!applicantsByJob[jobId]) {
      const { data } = await api.get(`/jobs/${jobId}/applicants/`)
      setApplicantsByJob((prev) => ({ ...prev, [jobId]: data }))
    }
  }

  const setStatus = async (applicationId, jobId, status) => {
    await api.patch(`/applications/${applicationId}/status/`, { status })
    const { data } = await api.get(`/jobs/${jobId}/applicants/`)
    setApplicantsByJob((prev) => ({ ...prev, [jobId]: data }))
  }

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Recruiting</div>
          <h1>My Job Postings</h1>
        </div>
        {isApproved && <button className="btn brass" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Post a job'}
        </button>}
      </div>

      {!isApproved && (
        <div className="pending-note">
          {user?.profile?.approval_status === 'rejected'
            ? `Your company was not approved: ${user.profile.rejection_reason || 'no reason recorded'}. You cannot post jobs.`
            : 'Your company account is awaiting approval from the placement cell. You can post jobs as soon as it is approved.'}
        </div>
      )}

      {showForm && (
        <div className="card">
          <h3>New job posting</h3>
          <form onSubmit={submitJob}>
            <div className="field"><label>Job title</label><input value={form.title} onChange={update('title')} required /></div>
            <div className="field"><label>Description</label><textarea rows={3} value={form.description} onChange={update('description')} required /></div>
            <div className="form-grid">
              <div className="field"><label>Eligible branches (comma separated, blank = all)</label><input value={form.eligible_branches} onChange={update('eligible_branches')} placeholder="CSE,IT" /></div>
              <div className="field"><label>Minimum CGPA</label><input type="number" step="0.01" value={form.min_cgpa} onChange={update('min_cgpa')} /></div>
              <div className="field"><label>Package</label><input value={form.package} onChange={update('package')} placeholder="6 LPA" required /></div>
              <div className="field"><label>Location</label><input value={form.location} onChange={update('location')} /></div>
              <div className="field"><label>Application deadline</label><input type="date" value={form.deadline} onChange={update('deadline')} required /></div>
            </div>
            {error && <p className="error-msg">{error}</p>}
            <button className="btn brass" type="submit">Publish job</button>
          </form>
        </div>
      )}

      {jobs.length === 0 ? (
        <div className="empty-state">No jobs posted yet.</div>
      ) : (
        jobs.map((job) => (
          <div className="card" key={job.id}>
            <h3>{job.title}</h3>
            <div className="job-meta">
              <span>Package: {job.package}</span>
              <span>Deadline: {job.deadline}</span>
              <span>Applicants: {job.applicant_count}</span>
              <span>{job.is_active ? 'Active' : 'Closed'}</span>
            </div>
            <p className="job-desc">{job.description}</p>
            <button className="btn outline small" onClick={() => toggleApplicants(job.id)}>
              {openJobId === job.id ? 'Hide applicants' : 'View applicants'}
            </button>

            {openJobId === job.id && (
              <div style={{ marginTop: 16 }}>
                {(applicantsByJob[job.id] || []).length === 0 ? (
                  <p className="empty-state">No applicants yet.</p>
                ) : (
                  <table>
                    <thead>
                      <tr><th>Student</th><th>Roll No.</th><th>Branch</th><th>CGPA</th><th>Resume</th><th>Status</th><th></th></tr>
                    </thead>
                    <tbody>
                      {applicantsByJob[job.id].map((a) => (
                        <tr key={a.id}>
                          <td>{a.student_name}</td>
                          <td>{a.roll_number}</td>
                          <td>{a.branch}</td>
                          <td>{a.cgpa}</td>
                          <td>{a.resume_link ? <a href={a.resume_link} target="_blank" rel="noreferrer">View</a> : '—'}</td>
                          <td><StatusBadge status={a.status} /></td>
                          <td>
                            <select
                              value={a.status}
                              onChange={(e) => setStatus(a.id, job.id, e.target.value)}
                              style={{ padding: '4px 8px', borderRadius: 6, border: '1px solid #cfc8b4' }}
                            >
                              <option value="applied">Applied</option>
                              <option value="shortlisted">Shortlisted</option>
                              <option value="selected">Selected</option>
                              <option value="rejected">Rejected</option>
                            </select>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}
          </div>
        ))
      )}
    </Layout>
  )
}
