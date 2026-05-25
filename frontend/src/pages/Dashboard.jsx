import React, {useEffect, useState, useContext} from 'react'
import api from '../utils/api'
import AuthContext from '../context/AuthContext'

export default function Dashboard(){
  const { user } = useContext(AuthContext)
  const [pending, setPending] = useState(0)
  const [approved, setApproved] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(()=>{ if(user) fetchCounts() }, [user])

  const fetchCounts = async ()=>{
    setLoading(true)
    try{
      const p = await api.get('/api/records/pending/?tenant_id=1')
      const a = await api.get('/api/records/audit/?tenant_id=1')
      const pj = p.ok ? await p.json() : []
      const aj = a.ok ? await a.json() : []
      setPending(pj.length)
      setApproved(aj.length)
    }catch(e){}
    setLoading(false)
  }

  return (
    <div>
      <h2>Dashboard</h2>
      {(!user) && <div className="empty">Please sign in to see dashboard metrics.</div>}
      {user && (
        <div style={{display:'flex', gap:12}}>
          <div className="kpi card">
            <div className="muted">Pending records</div>
            <div style={{fontSize:24, fontWeight:700}}>{loading ? '...' : pending}</div>
          </div>
          <div className="kpi card">
            <div className="muted">Approved records</div>
            <div style={{fontSize:24, fontWeight:700}}>{loading ? '...' : approved}</div>
          </div>
        </div>
      )}
    </div>
  )
}
