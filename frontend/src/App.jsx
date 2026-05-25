import React from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Ingest from './pages/Ingest'
import ReviewQueue from './pages/ReviewQueue'
import AuditLog from './pages/AuditLog'
import Login from './pages/Login'
import TenantList from './pages/TenantList'
import TenantSettings from './pages/TenantSettings'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import { useContext } from 'react'
import AuthContext from './context/AuthContext'
import Icon from './components/Icon'

function AuthControls(){
  const { user, logout } = useContext(AuthContext)
  if(!user) return <Link to="/login">Login</Link>
  return (
    <>
      {user.is_staff && <Link to="/tenants">Tenants</Link>}
      <button className="btn" style={{marginLeft:8}} onClick={() => { logout(); window.location.href='/login' }}>Logout</button>
    </>
  )
}

export default function App(){
  return (
    <AuthProvider>
    <BrowserRouter>
      <div className="app-shell">
        <nav className="app-nav">
          <div className="brand"><span className="logo-mark">BE</span>Breathe ESG</div>
          <Link to="/"><Icon name="dashboard"/>Dashboard</Link>
          <Link to="/ingest"><Icon name="upload"/>Ingest</Link>
          <Link to="/review"><Icon name="review"/>Review</Link>
          <Link to="/audit"><Icon name="audit"/>Audit</Link>
          <Link to="/tenants"><Icon name="tenants"/>Tenants</Link>
          <div className="spacer" />
          <AuthControls />
        </nav>

        <div style={{marginTop:16}}>
          <Routes>
            <Route path="/login" element={<Login/>} />
            <Route path="/" element={<ProtectedRoute><Dashboard/></ProtectedRoute>} />
            <Route path="/ingest" element={<ProtectedRoute><Ingest/></ProtectedRoute>} />
            <Route path="/review" element={<ProtectedRoute><ReviewQueue/></ProtectedRoute>} />
            <Route path="/audit" element={<ProtectedRoute><AuditLog/></ProtectedRoute>} />
            <Route path="/tenants" element={<ProtectedRoute><TenantList/></ProtectedRoute>} />
            <Route path="/settings/:tenantId" element={<ProtectedRoute><TenantSettings/></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><TenantSettings/></ProtectedRoute>} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
    </AuthProvider>
  )
}
