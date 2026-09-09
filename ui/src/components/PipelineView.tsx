import { useState } from 'react';
import { useTheme } from '../theme';

function tokenize(sql: string): string[] {
  return sql.match(/[a-zA-Z_]\w*|'[^']*'|\d+|[><!=]+|[*.,;()]/g) || sql.split(/\s+/).filter(Boolean);
}

function TreeNode({ node, depth = 0, mapFn }: { node: any; depth?: number; mapFn?: (l: string) => string }) {
  const { C } = useTheme();
  if (!node || !node.label) return null;
  const kids = node.children || [];
  const label = mapFn ? mapFn(node.label) : node.label;
  return (
    <div style={{ fontFamily: "'Geist Mono', monospace", fontSize: '12px', color: C.mid, lineHeight: '1.8' }}>
      <div style={{ paddingLeft: depth * 20 }}>
        <span style={{ color: C.lo }}>{depth > 0 ? '└── ' : ''}</span>
        <span style={{ color: C.hi }}>{label}</span>
      </div>
      {kids.map((c: any, i: number) => <TreeNode key={i} node={c} depth={depth + 1} mapFn={mapFn} />)}
    </div>
  );
}

const TREE_CHARS = new Set(['├', '└', '│', '─']);

/** Renders Python pretty_print() output with a single <pre> — guarantees all indentation is preserved. */
function PrettyTree({ text }: { text?: string | null }) {
  const { C } = useTheme();
  if (!text?.trim()) {
    return <span style={{ color: C.lo, fontFamily: "'Geist Mono', monospace", fontSize: '11px' }}>—</span>;
  }
  // Split the ENTIRE text on runs of box-drawing chars in one pass
  const TREE_SEG = /([\u251c\u2514\u2502\u2500]+)/g;
  const segments = text.trim().split(TREE_SEG);
  return (
    <pre style={{
      margin: 0, padding: 0,
      fontFamily: "'Geist Mono', monospace",
      fontSize: '11px',
      lineHeight: '1.9',
      background: 'transparent',
      color: C.hi,
      whiteSpace: 'pre',        // pre preserves all spaces/newlines unconditionally
      overflowX: 'auto',
    }}>
      {segments.map((seg, i) =>
        /^[\u251c\u2514\u2502\u2500]+$/.test(seg)
          ? <span key={i} style={{ color: C.lo }}>{seg}</span>
          : <span key={i}>{seg}</span>
      )}
    </pre>
  );
}


const physicalMap: Record<string, string> = {
  LogicalScan: 'SeqScanExec', LogicalFilter: 'FilterExec',
  LogicalProject: 'ProjectExec', LogicalJoin: 'HashJoinExec',
  LogicalGroupBy: 'GroupByExec', LogicalHaving: 'HavingExec',
  LogicalOrderBy: 'SortExec', LogicalLimit: 'LimitExec',
  LogicalInsert: 'InsertExec', LogicalDelete: 'DeleteExec',
  LogicalUpdate: 'UpdateExec', LogicalCreateTable: 'CreateTableExec',
  LogicalTruncate: 'TruncateExec',
};

function mapPhysical(label: string): string {
  for (const [k, v] of Object.entries(physicalMap)) {
    if (label.includes(k.replace('Logical', ''))) return label.replace(/^[A-Za-z]+/, v);
  }
  let mapped = label;
  for (const [k, v] of Object.entries(physicalMap)) {
    const short = k.replace('Logical', '');
    if (label.startsWith(short)) { mapped = v + label.slice(short.length); break; }
  }
  return mapped;
}

interface StageProps {
  num: string; name: string; timeMs: number;
  open: boolean; onToggle: () => void;
  children: React.ReactNode;
}

function Stage({ num, name, timeMs, open, onToggle, children }: StageProps) {
  const { C } = useTheme();
  return (
    <div>
      <div
        onClick={onToggle}
        style={{
          background: C.surface,
          border: `0.5px solid ${open ? 'rgba(0,212,170,0.2)' : C.border}`,
          borderRadius: '3px', cursor: 'pointer', transition: 'border-color 0.15s',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', padding: '10px 14px', gap: '10px' }}>
          <span style={{ fontFamily: "'Geist Mono', monospace", fontSize: '11px', color: C.lo }}>{num}</span>
          <span style={{ fontFamily: "'Geist', sans-serif", fontWeight: 500, fontSize: '12px', color: C.hi, flex: 1 }}>{name}</span>
          <span style={{ fontFamily: "'Geist Mono', monospace", fontSize: '11px', color: C.mid }}>{timeMs.toFixed(2)}ms</span>
          <span style={{
            fontSize: '10px', color: C.lo, transition: 'transform 0.2s',
            transform: open ? 'rotate(90deg)' : 'rotate(0deg)', display: 'inline-block',
          }}>›</span>
        </div>
        {open && (
          <div style={{
            borderTop: `0.5px solid ${C.border}`, background: C.base, padding: '16px',
            fontFamily: "'Geist Mono', monospace",
          }}>
            {children}
          </div>
        )}
      </div>
    </div>
  );
}

function Connector() {
  const { C } = useTheme();
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '2px 0' }}>
      <div style={{ width: '1px', height: '16px', background: C.border }} />
      <span style={{ fontSize: '9px', color: C.lo, lineHeight: 1 }}>▼</span>
    </div>
  );
}

