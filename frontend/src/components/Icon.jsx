import React from 'react'

export default function Icon({name, size=16, className=''}){
  const common = { width: size, height: size, viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' }
  switch(name){
    case 'dashboard':
      return (
        <svg {...common} className={className}><rect x="3" y="3" width="8" height="8" stroke="currentColor" strokeWidth="1.5"/><rect x="13" y="3" width="8" height="5" stroke="currentColor" strokeWidth="1.5"/><rect x="13" y="10" width="8" height="11" stroke="currentColor" strokeWidth="1.5"/><rect x="3" y="13" width="8" height="11" stroke="currentColor" strokeWidth="1.5"/></svg>
      )
    case 'upload':
      return (
        <svg {...common} className={className}><path d="M12 3v10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M5 10l7-7 7 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M21 21H3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
      )
    case 'review':
      return (
        <svg {...common} className={className}><circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.5"/><path d="M9.5 12.5l1.8 1.8L15 10.6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
      )
    case 'audit':
      return (
        <svg {...common} className={className}><rect x="3" y="4" width="18" height="6" stroke="currentColor" strokeWidth="1.5"/><rect x="3" y="14" width="18" height="6" stroke="currentColor" strokeWidth="1.5"/></svg>
      )
    case 'tenants':
      return (
        <svg {...common} className={className}><path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" stroke="currentColor" strokeWidth="1.5"/><path d="M3 21a9 9 0 0 1 18 0" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
      )
    default:
      return null
  }
}
