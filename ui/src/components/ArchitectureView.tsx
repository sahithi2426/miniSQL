import { useTheme } from '../theme';

export function ArchitectureView() {
  const { C } = useTheme();
  const aotStages = [
    { label: 'Lexer', strike: false },
    { label: 'Parser', strike: false },
    { label: 'Semantic', strike: false },
    { label: 'Logical Plan', strike: false },
    { label: 'C Codegen', strike: true },
    { label: 'gcc compile', strike: true },
    { label: 'exec binary', strike: true },
  ];

  const newStages = [
    { label: 'Lexer', highlight: false },
    { label: 'Parser', highlight: false },
    { label: 'Semantic', highlight: false },
    { label: 'Logical Plan', highlight: false },
    { label: 'Optimizer', highlight: true },
    { label: 'Physical Plan', highlight: true },
    { label: 'Volcano Exec', highlight: true },
  ];

  const cards = [
    {
      title: 'Storage Manager',
      desc: 'Manages persistent data files on disk. Each table is a file segmented into fixed 4KB pages. The DiskManager handles raw I/O operations — reading and writing page blocks to the filesystem.',
    },
    {
      title: 'Buffer Pool Manager',
      desc: 'An LRU-based caching layer sitting between disk and execution. Fetches pages into a finite set of memory frames, pins active pages, and evicts cold pages to stay within memory limits.',
    },
    {
      title: 'Volcano Iterator Model',
      desc: 'A pull-based execution model where every operator exposes init(), next(), close(). The root operator pulls tuples upward through the tree — enabling elegant pipelining without materializing intermediate results.',
    },
    {
      title: 'Logical Optimizer',
      desc: 'Rewrites the logical plan before execution. Performs predicate pushdown (moving filters below joins) and cost-based join reordering using catalog statistics to minimize tuple flow.',
    },
  ];

  return (
    <div style={{ padding: '24px', overflowY: 'auto', height: '100%', animation: 'fadeIn 0.15s ease' }}>

      {/* Pipeline Comparison */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ fontFamily: "'Geist', sans-serif", fontWeight: 500, fontSize: '13px', color: C.hi, marginBottom: '18px' }}>
          Execution Pipeline Evolution
        </div>

        {/* AOT Pipeline */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '10px', color: C.red, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '10px', fontFamily: "'Geist Mono', monospace" }}>
            Original AOT System
          </div>
          <div style={{ display: 'flex', gap: '4px', alignItems: 'center', flexWrap: 'wrap' }}>
            {aotStages.map((s, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <div style={{
                  padding: '6px 12px', borderRadius: '2px', fontSize: '11px',
                  fontFamily: "'Geist Mono', monospace", fontWeight: 500,
                  background: s.strike ? 'rgba(248,113,113,0.06)' : C.elevated,
                  border: `0.5px solid ${s.strike ? 'rgba(248,113,113,0.2)' : C.border}`,
                  color: s.strike ? C.red : C.hi,
                  textDecoration: s.strike ? 'line-through' : 'none',
                  opacity: s.strike ? 0.5 : 1,
                }}>
                  {s.label}
                </div>
                {i < aotStages.length - 1 && <span style={{ color: C.lo, fontSize: '11px', fontFamily: "'Geist Mono', monospace" }}>──▶</span>}
              </div>
            ))}
          </div>
        </div>

        {/* New Pipeline */}
        <div>
          <div style={{ fontSize: '10px', color: C.accent, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '10px', fontFamily: "'Geist Mono', monospace" }}>
            Redesigned DBMS System
          </div>
          <div style={{ display: 'flex', gap: '4px', alignItems: 'center', flexWrap: 'wrap' }}>
            {newStages.map((s, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <div style={{
                  padding: '6px 12px', borderRadius: '2px', fontSize: '11px',
                  fontFamily: "'Geist Mono', monospace", fontWeight: 500,
                  background: s.highlight ? C.accentDim : C.elevated,
                  border: `0.5px solid ${s.highlight ? 'rgba(0,212,170,0.2)' : C.border}`,
                  color: s.highlight ? C.accent : C.hi,
                }}>
                  {s.label}
                </div>
                {i < newStages.length - 1 && <span style={{ color: C.lo, fontSize: '11px', fontFamily: "'Geist Mono', monospace" }}>──▶</span>}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Architecture Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '20px' }}>
        {cards.map((card, i) => (
          <div key={i} style={{
            background: C.elevated, border: `0.5px solid ${C.border}`, borderRadius: '3px', padding: '18px',
            borderLeft: `1.5px solid ${C.accent}`, borderLeftColor: `rgba(0,212,170,${0.2 + i * 0.15})`,
          }}>
            <div style={{ fontFamily: "'Geist', sans-serif", fontWeight: 500, fontSize: '13px', color: C.hi, marginBottom: '8px' }}>{card.title}</div>
            <div style={{ fontSize: '12px', color: C.mid, lineHeight: '1.7', fontFamily: "'Geist', sans-serif" }}>{card.desc}</div>
          </div>
        ))}
      </div>

      {/* Why AOT Was Wrong */}
      <div style={{ borderLeft: `1.5px solid ${C.red}`, paddingLeft: '16px' }}>
        <div style={{ fontFamily: "'Geist', sans-serif", fontWeight: 500, fontSize: '13px', color: C.red, marginBottom: '12px' }}>
          Why AOT Compilation Was Fundamentally Wrong
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {[
            { title: 'Ephemeral Data', desc: 'Data is embedded as C arrays inside the compiled binary. When the program exits, the entire dataset vanishes — zero persistence.' },
            { title: 'Recompile on INSERT', desc: 'Every INSERT requires rewriting the entire .c source file and invoking gcc/clang again — a full system compilation for a single row addition.' },
            { title: 'No Transaction Isolation', desc: 'Without a storage abstraction layer, there is no mechanism for concurrent access, locking, or ACID guarantees.' },
          ].map((item, i) => (
            <div key={i} style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
              <span style={{ color: C.red, fontSize: '11px', marginTop: '2px', fontFamily: "'Geist Mono', monospace" }}>✗</span>
              <div>
                <span style={{ fontSize: '12px', fontWeight: 500, color: C.hi, fontFamily: "'Geist', sans-serif" }}>{item.title}: </span>
                <span style={{ fontSize: '12px', color: C.mid, fontFamily: "'Geist', sans-serif" }}>{item.desc}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
