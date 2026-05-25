import React, {useEffect, useState} from 'react'
import api from '../utils/api'
import { Link } from 'react-router-dom'

export default function TenantList(){
  const [tenants, setTenants] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(()=>{ fetchList() }, [])

  const fetchList = async ()=>{
    setLoading(true)
    setError(null)
    const res = await api.get('/api/tenants/')
    if(res.status === 403){ setError('Admin access required'); setLoading(false); return }
    if(res.ok){ setTenants(await res.json()) }
    else setError('Failed to load')
    setLoading(false)
  }

  return (
    <div>
      <h2>Tenants</h2>
      <div className="card">
        {loading && <div className="empty">Loading...</div>}
        {error && <div className="empty">{error}</div>}
        {!loading && !error && (
          <div>
            {tenants.map(t=> (
              <div key={t.id} style={{padding:8, borderBottom:'1px solid #f0f0f0'}}>
                <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                  <div>
                    <div style={{fontWeight:700}}>{t.name}</div>
                    <div className="muted">{t.slug}</div>
                  </div>
                  <div>
                    <Link className="btn-outline" to={`/settings/${t.id}`}>Edit</Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
