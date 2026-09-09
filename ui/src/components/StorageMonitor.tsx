import { useState, useEffect } from 'react';

import { useTheme } from '../theme';

interface CatalogTable {
  name: string;
  columns: { name: string; type: string }[];
  rows: number;
  primary_key: string | null;
  unique_keys: string[];
}

interface StorageMonitorProps {
  queryCount: number;
}

export function StorageMonitor({ queryCount }: StorageMonitorProps) {
  const { C } = useTheme();
  const [tables, setTables] = useState<CatalogTable[]>([]);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [tableRows, setTableRows] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch real catalog data
  const fetchCatalog = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/catalog');
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      setTables(data.tables || []);
      setError(null);
      // Auto-select first table if none selected
      if (!selectedTable && data.tables?.length > 0) {
        setSelectedTable(data.tables[0].name);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load catalog');
    } finally {
      setLoading(false);
    }
  };

  // Fetch rows for the selected table via a SELECT * query
  const fetchTableRows = async (tableName: string) => {
    try {
      const res = await fetch('http://127.0.0.1:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: `SELECT * FROM ${tableName};` }),
      });
      if (!res.ok) {
        setTableRows([]);
        return;
      }
      const data = await res.json();
      setTableRows(data.rows || []);
    } catch {
      setTableRows([]);
    }
  };

  useEffect(() => { fetchCatalog(); }, [queryCount]);

  useEffect(() => {
    if (selectedTable) fetchTableRows(selectedTable);
  }, [selectedTable, queryCount]);

  const selectedMeta = tables.find(t => t.name === selectedTable);
  const totalRows = tables.reduce((sum, t) => sum + t.rows, 0);
  const totalColumns = tables.reduce((sum, t) => sum + t.columns.length, 0);

  // Clean up type display: "TokenType.INT" -> "INT"
  const cleanType = (t: string) => t.replace('TokenType.', '');

  if (loading) {
    return (
      <div style={{ padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <div style={{ color: C.mid, fontFamily: "'Geist Mono', monospace", fontSize: '12px' }}>Loading catalog…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <div style={{ color: C.red, fontFamily: "'Geist Mono', monospace", fontSize: '12px' }}>Error: {error}</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', overflowY: 'auto', height: '100%', animation: 'fadeIn 0.15s ease' }}>

      {/* Metric Cards — Real Data */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', marginBottom: '20px' }}>
        {[
          { label: 'Tables', value: tables.length },
          { label: 'Total Rows', value: totalRows },
          { label: 'Total Columns', value: totalColumns },
          { label: 'Queries Run', value: queryCount },
        ].map((m, i) => (
          <div key={i} style={{ background: C.elevated, border: `0.5px solid ${C.border}`, borderRadius: '3px', padding: '14px' }}>
            <div style={{ fontSize: '10px', color: C.lo, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px', fontFamily: "'Geist Mono', monospace" }}>{m.label}</div>
            <div style={{ fontSize: '22px', fontWeight: 600, fontFamily: "'Geist Mono', monospace", color: C.hi }}>{m.value}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>

        {/* Table List — from real catalog */}
        <div style={{ background: C.elevated, border: `0.5px solid ${C.border}`, borderRadius: '3px', padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ fontFamily: "'Geist', sans-serif", fontWeight: 500, fontSize: '12px', color: C.hi }}>Tables in Catalog</div>
            <button
              onClick={fetchCatalog}
              style={{
                background: 'transparent', border: `0.5px solid ${C.border}`, color: C.mid,
                padding: '5px 12px', borderRadius: '2px', fontSize: '11px',
                fontFamily: "'Geist', sans-serif", fontWeight: 500, transition: 'all 0.15s', cursor: 'pointer',
              }}
              onMouseOver={e => { e.currentTarget.style.borderColor = C.accent; e.currentTarget.style.color = C.accent; }}
              onMouseOut={e => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.color = C.mid; }}
            >
              Refresh
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {tables.length === 0 && (
              <div style={{ color: C.lo, fontSize: '11px', fontFamily: "'Geist Mono', monospace", padding: '12px', textAlign: 'center' }}>
                No tables. Run a CREATE TABLE query first.
              </div>
            )}
            {tables.map((t) => (
              <div
                key={t.name}
                onClick={() => setSelectedTable(t.name)}
                style={{
                  background: selectedTable === t.name ? C.accentDim : C.base,
                  border: `0.5px solid ${selectedTable === t.name ? C.accent : C.border}`,
                  borderRadius: '2px', padding: '10px 12px', cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '12px', fontFamily: "'Geist Mono', monospace", color: selectedTable === t.name ? C.accent : C.hi, fontWeight: 500 }}>
                    {t.name}
                  </span>
                  <span style={{ fontSize: '10px', fontFamily: "'Geist Mono', monospace", color: C.lo }}>
                    {t.rows} row{t.rows !== 1 ? 's' : ''} · {t.columns.length} col{t.columns.length !== 1 ? 's' : ''}
                  </span>
                </div>
                {t.primary_key && (
                  <div style={{ fontSize: '10px', color: C.mid, fontFamily: "'Geist Mono', monospace", marginTop: '3px' }}>
                    PK: {t.primary_key}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Schema View — Real column info */}
        <div style={{ background: C.elevated, border: `0.5px solid ${C.border}`, borderRadius: '3px', padding: '20px' }}>
          <div style={{ fontFamily: "'Geist', sans-serif", fontWeight: 500, fontSize: '12px', color: C.hi, marginBottom: '16px' }}>
            {selectedMeta ? `Schema: ${selectedMeta.name}` : 'Select a Table'}
          </div>
          {selectedMeta ? (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  {['Column', 'Type', 'Constraints'].map(h => (
                    <th key={h} style={{ padding: '8px 14px', borderBottom: `0.5px solid ${C.border}`, textAlign: 'left', fontSize: '10px', color: C.lo, textTransform: 'uppercase', letterSpacing: '0.5px', fontFamily: "'Geist Mono', monospace" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {selectedMeta.columns.map((col) => {
                  const constraints: string[] = [];
                  if (selectedMeta.primary_key === col.name) constraints.push('PRIMARY KEY');
                  if (selectedMeta.unique_keys?.includes(col.name)) constraints.push('UNIQUE');
                  return (
                    <tr key={col.name} style={{ borderBottom: `0.5px solid ${C.border}` }}>
                      <td style={{ padding: '8px 14px', fontFamily: "'Geist Mono', monospace", fontSize: '12px', color: C.hi, fontWeight: 500 }}>{col.name}</td>
                      <td style={{ padding: '8px 14px', fontFamily: "'Geist Mono', monospace", fontSize: '12px', color: C.accent }}>{cleanType(col.type)}</td>
                      <td style={{ padding: '8px 14px', fontFamily: "'Geist Mono', monospace", fontSize: '11px', color: constraints.length > 0 ? C.green : C.lo }}>
                        {constraints.length > 0 ? constraints.join(', ') : '—'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <div style={{ color: C.lo, fontSize: '11px', fontFamily: "'Geist Mono', monospace", padding: '20px', textAlign: 'center' }}>
              ← Click a table to view its schema
            </div>
          )}
        </div>
      </div>

      {/* Row Data — Slotted Page Layout visualization using REAL data */}
      {selectedMeta && (
        <div style={{ marginTop: '16px', background: C.elevated, border: `0.5px solid ${C.border}`, borderRadius: '3px', padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', marginBottom: '16px' }}>
            <span style={{ fontFamily: "'Geist', sans-serif", fontWeight: 500, fontSize: '12px', color: C.hi }}>Stored Records</span>
            <span style={{ fontFamily: "'Geist Mono', monospace", fontSize: '11px', color: C.lo }}>
              {selectedMeta.name} — {tableRows.length} row{tableRows.length !== 1 ? 's' : ''}
            </span>
          </div>

          {tableRows.length === 0 ? (
            <div style={{ padding: '20px', textAlign: 'center', color: C.lo, fontFamily: "'Geist Mono', monospace", fontSize: '11px' }}>
              No rows in this table. Run an INSERT query to add data.
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ padding: '8px 14px', borderBottom: `0.5px solid ${C.border}`, textAlign: 'left', fontSize: '10px', color: C.lo, textTransform: 'uppercase', letterSpacing: '0.5px', fontFamily: "'Geist Mono', monospace", width: '60px' }}>Slot</th>
                  {selectedMeta.columns.map(col => (
                    <th key={col.name} style={{ padding: '8px 14px', borderBottom: `0.5px solid ${C.border}`, textAlign: 'left', fontSize: '10px', color: C.lo, textTransform: 'uppercase', letterSpacing: '0.5px', fontFamily: "'Geist Mono', monospace" }}>{col.name}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tableRows.map((row, i) => (
                  <tr key={i} style={{ borderBottom: `0.5px solid ${C.border}` }}>
                    <td style={{ padding: '8px 14px', fontFamily: "'Geist Mono', monospace", fontSize: '12px', color: C.mid, fontWeight: 500 }}>
                      [{i}]
                    </td>
                    {selectedMeta.columns.map(col => (
                      <td key={col.name} style={{ padding: '8px 14px', fontFamily: "'Geist Mono', monospace", fontSize: '12px', color: C.val }}>
                        {row[col.name] !== undefined ? String(row[col.name]) : '—'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
