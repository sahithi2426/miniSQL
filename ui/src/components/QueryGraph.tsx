import { useMemo } from 'react';
import { ReactFlow, Background, Controls } from '@xyflow/react';
import { useTheme } from '../theme';
import '@xyflow/react/dist/style.css';

interface PlanNode {
  id: string;
  type: string;
  label: string;
  children: PlanNode[];
}

const operatorColor: Record<string, string> = {
  LogicalScan: '#14b8a6',      // teal
  LogicalFilter: '#f59e0b',    // amber
  LogicalProject: '#534AB7',   // indigo
  LogicalJoin: '#f87171',      // coral
  LogicalGroupBy: '#a78bfa',   // violet
  LogicalHaving: '#f59e0b',    // amber
  LogicalOrderBy: '#38bdf8',   // sky
  LogicalLimit: '#22c55e',     // green
  LogicalCreateTable: '#64748b',
  LogicalInsert: '#64748b',
  LogicalDelete: '#f87171',
  LogicalUpdate: '#f59e0b',
  LogicalTruncate: '#f87171',
};

export function QueryGraph({ plan }: { plan: PlanNode | null }) {
  const { C, isDark } = useTheme();
  const { nodes, edges } = useMemo(() => {
    if (!plan || !plan.id) return { nodes: [], edges: [] };

    const generatedNodes: any[] = [];
    const generatedEdges: any[] = [];

    let leafCount = 0;
    const levelHeight = 130;

    function traverse(node: PlanNode, level: number): { x: number; y: number } {
      const color = operatorColor[node.type] || '#64748b';

      if (!node.children || node.children.length === 0) {
        const pos = { x: leafCount * 260, y: level * levelHeight };
        leafCount += 1;

        generatedNodes.push({
          id: node.id,
          position: pos,
          data: { label: node.label },
          style: {
            background: C.surface,
            color: color,
            border: `1px solid ${color}`,
            borderRadius: '8px',
            padding: '12px 18px',
            textAlign: 'center' as const,
            boxShadow: `0 0 12px ${color}22`,
            fontSize: '11px',
            fontFamily: "'JetBrains Mono', monospace",
            fontWeight: 500,
            minWidth: '120px',
          },
        });
        return pos;
      }

      const childPositions = node.children.map((child) => traverse(child, level + 1));
      const parentX = childPositions.reduce((a, p) => a + p.x, 0) / childPositions.length;
      const pos = { x: parentX, y: level * levelHeight };

      generatedNodes.push({
        id: node.id,
        position: pos,
        data: { label: node.label },
        style: {
          background: C.surface,
          color: color,
          border: `1px solid ${color}`,
          borderRadius: '8px',
          padding: '12px 18px',
          textAlign: 'center' as const,
          boxShadow: `0 0 12px ${color}22`,
          fontSize: '11px',
          fontFamily: "'JetBrains Mono', monospace",
          fontWeight: 500,
          minWidth: '120px',
        },
      });

      node.children.forEach((child) => {
        generatedEdges.push({
          id: `e-${node.id}-${child.id}`,
          source: node.id,
          target: child.id,
          animated: true,
          style: { stroke: C.mid, strokeWidth: 1.5 },
          type: 'smoothstep',
        });
      });

      return pos;
    }

    traverse(plan, 0);
    return { nodes: generatedNodes, edges: generatedEdges };
  }, [plan, C, isDark]);

  if (!plan || !plan.id) {
    return (
      <div style={{ height: '100%', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: C.lo, background: C.base, fontSize: '13px' }}>
        Run a SELECT / JOIN query to see the plan tree
      </div>
    );
  }

  return (
    <div style={{ height: '100%', width: '100%', background: C.base }}>
      <ReactFlow nodes={nodes} edges={edges} fitView colorMode={isDark ? "dark" : "light"}>
        <Background gap={20} size={1} color={C.border} />
        <Controls />
      </ReactFlow>
    </div>
  );
}
