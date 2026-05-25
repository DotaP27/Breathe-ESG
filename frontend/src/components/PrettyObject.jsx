import React from 'react'

export default function PrettyObject({obj, level=0}){
  if(obj === null || obj === undefined) return <div className="muted">—</div>
  if(Array.isArray(obj)){
    if(obj.length===0) return <div className="muted">[]</div>
    return (
      <div className="kv-list">
        {obj.map((it, i) => (
          <div className="kv-row" key={i} style={{paddingLeft: level*10}}>
            <div className="kv-key">[{i}]</div>
            <div className="kv-value">{typeof it === 'object' ? <PrettyObject obj={it} level={level+1} /> : String(it)}</div>
          </div>
        ))}
      </div>
    )
  }
  if(typeof obj === 'object'){
    const keys = Object.keys(obj)
    if(keys.length===0) return <div className="muted">{"{}"}</div>
    return (
      <div className="kv-list">
        {keys.map(k => (
          <div className="kv-row" key={k} style={{paddingLeft: level*10}}>
            <div className="kv-key">{k}</div>
            <div className="kv-value">{typeof obj[k] === 'object' ? <PrettyObject obj={obj[k]} level={level+1} /> : String(obj[k])}</div>
          </div>
        ))}
      </div>
    )
  }
  return <span>{String(obj)}</span>
}
