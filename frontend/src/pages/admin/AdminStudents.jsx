import { useEffect, useState } from 'react'
import api from '../../api'
import Layout from '../../components/Layout'

export default function AdminStudents() {
  const [students, setStudents] = useState([])

  useEffect(() => {
    api.get('/admin/students/').then((res) => setStudents(res.data))
  }, [])

  return (
    <Layout>
      <div className="page-header">
        <div>
          <div className="eyebrow">Records</div>
          <h1>Students</h1>
        </div>
      </div>
      <div className="card">
        {students.length === 0 ? (
          <p className="empty-state">No students registered yet.</p>
        ) : (
          <table>
            <thead>
              <tr><th>Name</th><th>Roll No.</th><th>Branch</th><th>CGPA</th><th>Year</th><th>Status</th></tr>
            </thead>
            <tbody>
              {students.map((s) => (
                <tr key={s.id}>
                  <td>{s.full_name}</td>
                  <td>{s.roll_number}</td>
                  <td>{s.branch}</td>
                  <td>{s.cgpa}</td>
                  <td>{s.graduation_year}</td>
                  <td>{s.is_placed ? <span className="badge selected">placed</span> : <span className="badge applied">seeking</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </Layout>
  )
}
