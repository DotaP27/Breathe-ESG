import React, {useState} from 'react'
import api from '../utils/api'

export default function Ingest(){
  const [file, setFile] = useState(null)
  const [msg, setMsg] = useState('')
  const [detectedSource, setDetectedSource] = useState('')

  const upload = async ()=>{
    if(!file) return setMsg('Select a file')
    const form = new FormData()
    form.append('file', file)
    form.append('tenant_id', 1)
    const res = await api.postFile('/api/ingestion/upload/', form)
    const payload = await res.json()
    if(res.ok){
      setDetectedSource(payload.source_type || '')
      setMsg(`Uploaded: ${payload.parsed_rows} rows (${payload.source_type})`)
    } else {
      setMsg(payload.error || 'Upload failed')
    }
  }

  const onFileChange = (e)=>{
    const picked = e.target.files && e.target.files[0]
    setFile(picked || null)
    setDetectedSource('')
    setMsg('')
  }

  return (
    <div>
      <h2>Ingest</h2>
      <div style={{marginTop:8}}>
        <input type="file" accept=".csv,.txt,.pdf" onChange={onFileChange} />
        <div className="muted" style={{marginTop:6}}>Accepted files: CSV, TXT, PDF</div>
      </div>
      {detectedSource && <div style={{marginTop:8}}><strong>Detected source:</strong> {detectedSource}</div>}
      <div style={{marginTop:8}}>
        <button onClick={upload}>Upload</button>
      </div>
      <div style={{marginTop:8}}>{msg}</div>
    </div>
  )
}
