import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { QueryGraph } from './components/QueryGraph';
import { StorageMonitor } from './components/StorageMonitor';
import { CatalogView } from './components/CatalogView';
import { ArchitectureView } from './components/ArchitectureView';
import { PipelineView } from './components/PipelineView';
import { useTheme } from './theme';

const QUICK_QUERIES = [
  { label: 'Create Schema', sql: "CREATE TABLE Orders (id INT, customer_id INT);\nCREATE TABLE Customers (id INT, name TEXT);" },
  { label: 'Insert Data', sql: "INSERT INTO Customers VALUES (1, 'Alice');\nINSERT INTO Customers VALUES (2, 'Bob');\nINSERT INTO Orders VALUES (101, 1);\nINSERT INTO Orders VALUES (102, 1);\nINSERT INTO Orders VALUES (103, 2);" },
  { label: 'Basic Select', sql: "SELECT * FROM Orders;" },
  { label: 'Where Filter', sql: "SELECT * FROM Orders WHERE id > 101;" },
  { label: 'Inner Join', sql: "SELECT o.id, c.name FROM Orders o INNER JOIN Customers c ON o.customer_id = c.id;" },
  { label: 'Group & Having', sql: "SELECT customer_id, COUNT(*) FROM Orders GROUP BY customer_id HAVING COUNT(*) > 1;" },
  { label: 'Order & Limit', sql: "SELECT * FROM Orders ORDER BY customer_id DESC LIMIT 2;" },
  { label: 'Update Row', sql: "UPDATE Orders SET customer_id = 999 WHERE id = 101;" },
  { label: 'Delete Row', sql: "DELETE FROM Orders WHERE id = 102;" },
  { label: 'Truncate Table', sql: "TRUNCATE TABLE Orders;" },
  { label: 'Drop Tables', sql: "DROP TABLE Orders;\nDROP TABLE Customers;" },
  { label: 'Rishi Insert', sql: "INSERT INTO Customers VALUES (99, 'Rishi');" },
  { label: 'Rishi Select', sql: "SELECT * FROM Customers WHERE name = 'Rishi';" },
];

type MainTab = 'query' | 'storage' | 'catalog' | 'architecture';
type ResultTab = 'results' | 'plan' | 'algebra' | 'timings' | 'pipeline';

