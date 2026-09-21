import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  const [data, setData] = useState(null);
  const [region, setRegion] = useState('');
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [refresh, setRefresh] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError('');
    const timer = setTimeout(async () => {
      try {
        const params = new URLSearchParams({ region, q: search });
        const response = await fetch(`/api/dashboard?${params}`, { signal: controller.signal });
        if (!response.ok) throw new Error(`Unable to load local authorities (HTTP ${response.status}).`);
        const result = await response.json();
        if (!controller.signal.aborted) setData(result);
      } catch (err) {
        if (!controller.signal.aborted) setError(err.message);
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }, 200);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [region, search, refresh]);

  const report = data?.pipeline;
  return (
    <main>
      <header>
        <div className="eyebrow">TT INTERVIEW <span>/</span> DATA EXPLORER</div>
        <h1>Local authorities.<br />Across England.</h1>
        <p>Explore local authority districts and regions from the Office for National Statistics.</p>
        <span className="badge">ONS geography · December 2024</span>
      </header>

      <section className="workspace" aria-label="Local authority explorer">
        <div className="section-heading">
          <div><h2>Local authorities</h2><p>Search a place or authority code.</p></div>
          <button onClick={() => setRefresh(value => value + 1)} disabled={loading}>Refresh view</button>
        </div>
        <div className="filters">
          <label>Search<input type="search" placeholder="Try Bristol or reading…" value={search} onChange={event => setSearch(event.target.value)} /></label>
          <label>Region<select value={region} onChange={event => setRegion(event.target.value)}>
            <option value="">All regions</option>
            {data?.regions.map(item => <option key={item.code} value={item.code}>{item.name}</option>)}
          </select></label>
        </div>
        {error && <p className="notice error" role="alert">{error} Check that Docker is running, then refresh the view.</p>}
        {loading && <p role="status">Loading local authorities…</p>}
        {data && !loading && !error && <>
          <div className="stats">
            <div><span>Local authorities shown</span><strong>{data.summary.authority_count}</strong></div>
            <div><span>Regions shown</span><strong>{data.summary.region_count}</strong></div>
          </div>
          <div className="table-wrap">
            <table>
              <caption className="sr-only">ONS local authority districts and regions</caption>
              <thead><tr><th scope="col">Local authority</th><th scope="col">Authority code</th><th scope="col">Region</th><th scope="col">Region code</th></tr></thead>
              <tbody>{data.authorities.map(authority => <tr key={authority.code}>
                <td><strong>{authority.name}</strong></td><td>{authority.code}</td>
                <td>{authority.region_name}</td><td>{authority.region_code}</td>
              </tr>)}</tbody>
            </table>
            {data.authorities.length === 0 && <p className="empty">No local authorities match these filters. Try another search or region.</p>}
          </div>
        </>}
      </section>

      {report && <section className="quality" aria-label="Data quality">
        <div className="section-heading"><h2>Behind the data</h2><span className="badge">{report.geography_source === 'live' ? 'Live API' : 'Previous import'}</span></div>
        <p>{report.authority_count} local authorities · {report.region_count ?? data.regions.length} regions</p>
        <p className="muted">Geography: {report.geography_vintage}. Last successful import: {new Date(report.loaded_at).toLocaleString('en-GB')}.</p>
      </section>}
      <footer>Source: <a href="https://www.ons.gov.uk/methodology/geography/licences">Office for National Statistics licensed under the Open Government Licence v.3.0</a>.</footer>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
