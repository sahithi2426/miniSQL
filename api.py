import time
import os
import io
import contextlib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Any

from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.analyzer import SemanticAnalyzer
from logical.builder import LogicalPlanBuilder
from logical.optimizer import LogicalOptimizer
from execution.builder_exec import PhysicalPlanBuilder
from storage.catalog import Catalog
from utils.relational_algebra import predicate_to_string, plan_to_ra_string

app = FastAPI(title="MiniSQL API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global catalog
catalog = Catalog()
analyzer = SemanticAnalyzer(catalog)
logical_builder = LogicalPlanBuilder()
optimizer = LogicalOptimizer(catalog)
physical_builder = PhysicalPlanBuilder(catalog, analyzer)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    status: str
    message: str
    rows: Optional[List[dict]] = None
    columns: Optional[List[str]] = None
    timings: dict
    plan_tree: dict
    ra_string: Optional[str] = None
    ra_optimized: Optional[str] = None
    ast_pretty: Optional[str] = None
    logical_plan_pretty: Optional[str] = None

def capture_pretty(obj) -> str:
    """Capture obj.pretty_print() output as a plain string, preserving partial output."""
    if obj is None:
        return ""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            obj.pretty_print()
        except Exception as e:
            # Keep whatever was already captured and append error note
            print(f"  [render error: {e}]")
    return buf.getvalue()

# We can re-use the predicate_to_string function directly from util
def serialize_plan(plan) -> dict:
    if not plan:
        return {}

    node_type = plan.__class__.__name__
    label = node_type
    children = []

    if node_type == "LogicalScan":
        label = f"Scan({plan.table})"
    elif node_type == "LogicalFilter":
        from utils.relational_algebra import predicate_to_string
        label = f"Filter({predicate_to_string(plan.predicate)})"
        children.append(serialize_plan(plan.child))
    elif node_type == "LogicalProject":
        label = f"Project({', '.join(plan.columns)})"
        children.append(serialize_plan(plan.child))
    elif node_type == "LogicalJoin":
        from utils.relational_algebra import predicate_to_string
        label = f"Join({predicate_to_string(plan.condition)})"
        children.append(serialize_plan(plan.left_child))
        children.append(serialize_plan(plan.right_child))
    elif node_type == "LogicalGroupBy":
        label = f"GroupBy({', '.join(plan.group_cols)})"
        children.append(serialize_plan(plan.child))
    elif node_type == "LogicalHaving":
        from utils.relational_algebra import predicate_to_string
        label = f"Having({predicate_to_string(plan.predicate)})"
        children.append(serialize_plan(plan.child))
    elif node_type == "LogicalOrderBy":
        label = f"OrderBy({plan.column} {plan.order_type})"
        children.append(serialize_plan(plan.child))
    elif node_type == "LogicalLimit":
        label = f"Limit({plan.limit})"
        children.append(serialize_plan(plan.child))
    elif node_type == "LogicalCreateTable":
        cols = ", ".join([c[0] if isinstance(c, (list, tuple)) else str(c) for c in plan.columns])
        label = f"CreateTable({plan.table}, {cols})"
    elif node_type == "LogicalInsert":
        label = f"Insert({plan.table})"
    elif node_type == "LogicalDelete":
        label = f"Delete({plan.table})"
    elif node_type == "LogicalUpdate":
        label = f"Update({plan.table})"
    elif node_type == "LogicalTruncate":
        label = f"Truncate({plan.table})"

    return {
        "id": str(id(plan)),
        "type": node_type,
        "label": label,
        "children": children
    }


@app.post("/query", response_model=QueryResponse)
def execute_query(req: QueryRequest):
    sql = req.query
    timings = {}

    try:
        # Lexing & Parsing
        t0 = time.perf_counter()
        lexer = Lexer(sql)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        timings["parse_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        ast_pretty = capture_pretty(ast)

        # Semantic Analysis
        t0 = time.perf_counter()
        analyzer.analyze(ast)
        timings["semantic_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        # Logical Plan
        t0 = time.perf_counter()
        logical_plan = logical_builder.build(ast)
        timings["logical_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        logical_plan_pretty = capture_pretty(logical_plan)
        ra_string = plan_to_ra_string(logical_plan)
        
        # Optimization
        t0 = time.perf_counter()
        optimized_plan = optimizer.optimize(logical_plan)
        timings["optimize_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        
        # Optimized RA string for comparison
        ra_optimized = plan_to_ra_string(optimized_plan)
        
        # Serialize Plan for UI
        plan_tree = serialize_plan(optimized_plan)
        
        # Physical Plan
        t0 = time.perf_counter()
        physical_plan = physical_builder.build(optimized_plan)
        
        if not physical_plan:
            timings["exec_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return QueryResponse(
                status="success",
                message="Command executed successfully.",
                timings=timings,
                plan_tree=plan_tree,
                ra_string=ra_string,
                ra_optimized=ra_optimized,
                ast_pretty=ast_pretty,
                logical_plan_pretty=logical_plan_pretty
            )

        # Execution
        physical_plan.init()
        rows = []
        columns = []
        while True:
            tup = physical_plan.next()
            if tup is None:
                break
            rows.append(tup)
            if not columns and tup:
                columns = list(tup.keys())
                
        timings["exec_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        return QueryResponse(
            status="success",
            message=f"Returned {len(rows)} rows.",
            rows=rows,
            columns=columns,
            timings=timings,
            plan_tree=plan_tree,
            ra_string=ra_string,
            ra_optimized=ra_optimized,
            ast_pretty=ast_pretty,
            logical_plan_pretty=logical_plan_pretty
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/catalog")
def get_catalog():
    data = []
    
    # Reload from disk just in case changes are made
    catalog._load()
    
    for name, table in catalog.tables.items():
        data.append({
            "name": name,
            "columns": [{"name": k, "type": v} for k, v in table.columns.items()],
            "rows": len(table.rows),
            "primary_key": table.primary_key,
            "unique_keys": table.unique_keys
        })
    return {"tables": data}

# ─── Serve React Frontend (for deployment) ───
# After building the React app, serve the static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "ui", "dist")

if os.path.isdir(STATIC_DIR):
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="static-assets")

    # Catch-all: serve index.html for any non-API route (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
