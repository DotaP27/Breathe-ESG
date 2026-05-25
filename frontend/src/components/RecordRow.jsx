import React from 'react'
import api from '../utils/api'

export default function RecordRow({row, onAction}){
  const approve = async ()=>{
    const res = await api.post(`/api/records/${row.id}/approve/`)
    if(res.ok) onAction(row.id)
  }
  const flag = async ()=>{
    const res = await api.post(`/api/records/${row.id}/flag/`, {reason:'manual flag'})
    if(res.ok) onAction(row.id)
  }
  const reject = async ()=>{
    const res = await api.post(`/api/records/${row.id}/reject/`, {reason:'reject'})
    if(res.ok) onAction(row.id)
  }

  return (
    <div className="record card">
      <div className="meta">
        <div>ID #{row.id}</div>
        <div className="muted">{row.source_type}</div>
        <div className="muted">{row.created_at?.split('T')[0]}</div>
      </div>
      <div className="body">
        <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
          <div>
            <strong>{row.quantity_kwh} kWh</strong>
            <div className="muted">Status: {row.status}</div>
          </div>
          <div className="actions">
            <button className="btn-approve" onClick={approve}>Approve</button>
            <button className="btn-flag" onClick={flag}>Flag</button>
            <button className="btn-reject" onClick={reject}>Reject</button>
          </div>
        </div>
        <div style={{marginTop:10}}>
          <pre>{JSON.stringify(row.raw_data, null, 2)}</pre>
        </div>
      </div>
    </div>
  )
}
