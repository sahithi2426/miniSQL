# MiniSQL — A Miniature Relational Database Engine

**Group 18** — Compiler Design Lab Project

| Name | Roll Number |
|------|-------------|
| Rishikesh Reddy | CS23B015 |
| Indu Sahithi | CS23B048 |
| Dhanya Koteswari | CS23B055 |

A full-pipeline SQL engine built from scratch in Python, featuring lexical analysis, parsing, semantic validation, logical plan generation, query optimization, physical execution via the Volcano Iterator model, and a React-based IDE frontend (**MiniSQL Studio**).

### 🌐 Live Demo — [https://sql-a8yx.onrender.com/](https://sql-a8yx.onrender.com/)

---

## Installation & Setup

### Prerequisites   

- **Python** ≥ 3.10 — [Download](https://www.python.org/downloads/)
- **Node.js** ≥ 18 — [Download](https://nodejs.org/)
- **Git** — [Download](https://git-scm.com/)
- **GCC / Clang** *(optional)* — only needed for the legacy `codegen` / `compiler` modules

### Install

```bash
# 1. Clone the repository
git clone https://github.com/ben-15-op/SQL.git
cd SQL

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Frontend dependencies
cd ui
npm install
cd ..
```

### Dependencies

#### Python Packages (installed via `pip install -r requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.111.0 | High-performance async web framework — serves the `/query` and `/catalog` API endpoints |
| `uvicorn` | 0.30.1 | ASGI server that runs the FastAPI application |
| `pydantic` | 2.7.2 | Data validation and serialization for API request/response models |

#### Python Standard Library Modules (no installation needed)

| Module | Used In | Purpose |
|--------|---------|---------|
| `json` | `storage/catalog.py` | Read/write persistent catalog data (`catalog.json`) |
| `os` | Multiple modules | File path handling, environment variables |
| `io`, `contextlib` | `api.py` | Capture `pretty_print()` output as strings |
| `time` | `api.py` | Performance timing for each pipeline stage |
| `subprocess` | `compiler/`, `runtime/` | Execute GCC and compiled binaries (legacy modules) |
| `unittest` | `test_*.py` | Unit testing framework |
| `enum` | `lexer/tokens.py` | Token type definitions |
| `re` | `lexer/lexer.py` | Regular expression-based tokenization |

#### Node.js Packages (installed via `npm install` in `ui/`)

| Package | Purpose |
|---------|---------|
| `react` / `react-dom` | Core UI framework for the MiniSQL Studio frontend |
| `@xyflow/react` | Interactive node-graph library for query plan visualization |
| `axios` | HTTP client for communicating with the FastAPI backend |
| `lucide-react` | SVG icon library used throughout the UI |
| `vite` | Dev server and production bundler |
| `typescript` | Static type checking for all `.tsx` source files |

### Run

**Terminal 1 — Backend:**

```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Frontend:**

```bash
cd ui
npm run dev
```

Open the URL shown by Vite (typically `http://localhost:5173`).

### Using the Makefile

If you have `make` installed (Linux/macOS, or via `choco install make` on Windows):

```bash
make install    # Install all dependencies (Python + Node)
make backend    # Start the FastAPI backend (port 8000)
make frontend   # Start the Vite dev server (port 5173)
make run        # Start both servers together (Windows)
make test       # Run all Python unit tests
make build      # Build frontend for production
make clean      # Remove caches and build artifacts
make help       # Show all available targets
```

### Run Tests

Test files are standalone scripts — run them directly with Python:

```bash
python test_lexer.py
python test_parser.py
python test_semantic.py
python test_logical.py
python test_optimizer.py
python test_fullpipeline.py
python test_joins.py
python test_integrity.py
python test_codegen.py
python test_compiler.py
python test_in.py
python test_ri.py
```

> **Note:** Some tests create/modify `catalog.json`. Delete it before re-running if tests interfere.

---

## Overview

MiniSQL implements the core pipeline of a relational database management system:

```
SQL String ──▶ Lexer ──▶ Parser (AST) ──▶ Semantic Analyzer ──▶ Logical Plan
    ──▶ Optimizer ──▶ Physical Plan ──▶ Volcano Execution Engine ──▶ Results
```

The project ships with **MiniSQL Studio**, a React + TypeScript IDE featuring:
- Rich SQL editor with syntax highlighting
- Real-time pipeline visualization (Tokens → AST → Logical Plan → Optimized Plan → Results)
- Interactive query graph (powered by React Flow)
- Catalog browser and storage monitor
- Light / Dark theme toggle

---

## Architecture

| Layer | Module | Description |
|-------|--------|-------------|
| **Lexer** | `lexer/` | Tokenizes raw SQL strings into a stream of typed tokens |
| **Parser** | `parser/` | Recursive-descent parser that builds an Abstract Syntax Tree (AST) |
| **Semantic Analyzer** | `semantic/` | Validates column references, type compatibility, and schema constraints |
| **Logical Planner** | `logical/` | Converts the AST into relational algebra operators (Scan, Filter, Project, Join, GroupBy, etc.) |
| **Optimizer** | `logical/optimizer.py` | Rule-based optimizations (predicate pushdown, projection pruning) |
| **Physical Planner** | `planner/` | Maps logical operators to physical executor nodes |
| **Execution Engine** | `execution/` | Pull-based Volcano Iterator model — `init()`, `next()`, `close()` |
| **Storage** | `storage/` | JSON-backed persistent catalog, buffer pool, disk manager, page/heap abstractions |
| **Code Generation** *(legacy)* | `codegen/` | Original AOT C-code generator (retained for reference) |
| **Compiler** *(legacy)* | `compiler/` | Assembly generation and linking via GCC (retained for reference) |
| **Runtime** *(legacy)* | `runtime/` | Runs compiled C executables (retained for reference) |
| **Utilities** | `utils/` | Pretty-printer and relational algebra string serializer |
| **API Server** | `api.py` | FastAPI backend exposing `/query` and `/catalog` endpoints |
| **Frontend** | `ui/` | React + TypeScript + Vite IDE (MiniSQL Studio) |

---

## Project Structure

```
.
├── api.py                    # FastAPI entry point
├── catalog.json              # Persistent table data (auto-generated)
├── requirements.txt          # Python dependencies
├── Makefile                  # Build & run automation
├── start_ui.bat              # Windows one-click launcher
│
├── lexer/
│   ├── tokens.py             # Token type enum
│   └── lexer.py              # Tokenizer
│
├── parser/
│   ├── ast.py                # AST node definitions
│   └── parser.py             # Recursive-descent parser
│
├── semantic/
│   └── analyzer.py           # Semantic validation
│
├── logical/
│   ├── logical_plan.py       # Logical operator node classes
│   ├── builder.py            # AST → Logical Plan builder
│   └── optimizer.py          # Rule-based query optimizer
│
├── planner/
│   └── physical_plan_builder.py  # Logical → Physical plan mapper
│
├── execution/
│   ├── builder_exec.py       # Physical plan builder (execution layer)
│   ├── seq_scan.py           # Sequential Scan operator
│   ├── filter.py             # Filter operator
│   ├── project.py            # Projection operator
│   ├── nested_loop_join.py   # Nested-Loop Join operator
│   ├── groupby.py            # Group By / Having / Order By / Limit
│   ├── insert.py             # Insert executor
│   └── ddl_dml_exec.py       # DDL/DML command executor
│
├── storage/
│   ├── catalog.py            # JSON-backed system catalog
│   ├── buffer_pool.py        # Buffer pool manager
│   ├── disk_manager.py       # Disk I/O manager
│   ├── page.py               # Page abstraction
│   └── table_heap.py         # Heap-file table storage
│
├── codegen/                  # (Legacy) AOT C code generator
├── compiler/                 # (Legacy) GCC assembly/linking
├── runtime/                  # (Legacy) Compiled executable runner
├── utils/                    # Pretty-printer, RA serializer
│
├── test_*.py                 # Unit tests (lexer, parser, semantic, etc.)
│
├── ui/                       # MiniSQL Studio (React frontend)
│   └── src/
│       ├── App.tsx           # Main application
│       ├── theme.tsx         # Light/dark theme provider
│       └── components/       # PipelineView, QueryGraph, CatalogView, etc.
│
└── Final_Deliverable.md      # Design rationale document
```

---

## Supported SQL

### DDL
```sql
CREATE TABLE students (id INT, name TEXT, age INT);
CREATE TABLE orders (id INT, customer_id INT REFERENCES customers(id));
```

### DML
```sql
INSERT INTO students VALUES (1, 'Alice', 22);
DELETE FROM students WHERE id = 1;
UPDATE students SET age = 23 WHERE name = 'Alice';
TRUNCATE TABLE students;
```

### Queries
```sql
SELECT * FROM students;
SELECT name, age FROM students WHERE age > 20;
SELECT name FROM students WHERE age > 20 ORDER BY name ASC LIMIT 5;
SELECT department, COUNT(*) FROM employees GROUP BY department HAVING COUNT(*) > 3;
SELECT c.name, o.amount FROM customers c JOIN orders o ON o.customer_id = c.id;
SELECT * FROM students WHERE age IN (20, 21, 22);
```

### Supported Clauses
`WHERE` (AND, OR, NOT) · `JOIN` · `GROUP BY` · `HAVING` · `ORDER BY` · `LIMIT` · `IN` · Primary Key · Unique · Foreign Key

---

## Deployment

Live at **[https://sql-a8yx.onrender.com/](https://sql-a8yx.onrender.com/)** — deployed via `render.yaml` on [Render](https://render.com).

The FastAPI server serves the built React frontend from `ui/dist/` as static files.

---

## License

This project was developed as a Compiler Design Lab project by **Group 18** — Rishikesh Reddy, Indu Sahithi, and Dhanya Koteswari.
