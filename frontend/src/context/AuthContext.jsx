import React, {createContext, useState, useEffect} from 'react'

const AuthContext = createContext()

export function AuthProvider({children}){
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const check = async ()=>{
    const token = localStorage.getItem('access_token')
    if(!token){ setUser(null); setLoading(false); return }
    try{
      const res = await fetch((import.meta.env.VITE_API_BASE||'http://127.0.0.1:8000') + '/api/me/', { headers: { 'Authorization': `Bearer ${token}` } })
      if(!res.ok){ localStorage.removeItem('access_token'); setUser(null); setLoading(false); return }
      const j = await res.json()
      setUser(j)
    }catch(e){ setUser(null) }
    setLoading(false)
  }

  useEffect(()=>{ check() }, [])

  const login = (token)=>{
    localStorage.setItem('access_token', token)
    return check()
  }
  const logout = ()=>{ localStorage.removeItem('access_token'); setUser(null) }

  return <AuthContext.Provider value={{user, loading, check, login, logout}}>{children}</AuthContext.Provider>
}

export default AuthContext
