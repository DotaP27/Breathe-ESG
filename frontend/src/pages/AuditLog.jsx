import React, {useEffect, useState} from 'react'
import api, { API_BASE } from '../utils/api'
import PrettyObject from '../components/PrettyObject'

export default function AuditLog(){
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState({})

  useEffect(()=>{ fetchAudit() }, [])

  const fetchAudit = async ()=>{
    setLoading(true)
    const res = await api.get('/api/records/audit/?tenant_id=1')
    if(res.ok){
      const data = await res.json()
      setRows(data)
    }
    setLoading(false)
  }

  const toggle = (id)=>{
    setExpanded(prev => ({...prev, [id]: !prev[id]}))
  }

  const downloadCsv = async ()=>{
    const token = localStorage.getItem('access_token')
    const tenantParam = '?tenant_id=1'
    const res = await fetch(API_BASE + '/api/records/audit/export/' + tenantParam, { headers: token ? { 'Authorization': `Bearer ${token}` } : {} })
    if(!res.ok){ alert('Failed to download CSV'); return }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const now = new Date().toISOString().slice(0,10)
    a.download = `audit_tenant_1_${now}.csv`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      <h2>Audit Log</h2>
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <div />
        <div>
          <button className="btn" onClick={downloadCsv}>Download CSV</button>
        </div>
      </div>
      {loading && <div className="empty">Loading...</div>}
      {!loading && rows.length===0 && <div className="empty">No approved records</div>}

      {!loading && rows.length>0 && (
        <div style={{overflowX:'auto'}}>
          <table className="audit-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Source</th>
                <th>Source File / Ref</th>
                <th>Quantity (kWh)</th>
                <th>CO2e (kg)</th>
                <th>Reviewed By</th>
                <th>Reviewed At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(r => (
                <React.Fragment key={r.id}>
                  <tr>
                    <td>#{r.id}</td>
                    <td className="muted">{r.source_type}</td>
                    <td style={{maxWidth:260, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}}>{r.source_file || r.source_ref || '—'}</td>
                    <td>{r.quantity_kwh ?? '—'}</td>
                    <td>{r.co2e_kg ?? '—'}</td>
                    <td>{r.reviewed_by || '—'}</td>
                    <td className="muted">{r.reviewed_at ? new Date(r.reviewed_at).toLocaleString() : '—'}</td>
                    <td>
                      <button className="btn" onClick={()=>toggle(r.id)}>{expanded[r.id] ? 'Hide' : 'View'}</button>
                    </td>
                  </tr>
                  {expanded[r.id] && (
                    <tr className="details-row">
                      <td colSpan={8}>
                        <div style={{display:'flex', gap:12}}>
                          <div style={{flex:1}}>
                            <strong>Raw data</strong>
                            <div className="kv-container">
                              <PrettyObject obj={r.raw_data || {}} />
                            </div>
                          </div>
                          <div style={{flex:1}}>
                            <strong>Edit history</strong>
                            <div className="kv-container">
                              <PrettyObject obj={r.edit_history || []} />
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}


// PrettyObject moved to shared component
