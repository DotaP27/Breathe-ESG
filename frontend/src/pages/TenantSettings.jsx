import React, {useEffect, useState} from 'react'
import api from '../utils/api'
import { useParams } from 'react-router-dom'

export default function TenantSettings(){
  const { tenantId: paramId } = useParams()
  const tenantId = paramId || 1
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [values, setValues] = useState({
    FLIGHT_KG_PER_KM: '', TRAIN_KG_PER_KM: '', HOTEL_KG_PER_NIGHT: '', LHV_LITERS_TO_KWH_DIESEL: ''
  })

  useEffect(()=>{ fetchConfig() }, [tenantId])

  const fetchConfig = async ()=>{
    setLoading(true)
    const res = await api.get(`/api/tenants/${tenantId}/config/`)
    if(res.ok){
      const j = await res.json()
      setValues({
        FLIGHT_KG_PER_KM: j.FLIGHT_KG_PER_KM || '',
        TRAIN_KG_PER_KM: j.TRAIN_KG_PER_KM || '',
        HOTEL_KG_PER_NIGHT: j.HOTEL_KG_PER_NIGHT || '',
        LHV_LITERS_TO_KWH_DIESEL: j.LHV_LITERS_TO_KWH_DIESEL || ''
      })
    }
    setLoading(false)
  }

  const onChange = (k,v)=> setValues(s=>({...s, [k]: v}))

  const save = async ()=>{
    setSaving(true)
    const payload = {}
    Object.keys(values).forEach(k=>{ if(values[k]!=='' && values[k]!==null) payload[k]=values[k] })
    const res = await api.put(`/api/tenants/${tenantId}/config/`, payload)
    if(res.ok){
      await fetchConfig()
    }
    setSaving(false)
  }

  return (
    <div style={{maxWidth:640}}>
      <h2>Tenant Emission Factors</h2>
      <div className="card">
        {loading ? <div className="empty">Loading...</div> : (
          <div>
            <div className="form-field">
              <label>Flight (kg CO₂ / km)</label>
              <input value={values.FLIGHT_KG_PER_KM} onChange={e=>onChange('FLIGHT_KG_PER_KM', e.target.value)} />
            </div>
            <div className="form-field">
              <label>Train (kg CO₂ / km)</label>
              <input value={values.TRAIN_KG_PER_KM} onChange={e=>onChange('TRAIN_KG_PER_KM', e.target.value)} />
            </div>
            <div className="form-field">
              <label>Hotel (kg CO₂ / night)</label>
              <input value={values.HOTEL_KG_PER_NIGHT} onChange={e=>onChange('HOTEL_KG_PER_NIGHT', e.target.value)} />
            </div>
            <div className="form-field">
              <label>Diesel LHV (kWh / litre)</label>
              <input value={values.LHV_LITERS_TO_KWH_DIESEL} onChange={e=>onChange('LHV_LITERS_TO_KWH_DIESEL', e.target.value)} />
            </div>
            <div className="row">
              <button className="btn" onClick={save} disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
              <button className="btn-outline" onClick={fetchConfig}>Reload</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
