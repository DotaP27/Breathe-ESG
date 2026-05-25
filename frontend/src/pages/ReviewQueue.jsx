import React, {useEffect, useState} from 'react'
import api from '../utils/api'
import PrettyObject from '../components/PrettyObject'

export default function ReviewQueue(){
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState({})

  useEffect(()=>{ fetchPending() }, [])

  const fetchPending = async ()=>{
    setLoading(true)
    const res = await api.get('/api/records/pending/?tenant_id=1')
    if(res.ok){
      const data = await res.json()
      setRows(data)
    }
    setLoading(false)
  }

  const onAction = (id)=>{
    setRows(rows.filter(r=>r.id!==id))
  }

  const toggle = (id)=> setExpanded(prev => ({...prev, [id]: !prev[id]}))

  const approve = async (id)=>{ const res = await api.post(`/api/records/${id}/approve/`); if(res.ok) onAction(id) }
  const flag = async (id)=>{ const res = await api.post(`/api/records/${id}/flag/`, {reason:'manual flag'}); if(res.ok) onAction(id) }
  const reject = async (id)=>{ const res = await api.post(`/api/records/${id}/reject/`, {reason:'reject'}); if(res.ok) onAction(id) }

  return (
    <div>
      <h2>Review Queue</h2>
      {loading && <div className="empty">Loading...</div>}
      {!loading && rows.length===0 && <div className="empty">No pending records</div>}

      {!loading && rows.length>0 && (
        <div style={{overflowX:'auto'}}>
          <table className="audit-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Source</th>
                <th>Ref</th>
                <th>Quantity (kWh)</th>
                <th>CO2e (kg)</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(r => (
                <React.Fragment key={r.id}>
                  <tr>
                    <td>#{r.id}</td>
                    <td className="muted">{r.source_type}</td>
                    <td style={{maxWidth:220, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}}>{r.source_file || r.source_ref || '—'}</td>
                    <td>{r.quantity_kwh ?? '—'}</td>
                    <td>{r.co2e_kg ?? '—'}</td>
                    <td className="muted">{r.created_at ? new Date(r.created_at).toLocaleString() : '—'}</td>
                    <td>
                      <div className="actions">
                        <button className="btn-approve" onClick={()=>approve(r.id)}>Approve</button>
                        <button className="btn-flag" onClick={()=>flag(r.id)}>Flag</button>
                        <button className="btn-reject" onClick={()=>reject(r.id)}>Reject</button>
                        <button className="btn" onClick={()=>toggle(r.id)}>{expanded[r.id] ? 'Hide' : 'View'}</button>
                      </div>
                    </td>
                  </tr>
                  {expanded[r.id] && (
                    <tr className="details-row">
                      <td colSpan={7}>
                        <div style={{display:'flex', gap:12}}>
                          <div style={{flex:1}}>
                            <strong>Raw data</strong>
                            <div className="kv-container"><PrettyObject obj={r.raw_data||{}} /></div>
                          </div>
                          <div style={{flex:1}}>
                            <strong>Notes</strong>
                            <div className="kv-container"><PrettyObject obj={r.edit_history||[]} /></div>
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
