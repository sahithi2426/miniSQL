import { useState, useEffect } from 'react';
import axios from 'axios';

import { useTheme } from '../theme';

export function CatalogView() {
  const { C } = useTheme();
  const [catalog, setCatalog] = useState<{ tables: any[] }>({ tables: [] });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError(null);
    axios.get('/catalog')
      .then(res => { setCatalog(res.data); setLoading(false); })
      .catch(() => { setError('Cannot reach the MiniSQL API.'); setLoading(false); });
  }, []);

  if (loading) {
    return (
      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: C.lo, fontSize: '13px', fontFamily: "'Geist Mono', monospace" }}>
        Loading catalog...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '40px', animation: 'fadeIn 0.15s ease' }}>
        <div style={{ borderLeft: `1.5px solid ${C.red}`, paddingLeft: '16px' }}>
          <div style={{ color: C.red, fontFamily: "'Geist', sans-serif", fontWeight: 500, fontSize: '13px', marginBottom: '10px' }}>API Unreachable</div>
          <div style={{ color: C.mid, fontSize: '12px', marginBottom: '12px' }}>Make sure the FastAPI backend is running:</div>
          <div style={{ background: C.base, borderRadius: '2px', padding: '10px 14px', fontFamily: "'Geist Mono', monospace", fontSize: '12px', color: C.val, border: `0.5px solid ${C.border}` }}>
            uvicorn api:app --host 127.0.0.1 --port 8000 --reload
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', overflowY: 'auto', height: '100%', animation: 'fadeIn 0.15s ease' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', marginBottom: '20px' }}>
        <span style={{ fontFamily: "'Geist', sans-serif", fontWeight: 500, fontSize: '13px', color: C.hi }}>System Catalog</span>
        <span style={{ fontFamily: "'Geist Mono', monospace", fontSize: '11px', color: C.lo }}>
          {catalog.tables.length} table{catalog.tables.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
        {catalog.tables.map((table: any) => (
          <div key={table.name} style={{
            background: C.elevated, border: `0.5px solid ${C.border}`, borderRadius: '3px', padding: '16px',
          }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <span style={{ fontFamily: "'Geist', sans-serif", fontWeight: 500, fontSize: '13px', color: C.hi }}>{table.name}</span>
              <span style={{ fontSize: '11px', fontFamily: "'Geist Mono', monospace", color: C.lo }}>
                {table.rows} rows
              </span>
            </div>

            {/* Columns */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              {table.columns.map((col: any) => (
                <div key={col.name} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '5px 8px', background: C.base, borderRadius: '2px',
                }}>
                  <span style={{ fontFamily: "'Geist Mono', monospace", fontSize: '12px', color: C.mid }}>
                    {col.name}
                    {table.primary_key === col.name && <span style={{ marginLeft: '6px', fontSize: '10px', color: C.accent }}>PK</span>}
                  </span>
                  <span style={{ fontSize: '10px', fontFamily: "'Geist Mono', monospace", color: C.lo, textTransform: 'uppercase' }}>
                    {col.type}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