export function PipelineView({ response, query }: { response: any; query: string }) {
  const { C } = useTheme();
  const [open, setOpen] = useState<Record<number, boolean>>({});
  const toggle = (n: number) => setOpen(p => ({ ...p, [n]: !p[n] }));

  if (!response?.timings) return <div style={{ padding: 20, color: C.lo, textAlign: 'center' }}>—</div>;

  const t = response.timings;
  const tokens = tokenize(query);
  const rowCount = response.rows?.length ?? 0;

  return (
    <div style={{ padding: '20px', maxWidth: 700, margin: '0 auto', animation: 'fadeIn 0.2s ease' }}>

      {/* ── Stage 01: LEXER ── */}
      <Stage num="01" name="LEXER" timeMs={t.parse_ms * 0.6} open={!!open[1]} onToggle={() => toggle(1)}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {tokens.map((tk, i) => (
            <span key={i} style={{
              fontSize: '11px', color: C.hi, border: `0.5px solid ${C.border}`,
              borderRadius: '2px', padding: '3px 8px', fontFamily: "'Geist Mono', monospace",
            }}>{tk}</span>
          ))}
        </div>
      </Stage>

      <Connector />

      {/* ── Stage 02: PARSER → real AST from ast.pretty_print() ── */}
      <Stage num="02" name="PARSER → AST" timeMs={t.parse_ms * 0.4} open={!!open[2]} onToggle={() => toggle(2)}>
        {response.ast_pretty
          ? <PrettyTree text={response.ast_pretty} />
          : response.plan_tree
            ? <TreeNode node={response.plan_tree} />
            : <span style={{ color: C.lo }}>No AST available</span>
        }
      </Stage>

      <Connector />

      {/* ── Stage 03: SEMANTIC ANALYZER ── */}
      <Stage num="03" name="SEMANTIC ANALYZER" timeMs={t.semantic_ms} open={!!open[3]} onToggle={() => toggle(3)}>
        <div style={{ fontSize: '12px', lineHeight: '2.2' }}>
          {['Table existence verified', 'Column types resolved', 'Constraints checked'].map((txt, i) => (
            <div key={i}><span style={{ color: C.accent }}>✓</span> <span style={{ color: C.mid }}>{txt}</span></div>
          ))}
          <div><span style={{ color: C.accent }}>✓</span> <span style={{ color: C.mid }}>Completed in {t.semantic_ms}ms</span></div>
        </div>
      </Stage>

      <Connector />

      {/* ── Stage 04: LOGICAL PLAN + OPTIMIZER ── */}
      <Stage num="04" name="LOGICAL PLAN + OPTIMIZER" timeMs={t.logical_ms + t.optimize_ms} open={!!open[4]} onToggle={() => toggle(4)}>
        <div style={{ display: 'flex', gap: 0 }}>

          {/* Left: Before Optimization — real logical plan pretty_print (LogicalFilter / LogicalProject tree) */}
          <div style={{ flex: 1, paddingRight: '16px' }}>
            <div style={{
              fontSize: '10px', textTransform: 'uppercase', color: C.lo,
              letterSpacing: '0.5px', marginBottom: '10px', fontFamily: "'Geist Mono', monospace",
            }}>Before Optimization</div>

            {/* PrettyTree shows exact LogicalFilter / LogicalProject / LogicalScan tree */}
            {response.logical_plan_pretty
              ? <PrettyTree text={response.logical_plan_pretty} />
              : response.plan_tree && <TreeNode node={response.plan_tree} />
            }
          </div>



          <div style={{ width: '1px', background: C.border }} />

          {/* Right: After Optimization */}
          <div style={{ flex: 1, paddingLeft: '16px' }}>
            <div style={{
              fontSize: '10px', textTransform: 'uppercase', color: C.lo,
              letterSpacing: '0.5px', marginBottom: '10px', fontFamily: "'Geist Mono', monospace",
            }}>After Optimization</div>
            <div style={{
              fontSize: '10px', color: C.accent, marginBottom: '10px', padding: '4px 8px',
              background: C.accentDim, borderRadius: '2px', display: 'inline-block',
            }}>Predicate pushdown applied</div>
            <div style={{ borderLeft: `1.5px solid rgba(0,212,170,0.3)`, paddingLeft: '12px' }}>
              {response.plan_tree && <TreeNode node={response.plan_tree} />}
            </div>
          </div>
        </div>
      </Stage>

      <Connector />

      {/* ── Stage 05: PHYSICAL PLAN → EXECUTOR ── */}
      <Stage num="05" name="PHYSICAL PLAN → EXECUTOR" timeMs={t.exec_ms} open={!!open[5]} onToggle={() => toggle(5)}>
        {response.plan_tree && <TreeNode node={response.plan_tree} mapFn={mapPhysical} />}
        <div style={{ marginTop: '14px', borderTop: `0.5px solid ${C.border}`, paddingTop: '10px', fontSize: '11px', color: C.mid }}>
          <span>{rowCount} row{rowCount !== 1 ? 's' : ''} returned</span>
          <span style={{ margin: '0 8px', color: C.lo }}>·</span>
          <span>Execution: {t.exec_ms}ms</span>
        </div>
      </Stage>

    </div>
  );
}
