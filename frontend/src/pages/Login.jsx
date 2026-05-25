import React, {useState, useContext} from 'react'
import { useNavigate } from 'react-router-dom'
import AuthContext from '../context/AuthContext'

export default function Login(){
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()
  const { login } = useContext(AuthContext)

  const submit = async (e)=>{
    e.preventDefault()
    setLoading(true)
    setError(null)
    try{
      if(isRegister){
        const r = await fetch((import.meta.env.VITE_API_BASE||'http://127.0.0.1:8000') + '/api/register/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, email, password })
        })
        if(!r.ok){
          const t = await r.text()
          throw new Error(t || 'Register failed')
        }
        const j = await r.json()
        await login(j.access)
        navigate('/')
        return
      }

      const res = await fetch((import.meta.env.VITE_API_BASE||'http://127.0.0.1:8000') + '/api/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })
      if(!res.ok){
        const t = await res.text()
        throw new Error(t || 'Login failed')
      }
      const j = await res.json()
      await login(j.access)
      navigate('/')
    }catch(err){
      setError(err.message)
    }finally{ setLoading(false) }
  }

  return (
    <div style={{display:'flex', alignItems:'center', justifyContent:'center', minHeight:'60vh'}}>
      <div className="card" style={{width:420}}>
        <h2 style={{marginTop:0}}>Welcome back</h2>
        <p className="muted">Sign in to continue to Breathe ESG</p>
        <form onSubmit={submit}>
          <div className="form-field">
            <label>Username</label>
            <input value={username} onChange={e=>setUsername(e.target.value)} placeholder="username" />
          </div>
          {isRegister && (
            <div className="form-field">
              <label>Email</label>
              <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com" />
            </div>
          )}
          <div className="form-field">
            <label>Password</label>
            <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="password" />
          </div>
          <div className="row">
            <button className="btn" disabled={loading} type="submit">{loading ? (isRegister? 'Registering...':'Signing in...') : (isRegister? 'Create account' : 'Sign in')}</button>
            <button type="button" className="btn-outline" onClick={() => { setUsername('tester'); setPassword('pass'); }}>{isRegister? 'Fill demo' : 'Use demo'}</button>
          </div>
          <div style={{marginTop:8}}>
            <a href="#" onClick={(e)=>{e.preventDefault(); setIsRegister(!isRegister); setError(null)}}>{isRegister? 'Already have an account? Sign in' : 'New here? Create an account'}</a>
          </div>
          {error && (
            <div className="muted" style={{ color: 'red', marginTop: 8 }}>{error}</div>
          )}
        </form>
      </div>
    </div>
  )
}
