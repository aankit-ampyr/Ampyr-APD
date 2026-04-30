# Ankit Agarwal — Work Profile & Projects

## About
- **Role**: GM — Product & Technology, Ampyr Energy Tech Solutions Pvt Ltd
- **Entity**: Ampyr Energy Tech Solutions Pvt Ltd (CIN: U72900KA2021PTC143816)
- **Office**: Assetz House No. 30, 3rd Floor, Crescent Road, Bangalore 560001
- **Reports to**: Shivendu Airi (Director — Investment & Business Development)
- **Development Partner**: DoublU India Pvt Ltd (Bangalore) — contracted under Project Lazarus
- **Working Directory**: `C:\repos`

---

## Company Context

### AGP Group (Parent)
AGP Sustainable Real Assets is a Singapore-headquartered global investor, developer, and asset manager focused on sustainable real assets. Founded in 2018 by partners from Assetz Property Group (est. 2005) and Equis Funds Group (est. 2011).

- **AUM**: US$4.2 billion+
- **Pipeline**: US$10 billion secured development
- **Headcount**: 770+ platform employees, 17 Partners globally
- **Strategic Investor**: Stonepeak ($650M, Nov 2023)
- **Three pillars**: Energy (AMPYR), Digital (data centres), Real Estate (Assetz)

### AMPYR Energy (Energy Pillar)
AMPYR is AGP's global renewable energy platform — a vertically integrated IPP (develop, build, own, operate).

| Platform | Geography | Structure | Scale |
|----------|-----------|-----------|-------|
| **AMPYR Solar Europe (ASE)** | UK, Germany, Netherlands | JV: AGP + Hartree Partners + NaGa Solar | 7+ GW pipeline |
| **AMPYR Distributed Energy (ADE)** | UK & Europe | Subsidiary | 100+ MW, 150+ sites |
| **AMPYR Energy USA** | USA | JV: AGP + Hartree Partners | 4+ GW pipeline |
| **AMPYR Energy India** | Karnataka, Maharashtra | JV: AGP + Climate Fund Managers | 1+ GW |
| **AMPYR Energy Australia** | Australia/NZ | AGP platform | Solar, wind, BESS |

**Global totals**: 12+ GW development pipeline, 365+ projects, 130 MW constructed/operational (by 2024), 9 countries, 95+ projects active, 6 offices.

### AMPYR GTC (Global Technology Centre) — Where Ankit Works
AMPYR GTC is the in-house capability centre spanning across all AMPYR global platforms. It provides:

| Function | Description |
|----------|-------------|
| **Investment & Business Development** | Market intelligence, financial modelling, opportunity assessments |
| **Design & Engineering** | GIS, 3D modelling, yield simulations, technical project delivery |
| **Procurement & Supply Chain** | Strategic sourcing, contracting, vendor management |
| **Program Management** | Risk mitigation, resource planning, stakeholder communication |
| **Asset Management** | Real-time analytics, custom reporting, predictive maintenance |