export default function App() {
  const { C, isDark, toggle } = useTheme();
  const [mainTab, setMainTab] = useState<MainTab>('query');
  const [resultTab, setResultTab] = useState<ResultTab>('results');
  const [query, setQuery] = useState("SELECT * FROM Orders;");
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [apiReady, setApiReady] = useState(false);
  const [queryCount, setQueryCount] = useState(0);
  const [catalog, setCatalog] = useState<{ tables: any[] }>({ tables: [] });
  const [sidebarCollapsed, setSidebarCollapsed] = useState<Record<string, boolean>>({});

  useEffect(() => {
    axios.get('/catalog').then(() => setApiReady(true)).catch(() => setApiReady(false));
  }, []);

  const fetchCatalog = async () => {
    try { const res = await axios.get('/catalog'); setCatalog(res.data); setApiReady(true); }
    catch { setApiReady(false); }
  };

  useEffect(() => { fetchCatalog(); }, []);

  const handleRun = useCallback(async () => {
    setLoading(true);
    setResponse(null);
    const statements = query.split(';').map(s => s.trim()).filter(s => s.length > 0);
    let lastResponse: any = null;
    try {
      for (const stmt of statements) {
        lastResponse = (await axios.post('/query', { query: stmt + ';' })).data;
      }
      setResponse(lastResponse);
      setQueryCount(prev => prev + 1);
      fetchCatalog();
    } catch (e: any) {
      setResponse({ status: 'error', message: e.response?.data?.detail || e.message });
    }
    setLoading(false);
  }, [query]);

  const toggleSidebar = (name: string) => {
    setSidebarCollapsed(prev => ({ ...prev, [name]: !prev[name] }));
  };

  const totalTime = response?.timings
    ? (Object.values(response.timings) as number[]).reduce((a, b) => a + (Number(b) || 0), 0).toFixed(2)
    : null;

  // ─── TAB BUTTONS ───
  const mainTabs: { id: MainTab; label: string }[] = [
    { id: 'query', label: 'Query Editor' },
    { id: 'storage', label: 'Storage' },
    { id: 'catalog', label: 'Catalog' },
    { id: 'architecture', label: 'Architecture' },
  ];

  const resultTabs: { id: ResultTab; label: string }[] = [
    { id: 'results', label: 'RESULTS' },
    { id: 'plan', label: 'PLAN TREE' },
    { id: 'algebra', label: 'REL. ALGEBRA' },
    { id: 'timings', label: 'TIMINGS' },
    { id: 'pipeline', label: 'PIPELINE' },
  ];

  // Timing bar helpers
  const timingStages = [
    { label: 'Parse', key: 'parse_ms', opacity: 0.2 },
    { label: 'Semantic', key: 'semantic_ms', opacity: 0.3 },
    { label: 'Logical', key: 'logical_ms', opacity: 0.4 },
    { label: 'Optimize', key: 'optimize_ms', opacity: 0.6 },
    { label: 'Execute', key: 'exec_ms', opacity: 1.0 },
  ];

  const planningMs = response?.timings
    ? (response.timings.parse_ms || 0) + (response.timings.semantic_ms || 0) + (response.timings.logical_ms || 0) + (response.timings.optimize_ms || 0)
    : 0;
  const execMs = response?.timings?.exec_ms || 0;
  const totalPlanExec = planningMs + execMs || 1;
  const planPct = (planningMs / totalPlanExec) * 100;

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', background: C.base, fontFamily: "'Geist', sans-serif", overflow: 'hidden', color: C.mid }}>

      {/* ════════ LEFT SIDEBAR ════════ */}
      <div style={{ width: '210px', minWidth: '210px', background: C.surface, borderRight: `0.5px solid ${C.border}`, display: 'flex', flexDirection: 'column', height: '100vh' }}>

        {/* Logo */}
        <div style={{ padding: '14px 16px', borderBottom: `0.5px solid ${C.border}`, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600, fontSize: '14px', color: C.hi }}>MiniSQL</span>
          <span style={{ fontSize: '10px', color: C.accent, fontFamily: "'Geist Mono', monospace", fontWeight: 500 }}>Studio</span>
        </div>

        {/* Schema Tree */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '12px' }}>
          <div style={{ fontSize: '10px', textTransform: 'uppercase', color: C.lo, fontWeight: 500, letterSpacing: '1px', marginBottom: '10px', fontFamily: "'Geist Mono', monospace" }}>
            Schema Explorer
          </div>

          {catalog.tables.map((table: any) => (
            <div key={table.name} style={{ marginBottom: '2px' }}>
              <button
                onClick={() => toggleSidebar(table.name)}
                style={{
                  width: '100%', padding: '6px 8px', fontSize: '12px',
                  textAlign: 'left', display: 'flex', alignItems: 'center', gap: '6px',
                  fontFamily: "'Geist', sans-serif", color: C.mid,
                }}
                onMouseOver={e => (e.currentTarget.style.color = C.hi)}
                onMouseOut={e => (e.currentTarget.style.color = C.mid)}
              >
                <span style={{ fontSize: '9px', color: C.lo, transition: 'transform 0.2s', transform: sidebarCollapsed[table.name] ? 'rotate(0deg)' : 'rotate(90deg)', display: 'inline-block' }}>›</span>
                <span style={{ fontWeight: 500, color: C.hi, flex: 1 }}>{table.name}</span>
                <span style={{ fontSize: '10px', color: C.lo, fontFamily: "'Geist Mono', monospace" }}>{table.rows}</span>
              </button>
              {!sidebarCollapsed[table.name] && (
                <div style={{ paddingLeft: '24px', animation: 'slideIn 0.15s ease' }}>
                  {table.columns.map((col: any) => (
                    <div key={col.name} style={{ fontSize: '11px', color: C.mid, padding: '2px 0', display: 'flex', justifyContent: 'space-between', fontFamily: "'Geist Mono', monospace" }}>
                      <span>{col.name}</span>
                      <span style={{ color: C.lo, fontSize: '10px' }}>{col.type}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          {/* Quick Queries */}
          <div style={{ fontSize: '10px', textTransform: 'uppercase', color: C.lo, fontWeight: 500, letterSpacing: '1px', marginTop: '20px', marginBottom: '10px', fontFamily: "'Geist Mono', monospace" }}>
            Quick Queries
          </div>
          {QUICK_QUERIES.map((q, i) => (
            <button
              key={i}
              onClick={() => { setQuery(q.sql); setMainTab('query'); }}
              style={{
                width: '100%', padding: '6px 10px', fontSize: '11px',
                textAlign: 'left', marginBottom: '1px', color: C.mid,
                fontFamily: "'Geist', sans-serif", transition: 'color 0.1s',
              }}
              onMouseOver={e => (e.currentTarget.style.color = C.accent)}
              onMouseOut={e => (e.currentTarget.style.color = C.mid)}
            >
              {q.label}
            </button>
          ))}
        </div>
      </div>

      {/* ════════ MAIN AREA ════════ */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>

        {/* ── TOP TAB BAR ── */}
        <div style={{ display: 'flex', alignItems: 'stretch', height: '38px', borderBottom: `0.5px solid ${C.border}`, background: C.surface }}>
          {mainTabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setMainTab(tab.id)}
              style={{
                background: 'transparent',
                borderBottom: mainTab === tab.id ? `1.5px solid ${C.accent}` : '1.5px solid transparent',
                color: mainTab === tab.id ? C.hi : C.lo,
                padding: '0 18px',
                fontSize: '12px',
                fontWeight: 500,
                fontFamily: "'Geist', sans-serif",
                transition: 'all 0.15s',
                borderRadius: 0,
              }}
            >
              {tab.label}
            </button>
          ))}

          <div style={{ marginLeft: 'auto', paddingRight: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              onClick={toggle}
              style={{
                background: C.elevated, border: `0.5px solid ${C.border}`, borderRadius: '4px',
                padding: '4px 10px', fontSize: '11px', cursor: 'pointer',
                color: C.hi, marginRight: '8px', display: 'flex', alignItems: 'center', gap: '6px',
                fontFamily: "'Geist', sans-serif", fontWeight: 500, transition: 'all 0.15s'
              }}
              onMouseOver={e => { e.currentTarget.style.borderColor = C.accent; e.currentTarget.style.color = C.accent; }}
              onMouseOut={e => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.color = C.hi; }}
            >
              {isDark ? (
                <><span style={{ fontSize: '14px' }}>☀️</span> Light</>
              ) : (
                <><span style={{ fontSize: '14px' }}>🌙</span> Dark</>
              )}
            </button>
            <div style={{
              width: '6px', height: '6px', borderRadius: '50%',
              background: apiReady ? C.green : C.red,
              animation: apiReady ? 'pulse 2s infinite' : undefined,
            }} />
            <span style={{ fontSize: '11px', color: apiReady ? C.green : C.red, fontFamily: "'Geist Mono', monospace", fontWeight: 400 }}>
              {apiReady ? 'API' : 'Offline'}
            </span>

            {response?.timings && totalTime && (
              <span style={{ fontSize: '11px', color: C.mid, fontFamily: "'Geist Mono', monospace" }}>
                · {totalTime}ms
              </span>
            )}
            {response?.rows && (
              <span style={{ fontSize: '11px', color: C.mid, fontFamily: "'Geist Mono', monospace" }}>
                · {response.rows.length} rows
              </span>
            )}
          </div>
        </div>

        {/* ── CONTENT ── */}
        <div style={{ flex: 1, overflow: 'hidden' }}>

          {/* ════════ QUERY EDITOR TAB ════════ */}
          {mainTab === 'query' && (
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>

              {/* Editor */}
              <div style={{ height: '38%', position: 'relative', background: C.base, borderBottom: `0.5px solid ${C.border}` }}>
                <div style={{ position: 'absolute', top: '12px', right: '12px', zIndex: 10 }}>
                  <button
                    onClick={handleRun}
                    disabled={loading}
                    style={{
                      background: C.accent, color: C.base, border: 'none',
                      padding: '7px 18px', borderRadius: '2px', cursor: loading ? 'wait' : 'pointer',
                      display: 'flex', alignItems: 'center', gap: '6px',
                      fontWeight: 600, fontSize: '12px', fontFamily: "'Geist', sans-serif",
                      opacity: loading ? 0.6 : 1, transition: 'opacity 0.15s',
                      boxShadow: '0 1px 2px rgba(0,0,0,0.5)',
                    }}
                  >
                    {loading ? '···' : '▶'} {loading ? 'Running' : 'Run'}
                  </button>
                </div>
                <textarea
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  onKeyDown={e => {
                    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); handleRun(); }
                  }}
                  placeholder="-- Write SQL here..."
                  spellCheck={false}
                  style={{
                    width: '100%', height: '100%', padding: '18px', paddingRight: '140px',
                    background: 'transparent', color: C.hi,
                    fontFamily: "'Geist Mono', monospace", fontSize: '13px', lineHeight: '1.8',
                    border: 'none', outline: 'none', resize: 'none',
                  }}
                />
              </div>

              {/* Results area */}
              <div style={{ height: '62%', display: 'flex', flexDirection: 'column', background: C.surface, overflow: 'hidden' }}>

                {/* Sub-tabs */}
                <div style={{ display: 'flex', alignItems: 'stretch', height: '34px', borderBottom: `0.5px solid ${C.border}`, background: C.base, gap: 0 }}>
                  {resultTabs.map(tab => (
                    <button
                      key={tab.id}
                      onClick={() => setResultTab(tab.id)}
                      style={{
                        background: 'transparent',
                        borderBottom: resultTab === tab.id ? `1.5px solid ${C.accent}` : '1.5px solid transparent',
                        color: resultTab === tab.id ? C.hi : C.lo,
                        padding: '0 14px',
                        fontSize: '10px',
                        fontWeight: 500,
                        fontFamily: "'Geist Mono', monospace",
                        letterSpacing: '0.3px',
                        transition: 'all 0.15s',
                        borderRadius: 0,
                      }}
                    >
                      {tab.label}
                    </button>
                  ))}
                  {response?.timings && (
                    <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', paddingRight: '14px', fontSize: '10px', fontFamily: "'Geist Mono', monospace", color: C.lo }}>
                      <span>parse: {response.timings.parse_ms}ms</span>
                      <span style={{ margin: '0 6px' }}>·</span>
                      <span>exec: {response.timings.exec_ms}ms</span>
                    </div>
                  )}
                </div>

                <div style={{ flex: 1, overflow: 'auto' }}>
                  {!response ? (
                    <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: C.lo, fontSize: '13px' }}>
                      —
                    </div>
                  ) : response.status === 'error' ? (
                    <div style={{ padding: '20px' }}>
                      <div style={{ borderLeft: `1.5px solid ${C.red}`, paddingLeft: '12px', color: C.red, fontFamily: "'Geist Mono', monospace", fontSize: '13px' }}>
                        {response.message}
                      </div>
                    </div>
                  ) : (
                    <>
                      {/* ── RESULTS TAB ── */}
                      {resultTab === 'results' && (
                        <div style={{ animation: 'fadeIn 0.15s ease' }}>
                          {response.message && !response.rows && (
                            <div style={{ padding: '20px', color: C.accent, fontFamily: "'Geist Mono', monospace", fontSize: '13px' }}>
                              ✓ {response.message}
                            </div>
                          )}
                          {response.rows && response.rows.length > 0 && (
                            <table style={{ width: '100%', textAlign: 'left' }}>
                              <thead>
                                <tr>
                                  {response.columns.map((col: string) => (
                                    <th key={col} style={{
                                      padding: '10px 16px', borderBottom: `0.5px solid ${C.border}`,
                                      position: 'sticky', top: 0, background: C.elevated,
                                    }}>{col}</th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {response.rows.map((row: any, i: number) => (
                                  <tr key={i} style={{ borderBottom: `0.5px solid ${C.border}` }}
                                    onMouseOver={e => (e.currentTarget.style.background = C.accentDim)}
                                    onMouseOut={e => (e.currentTarget.style.background = 'transparent')}
                                  >
                                    {response.columns.map((col: string) => (
                                      <td key={col} style={{ padding: '8px 16px' }}>
                                        {String(row[col])}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          )}
                          {response.rows && response.rows.length === 0 && (
                            <div style={{ padding: '20px', color: C.lo, fontFamily: "'Geist Mono', monospace", fontSize: '13px' }}>Empty set (0 rows)</div>
                          )}
                        </div>
                      )}

                      {/* ── PLAN TREE TAB ── */}
                      {resultTab === 'plan' && (
                        <div style={{ height: '100%', width: '100%' }}>
                          <QueryGraph plan={response.plan_tree} />
                        </div>
                      )}

                      {/* ── RELATIONAL ALGEBRA TAB ── */}
                      {resultTab === 'algebra' && (
                        <div style={{ padding: '20px', animation: 'fadeIn 0.15s ease' }}>
                          <div style={{ fontSize: '10px', textTransform: 'uppercase', color: C.lo, fontWeight: 500, letterSpacing: '0.5px', marginBottom: '12px', fontFamily: "'Geist Mono', monospace" }}>Relational Algebra Expression</div>
                          <div style={{
                            background: C.elevated, border: `0.5px solid ${C.border}`, borderRadius: '3px',
                            padding: '20px',
                          }}>
                            {response.ra_string
                              ? (() => {
                                  const segs = response.ra_string.split(/([\u251c\u2514\u2502\u2500]+)/g);
                                  return (
                                    <pre style={{ margin: 0, padding: 0, fontFamily: "'Geist Mono', monospace", fontSize: '13px', color: C.hi, lineHeight: '2', background: 'transparent', whiteSpace: 'pre', overflowX: 'auto' }}>
                                      {segs.map((seg: string, i: number) =>
                                        /^[\u251c\u2514\u2502\u2500]+$/.test(seg)
                                          ? <span key={i} style={{ color: C.lo }}>{seg}</span>
                                          : <span key={i}>{seg}</span>
                                      )}
                                    </pre>
                                  );
                                })()
                              : <span style={{ color: C.lo, fontFamily: "'Geist Mono', monospace", fontSize: '13px' }}>No relational algebra expression available for this query type.</span>
                            }
                          </div>
                        </div>
                      )}




                      {/* ── TIMINGS TAB ── */}
                      {resultTab === 'timings' && response.timings && (
                        <div style={{ padding: '20px', animation: 'fadeIn 0.15s ease' }}>
                          {/* Metric Cards */}
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '8px', marginBottom: '20px' }}>
                            {timingStages.map(m => (
                              <div key={m.key} style={{
                                background: C.elevated, border: `0.5px solid ${C.border}`, borderRadius: '3px',
                                padding: '14px', textAlign: 'center',
                              }}>
                                <div style={{ fontSize: '10px', color: C.lo, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px', fontFamily: "'Geist Mono', monospace" }}>{m.label}</div>
                                <div style={{ fontSize: '20px', fontWeight: 600, fontFamily: "'Geist Mono', monospace", color: C.hi }}>
                                  {response.timings[m.key]}
                                </div>
                                <div style={{ fontSize: '10px', color: C.lo, fontFamily: "'Geist Mono', monospace" }}>ms</div>
                              </div>
                            ))}
                          </div>

                          {/* Bar Chart */}
                          <div style={{ background: C.elevated, border: `0.5px solid ${C.border}`, borderRadius: '3px', padding: '20px', marginBottom: '16px' }}>
                            <div style={{ fontFamily: "'Geist', sans-serif", fontWeight: 500, fontSize: '12px', color: C.hi, marginBottom: '16px' }}>Execution Breakdown</div>
                            {timingStages.map(m => {
                              const val = response.timings[m.key] || 0;
                              const max = Math.max(...Object.values(response.timings).map(Number).filter((n: number) => !isNaN(n)), 1);
                              const pct = Math.max(2, (val / max) * 100);
                              return (
                                <div key={m.key} style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                                  <div style={{ width: '70px', fontSize: '11px', color: C.lo, fontFamily: "'Geist Mono', monospace", textAlign: 'right' }}>{m.label}</div>
                                  <div style={{ flex: 1, background: C.base, borderRadius: '2px', height: '12px', overflow: 'hidden' }}>
                                    <div style={{
                                      width: `${pct}%`, height: '100%',
                                      background: C.accent, opacity: m.opacity,
                                      borderRadius: '2px', transition: 'width 0.4s ease',
                                    }} />
                                  </div>
                                  <div style={{ width: '50px', fontSize: '11px', color: C.mid, fontFamily: "'Geist Mono', monospace" }}>{val}ms</div>
                                </div>
                              );
                            })}
                          </div>

                          {/* Optimization Impact */}
                          <div style={{ background: C.elevated, border: `0.5px solid ${C.border}`, borderRadius: '3px', padding: '20px' }}>
                            <div style={{ fontFamily: "'Geist Mono', monospace", fontWeight: 500, fontSize: '10px', color: C.lo, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '16px' }}>Optimization Impact</div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px', fontFamily: "'Geist Mono', monospace", fontSize: '12px' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span style={{ color: C.mid }}>Planning overhead</span>
                                <span style={{ color: C.hi }}>{planningMs.toFixed(2)}ms</span>
                              </div>
                              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span style={{ color: C.mid }}>Optimizer cost</span>
                                <span style={{ color: C.hi }}>{(response.timings.optimize_ms || 0).toFixed(2)}ms</span>
                              </div>
                              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span style={{ color: C.mid }}>Execution</span>
                                <span style={{ color: C.hi }}>{execMs.toFixed(2)}ms</span>
                              </div>
                            </div>
                            {/* Two-segment bar */}
                            <div style={{ display: 'flex', borderRadius: '2px', overflow: 'hidden', height: '14px', background: C.base }}>
                              <div style={{ width: `${planPct}%`, background: 'rgba(0,212,170,0.3)', transition: 'width 0.4s ease' }} />
                              <div style={{ width: `${100 - planPct}%`, background: C.accent, transition: 'width 0.4s ease' }} />
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px', fontSize: '10px', fontFamily: "'Geist Mono', monospace" }}>
                              <span style={{ color: C.lo }}>PLANNING</span>
                              <span style={{ color: C.lo }}>EXECUTION</span>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* ── PIPELINE TAB ── */}
                      {resultTab === 'pipeline' && (
                        <PipelineView response={response} query={query} />
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ════════ STORAGE MONITOR TAB ════════ */}
          {mainTab === 'storage' && <StorageMonitor queryCount={queryCount} />}

          {/* ════════ CATALOG TAB ════════ */}
          {mainTab === 'catalog' && <CatalogView />}

          {/* ════════ ARCHITECTURE TAB ════════ */}
          {mainTab === 'architecture' && <ArchitectureView />}
        </div>
      </div>
    </div>
  );
}
