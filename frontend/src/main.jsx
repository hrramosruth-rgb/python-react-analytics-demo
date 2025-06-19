import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

const money = cents => new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(cents/100);

function App(){
  const [draft,setDraft] = useState({start:'',end:''});
  const [range,setRange] = useState({start:'',end:''});
  const [data,setData] = useState(null);
  const [loading,setLoading] = useState(true);
  const [error,setError] = useState('');
  useEffect(()=>{
    const controller=new AbortController();
    setLoading(true); setData(null); setError('');
    const query=new URLSearchParams(Object.entries(range).filter(([,value])=>value));
    fetch('/api/metrics?'+query,{signal:controller.signal}).then(async response=>{
      const body=await response.json();
      if(!response.ok) throw new Error(typeof body.detail==='string'?body.detail:'Use valid dates in chronological order.');
      return body;
    }).then(setData).catch(error=>{if(error.name!=='AbortError')setError(error.message)}).finally(()=>{if(!controller.signal.aborted)setLoading(false)});
    return ()=>controller.abort();
  },[range]);
  function filter(event){event.preventDefault(); setRange({...draft});}
  return <main className="shell">
    <aside><a className="brand" href="#overview"><span className="mark">f.</span>FIELDNOTE</a><p className="nav-label">WORKSPACE</p><a className="selected" href="#overview">◈ Overview</a><p className="aside-note">Independent portfolio demo<br/>Python + React<br/>Synthetic fixture data</p></aside>
    <section className="workspace" id="overview"><header><span>Analytics / Overview</span><span className="badge">LOCAL DEMO</span></header>
      <div className="heading"><div><p className="eyebrow">BUSINESS INTELLIGENCE</p><h1>A clearer view of delivery.</h1><p>Explore revenue from a small, reproducible sales fixture.</p></div><span className="live">● CSV dataset</span></div>
      <form className="filters" onSubmit={filter}><label>From<input type="date" value={draft.start} onChange={event=>setDraft({...draft,start:event.target.value})}/></label><label>Through<input type="date" value={draft.end} onChange={event=>setDraft({...draft,end:event.target.value})}/></label><button disabled={loading}>Apply period</button><button className="secondary" type="button" disabled={loading} onClick={()=>{setDraft({start:'',end:''});setRange({start:'',end:''})}}>All dates</button></form>
      <div aria-live="polite">{loading&&<p className="status">Loading metrics…</p>}{error&&<p role="alert" className="error">Could not load metrics: {error}</p>}</div>
      {data&&<><div className="metrics"><article><p>Total revenue</p><h2>{money(data.revenue_cents)}</h2><small>Exact totals, stored in cents</small></article><article><p>Orders</p><h2>{data.orders}</h2><small>One order per CSV record</small></article><article><p>Units delivered</p><h2>{data.units}</h2><small>Quantity across selected orders</small></article></div>
        {data.orders===0?<div className="card empty"><h2>No orders in this period</h2><p>Try the fixture range: {data.available_range?.start} through {data.available_range?.end}.</p></div>:<div className="panels"><section className="card"><div className="card-title"><h2>Revenue by day</h2><span>{data.daily.length} active days</span></div><p>Only days with sales appear below.</p><div className="bars">{data.daily.map(day=><div className="bar-row" key={day.date}><time dateTime={day.date}>{day.date}</time><div className="track" aria-hidden="true"><div style={{width:`${day.revenue_cents/Math.max(1,...data.daily.map(d=>d.revenue_cents))*100}%`}}/></div><strong>{money(day.revenue_cents)}</strong></div>)}</div></section><section className="card"><div className="card-title"><h2>Service mix</h2><span>By revenue</span></div><table><caption className="sr-only">Revenue and units per service</caption><thead><tr><th scope="col">Service</th><th scope="col">Units</th><th scope="col">Revenue</th></tr></thead><tbody>{data.products.map(product=><tr key={product.product}><th scope="row">{product.product}</th><td>{product.units}</td><td>{money(product.revenue_cents)}</td></tr>)}</tbody></table></section></div>}
      </>}
      <footer>Code created in October 2026 · Disclosed simulated development timeline · No real client data</footer>
    </section>
  </main>;
}
createRoot(document.getElementById('root')).render(<App/>);