### GTC Leadership Team
| Name | Role |
|------|------|
| **Tarun Agrawal** | Partner with AGP, CEO — AMPYR Solar Europe |
| **Shivendu Airi** | Director — Investment & Business Development (Ankit's manager) |
| **Mohammad Mustaque** | Director — Design & Engineering, Asset Management |
| **Vikas Varshney** | Director — Procurement & Supply Chain Management |

*Note: Pradeep Kunwar (former Centre Head — GTC and Investment) has left the company.*

### Key Internal Contacts
- **HR**: Neha Tyagi (neha.tyagi@ampyrenergy.com), Palak Jain (palak.jain@ampyrenergy.com)
- **IT Helpdesk**: helpdesk@agpgroup.com
- **Admin**: Neha Chauhan (neha.chauhan@ampyrenergy.com)
- **Doublu (Dev Partner)**: Arijit Sarkar (arijit.sarkar@doublu.ai)

---

## Long-Term Product Vision

All projects below are building blocks toward a single strategic goal: **Autonomous Portfolio Revenue Optimisation**.

The end-state platform will:
1. **Monitor** asset performance across the portfolio in real-time (APD)
2. **Size** new investments optimally before committing capital (PSP)
3. **Model** financials across the full portfolio at speed (PFA)
4. **Predict** market prices (in-house or purchased forecasts) and generation output (purchased initially, then in-house)
5. **Optimise** bid strategies across assets using those predictions to maximise portfolio revenue
6. **Automate** reconciliation and back-office operations (Bank-Rec)
7. **Assist** analysts and decision-makers with a domain-aware AI layer (RAG + proprietary LLM)

### How the projects connect

```
                        AMPYR PRODUCT PLATFORM
                        ~~~~~~~~~~~~~~~~~~~~~~

  [Market Price Forecasts] ──┐     ┌── [Generation Forecasts]
   (in-house / purchased)    │     │    (purchased → in-house)
                             ▼     ▼
                    ┌─────────────────────┐
                    │  BID OPTIMISATION   │  ← Future: autonomous bidding
                    │  ENGINE             │    across assets & markets
                    └────────┬────────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │   APD        │ │   PSP        │ │   PFA        │
    │  (Monitor)   │ │  (Size)      │ │  (Model)     │
    │  Asset Perf  │ │  New Invest  │ │  Financials  │
    └──────────────┘ └──────────────┘ └──────────────┘
            │                                 │
            └──────────┐      ┌───────────────┘
                       ▼      ▼
               ┌──────────────────┐
               │   Bank-Rec       │
               │  (Reconcile)     │
               └──────────────────┘

    ┌─────────────────────────────────────────┐
    │  RAG + Proprietary LLM                  │
    │  (AI layer spanning all modules)        │
    │  Domain knowledge, natural language     │
    │  querying, recommendations, anomaly     │
    │  detection across the entire platform   │
    └─────────────────────────────────────────┘
```

### Phased approach
| Phase | Focus | Status |
|-------|-------|--------|
| **Now** | Build APD + PSP (Doublu), start PFA + Bank-Rec (internal) | In progress |
| **Next** | Generation forecasts (purchased), market price data integration | Planning |
| **Later** | In-house forecasting models, bid optimisation engine | Future |
| **End-state** | AI-driven autonomous portfolio revenue optimisation with RAG + LLM | Vision |

---

## Project Lazarus — Doublu Engagement (SOW: AMP/LZ/001)

Doublu is rebuilding Ankit's two Streamlit prototypes into production web applications.

- **Contract**: MSA + SOW signed, NDA in place
- **Duration**: 12 Feb 2026 → 20 Nov 2026 (40 weeks)
- **Doublu Contact**: Arijit Sarkar (Managing Director)
- **Ampyr Contact**: Ankit Agarwal
- **Production Stack**: React + TypeScript, MUI, Recharts/Plotly, FastAPI (Python), PostgreSQL, Docker, JWT auth, OLlama (AI)
- **Doublu Team**: Lead Backend/Architect, Backend Engineer, Frontend Engineer (React), BA, UI/UX Designer, DevOps, QA

### Pricing (INR ex taxes)
| Module | Phase 1A | Phase 1B |
|--------|----------|----------|
| AMD    | 15,18,000 | 15,64,000 |
| BESS   | 14,72,000 | 17,02,000 |
| **Total** | **29,90,000** | **32,66,000** |

Phase 2 pricing to be confirmed after Phase 1 delivery. Service fee of 4.5%/month applies during transition periods.

### Payment Schedule
- 30% at Project Kick Off
- 25% at Phase 1A delivery
- 25% at Phase 1B commencement
- 20% at Phase 1 code handover

---

## Active Projects (Officially Approved)

### 1. Ampyr-APD — Asset Performance Dashboard (formerly Bess-Dashboard)
- **Path (prototype)**: `C:\repos\Ampyr-APD`
- **Built by**: DoublU (production) / Ankit (Streamlit prototype — actively developed in parallel)
- **Status**: Phase 1A — Sprint 1 complete, **Sprint 2 demoed 6 Apr (25% milestone reached)**. Sprint 3 prep pending from Doublu.
- **Sprint 1 (Delivered)**: Authentication & authorization, user management & platform assignment, audit logs (12 stories)
- **Sprint 2 (Delivered, demoed 6 Apr)**: AMD asset onboarding wizard (basic info → optimization params → file upload), aggregator + SCADA validation, data merging (50 cols), SOC calculation logic. Action items raised: rename AMD→APD, alphanumeric asset name validation, flag missing SCADA intervals as errors (no auto-fill), GitHub repo access, send Nov–Feb aggregator files to Anil/Arijit.
- **Prototype Stack**: Python 3.11, Streamlit, Pandas, NumPy, Plotly, Matplotlib, SciPy (LP), OpenPyXL
- **Production Stack**: React + TypeScript, MUI, FastAPI, PostgreSQL, Docker
- **What it does**: Dashboard for monitoring and analyzing Ampyr Group's energy assets (solar, BESS, solar+BESS). Tracks aggregator performance against optimized baselines, IAR projections, and market benchmarks. Currently prototyped for Northwold Solar Farm BESS (8.4 MWh).
- **Prototype Key files**: `streamlit_dashboard.py` (main, 184KB), `/src/`, `/data/`, `/extra/`
- **Prototype Data Pipeline** (as of 30 Apr 2026): `raw/` is starting-point only — organised by month folders (`Oct 2025/`, …, `Apr 2026/`, plus `OneDrive_*/` for multi-month Hartree batches). Pages never read `raw/` directly. ETL: `python -m src.data_cleaning.process_invoices` materialises `data/invoices/*.parquet`; pages read those via `data_cleaning.read_*` functions. Run the ETL whenever new files are dropped into `raw/`.
- **Prototype Active Work**: **EPEX sample data received from Sunil (6 Apr) — analysis underway, database design in progress.** **Modo Energy API access live — integration starting.** Adding more benchmarks, invoice energy reconciliation. **Grid fees (~£6k/month, ~20% revenue) — email sent to Matt 7 Apr; Tinvia to be engaged as ongoing data source.** Intraday calc review with Daniel targeted 7 Apr (else 15/16 Apr).

#### AMD Roadmap (Doublu)
| Phase | Weeks | Scope |
|-------|-------|-------|
| **Phase 1A** | 1–8 | Initial working system: single asset/org, manual upload, basic validation, core metrics, single benchmark (Modo), basic dashboards, inline annotations |
| **Phase 1B** | 9–17 | Full Phase 1: auth + RBAC, multi-org/asset management, full data ingestion pipeline, complete analytics + benchmarking, automated digests + reporting, exports (CSV/Excel), admin/audit/governance |
| **Phase 2** | 14–28 | Additional benchmark sources, aggregator API ingestion, SCADA API ingestion, multi-region/country, enhanced visualisations |
| **Support** | 29–40 | Post-implementation support |

### 2. Ampyr-PSP — Project Sizing Platform (formerly BESS Sizing Tool)
- **Path (prototype)**: `C:\repos\Ampyr-PSP`
- **Built by**: DoublU (production) / Ankit (Streamlit prototype — actively developed in parallel)
- **Status**: Phase 1A — Sprint 1 complete, **Sprint 2 demoed 6 Apr (25% milestone reached)**. Sprint 3 prep pending from Doublu.
- **Sprint 1 (Delivered)**: Authentication & authorization, user management & platform assignment, audit logs (shared with AMD)
- **Sprint 2 (Delivered, demoed 6 Apr)**: Project management (search/filter/archive/delete with audit trail, double-confirm deletion), simulation wizard steps 1–3: load profile (5 patterns: 24/7, day, night, seasonal, custom windows), solar profile (Excel upload + curtailable analysis), battery configuration (containers, SOC 5–95%, RTE 87%, cycle limits 0–3). Action items: rename BESS→"Project Sizing Platform", min cycle limit 0.5→0, share Figma (Shikha off until 15 Apr).
- **Prototype Stack**: Python 3.11+, Streamlit, Pandas, NumPy, Plotly, SciPy
- **Production Stack**: React + TypeScript, MUI, FastAPI, PostgreSQL, Docker
- **What it does**: Optimizes BESS sizing for solar+storage. Year-long hourly simulation with binary delivery constraints (25 MW or nothing). Finds optimal battery capacity (10–500 MWh). Includes DG hybrid simulation.
- **Prototype Key files**: `app.py` (entry), `/pages/` (wizard steps), `/src/` (dispatch engine, config), `/Inputs/` (solar profiles)
- **Prototype Active Work**: Project IRR calculation — Level 1 testing **resumed with Anchal 1 Apr**. ~447 lines uncommitted in `src/financial_model.py` plus new `consolidated_model.py`, `dispatch_energy.py`, `excel_reader.py`, `gas_model.py`, `tests/test_project_irr.py` — needs commit.

#### BESS Roadmap (Doublu)
| Phase | Weeks | Scope |
|-------|-------|-------|
| **Phase 1A** | 1–8 | Initial working system: basic scenario setup, core simulation config, engine integration, guided config, basic dashboards, persistence, basic result views |
| **Phase 1B** | 9–17 | Full Phase 1: auth + user access, project/scenario management, full simulation input config, engine integration + execution, scenario versioning, results analysis + visualization, exports, admin/audit |
| **Phase 2** | 14–28 | AI features: chat interface, NLP querying over scenarios, result interpretation, scenario recommendation, anomaly detection, AI-assisted reporting, product polish (caching, lazy loading, UX) |
| **Support** | 29–40 | Post-implementation support |

### 3. Ampyr-PFA — Financial Analysis Digitisation (Financial Model Digitisation)
- **Path**: `C:\repos\Ampyr-PFA`
- **Built by**: Ankit (internal)
- **Status**: Phase 0 Complete (infra ready), Phase 1 next (DB schema & ingestion)
- **Stack**: Python 3.12, FastAPI, PostgreSQL 16, SQLAlchemy 2.0, Alembic, NumPy, SciPy, Streamlit (UI), Docker, Ruff, pytest
- **What it does**: Digitises Ampyr's Excel-based renewable energy financial model. Portfolio of 78 solar/BESS assets, 170 metrics each, 35-year monthly horizon (3.1M output cells). Target: reduce modelling time from 2–3 hours to <5 seconds. Handles 877 Excel formulas (26 function types), DSCR circular reference solving.
- **Key files**: `app/{models,ingestion,engine,api,reports,ui}/`
- **Config**: `.env.example` present, PostgreSQL at localhost:5432, Git LFS for Excel files
- **Next**: Database schema & ingestion pipeline

### 4. AGP-Bank-Rec (Bank Reconciliation — Functional Prototype)
- **Path**: `C:\repos\AGP-Bank-Rec`
- **Built by**: Ankit (internal)
- **Scope**: Functional prototype — not production system
- **Status**: **Project discontinued (30 Mar 2026)**. Kyriba bank statement function terminated for cost savings. Prototype demoed to Tinvia & Francine — project closed after meeting.
- **Stack**: Python 3.12+, Pandas, OpenPyXL, RapidFuzz, httpx (async), Streamlit (review UI), pytest, Ruff
- **What it does**: Was: daily bank reconciliation prototype for 3 SPV entities with 5-tier matching engine. Prototype demonstrated to Tinvia & Francine on 30 Mar. Project discontinued.
- **Key files**: `run_matching.py` (entry, needs `-X utf8` on Windows), `data/samples/` (private Excel files)
- **Important**: Uses `Decimal` (never `float`) for all monetary amounts, quantized to 2 decimal places
- **Completed**: NetSuite OAuth 1.0 client, matching engine, dashboard, prototype demo to finance team
- **Limitations identified**: Intercompany transfers, pay-on-behalf, SEPA batch payments, multi-currency scenarios, CSV upload bypasses NetSuite mandatory field validation
- **Next**: None — project closed.

---

## Upcoming / In-Progress Initiatives

### 5. Ampyr RAG System
- **Path**: `C:\repos\Ampyr-RAG`
- **Built by**: Ankit (internal)
- **Status**: Pre-implementation (domain ontology + research phase)
- **Stack**: Python, Docling (PDF conversion), planned: vector DB (Pinecone), LangChain, Elasticsearch, embeddings
- **What it does**: Domain-specific RAG pipeline for renewable energy knowledge (Solar PV, Wind, BESS). Entity/relationship extraction using domain ontology.
- **Key files**: `ampyr_domain_ontology_v1.yaml`, `rag-reference/` (architecture research)
- **Next**: Architecture selection, pipeline implementation

### 6. Proprietary LLM for Ampyr Energy
- **Built by**: Ankit (internal)
- **Status**: Planning
- **Notes**: Custom LLM fine-tuned for Ampyr's energy domain. To be integrated with the RAG system above.

---

## Out of Scope (per Doublu SOW)
- Creation/modification of core optimization or financial algorithms (Ankit owns these)
- Real-time operational execution, automated dispatch, trading/bidding integration
- Autonomous AI decision-making, continuous model training, custom AI model development
- External user access, public links, collaborative multi-user editing
- Custom report formats beyond defined templates

---

## Reference / Documentation

### Development PRDs
- **Path**: `C:\repos\Ampyr-PRDs`
- **Purpose**: All approved project documentation, contracts, and specs
- **Key subfolders**:
  - `Final Project Docs/` — Approved PDFs (business requirements v2, cost proposal, roadmap, executive summary, Lars's BESS presentation)
  - `Final Project Docs/Signed agreements/` — MSA (signed), SOW (signed), NDA, Contract Review Form (with Doublu)
  - `BessDashboard Docs 12 Feb/` — Comprehensive BESS/Lazarus specs (Tool1, Tool2, data requirements, UK markets, methodology)
  - `MarkDown Files/` — Platform PRDs (Asset Performance, Investment Sizing, Revenue Optimisation, Strategy docs)
  - `Dev Work updates/` — Sprint-level user stories and Doublu weekly status reports
    - `Lazarus - User Stories_Sprint 1.xlsx` — 12 stories (completed): Auth, user management, platform assignment, audit logs
    - `Lazarus - User Stories_Sprint 2.xlsx` — 32 stories (in progress): AMD asset onboarding + view analysis, BESS project management + simulation wizard
    - `Lazarus - Weekly_Status_Report_ 26 Mar '26.pptx` — Doublu weekly report (Sprint 2, 12.5% milestone)

---

## General Conventions
- All Ampyr projects use **Python** as primary language
- UI preference: **Streamlit** for internal prototypes/dashboards, **React + FastAPI** for production (Doublu)
- Data handling: **Pandas + NumPy**, financial data always uses **Decimal**
- Deployment: Streamlit Cloud for prototypes, Docker for production services
- Code quality: **Ruff** for linting, **pytest** for testing
- All projects are under `C:\repos\` on Windows

---

## End-of-Conversation Checklist

**Before closing any conversation, always do the following:**

1. **Update Project Timelines**: Review and update `C:\repos\Ampyr-PRDs\Ampyr Project Timelines.xlsx` if any project status, timeline, or scope changed during this conversation. Update the `Status` column for any work items that moved (e.g., Not Started → In Progress → Done), adjust weekly checkpoints, and update the Portfolio Summary sheet if priorities or allocations shifted.

2. **Update CLAUDE.md**: If any project status, scope, or context changed, update this file to reflect the latest state.

3. **Update Memory**: If new persistent context was discussed (new projects, contacts, decisions), update the memory files at `C:\Users\AnkitAgarwal\.claude\projects\C--repos\memory\`.
