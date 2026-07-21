# Aurora Origin Python SDK — Use Cases & Capabilities

**Investigation scope**: Concrete tasks the SDK is designed for, fetch patterns for projects / scenarios / market price forecasts / battery data, time horizons, geographies, and mentions of BESS-specific metrics relevant to the Northwold benchmark stack.

**Sources fetched**:
- `https://raw.githubusercontent.com/AuroraEnergyResearch/aurora-origin-python-sdk/main/examples.ipynb`
- `https://raw.githubusercontent.com/AuroraEnergyResearch/aurora-origin-python-sdk/main/README.md`
- `https://raw.githubusercontent.com/AuroraEnergyResearch/aurora-origin-python-sdk/main/README_DEVELOP.md`
- `https://raw.githubusercontent.com/AuroraEnergyResearch/aurora-origin-python-sdk/main/src/origin_sdk/OriginSession.py` (full)
- `https://raw.githubusercontent.com/AuroraEnergyResearch/aurora-origin-python-sdk/main/src/origin_sdk/service/Scenario.py` (full)
- `https://raw.githubusercontent.com/AuroraEnergyResearch/aurora-origin-python-sdk/main/src/origin_sdk/service/InputsEditor.py`
- `https://raw.githubusercontent.com/AuroraEnergyResearch/aurora-origin-python-sdk/main/src/origin_sdk/types/scenario_enums.py`
- `https://raw.githubusercontent.com/AuroraEnergyResearch/aurora-origin-python-sdk/main/src/origin_sdk/types/scenario_types.py`
- `https://raw.githubusercontent.com/AuroraEnergyResearch/aurora-origin-python-sdk/main/src/origin_sdk/types/project_types.py`
- `https://raw.githubusercontent.com/AuroraEnergyResearch/aurora-origin-python-sdk/main/src/origin_sdk/types/input_types.py`
- `https://raw.githubusercontent.com/AuroraEnergyResearch/aurora-origin-python-sdk/main/src/origin_sdk/gql/queries/scenario_queries.py`
- `https://raw.githubusercontent.com/AuroraEnergyResearch/aurora-origin-python-sdk/main/docsite/docs/common-patterns.mdx`
- `https://raw.githubusercontent.com/AuroraEnergyResearch/aurora-origin-python-sdk/main/docsite/docs/intro.md`
- `https://ghp.auroraer.com/aurora-origin-python-sdk/docs/intro` (live docs)
- `https://ghp.auroraer.com/aurora-origin-python-sdk/docs/common-patterns` (live docs)

---

## 1. What the SDK is for (per the examples & docs)

Aurora Origin is **Aurora Energy Research's market-model platform**. The SDK is a Python client that lets users:

1. **Browse Aurora's published market scenarios** (regional power-market forecasts) by region
2. **Pick a scenario** (typically the latest "central case" for a region) and **download its CSV outputs**
3. **Build custom scenarios** (create projects + scenarios, override inputs such as demand, technology assumptions, commodity prices, interconnectors, then launch a custom model run)
4. **Retrieve modified-scenario outputs** the same way — as CSVs by region / type / granularity / year

So the SDK is fundamentally a **scenario-fetch-and-customize** client, not a "give me current battery prices" REST API. It is built around Aurora's central concepts of **Projects** (containers) holding **Scenarios** (parameterised model runs that produce CSV downloads).

The repo README and docs both note the SDK is **still under active development** ("not ready for general use" in README_DEVELOP). Aurora's full product surface (Aurora Vision, EOS, Chronos, etc.) is broader than what the public SDK exposes today.

---

## 2. Aurora's vocabulary: Project vs Scenario

From `project_types.py` and `scenario_types.py`:

**Project** — a container that groups related scenarios. The Aurora landing page in `examples.ipynb` calls `session.get_projects()` to list them. Fields:
```python
class ProjectSummaryType(TypedDict):
    projectGlobalId: str
    name: str
    description: str
    productId: str
    productName: Optional[str]
    isProjectPinned: bool

class ProjectType(ProjectSummaryType):
    scenarios: List[ScenarioSummaryType]
```
A project owns N scenarios; each scenario belongs to exactly one project (`projectGlobalId` on `InputScenario`).

**Scenario** — a single parameterised model run. Tied to a **region group**, a **run type** (MYR/FYR/NODAL/...), a **model type** (aeres/nodal/regional/network), with a publication date, run status, and (once successful) downloadable outputs. Fields:
```python
class ScenarioSummaryType(TypedDict):
    scenarioGlobalId: str
    name: str
    description: str
    regionGroupCode: str
    publishType: str
    publicationDate: str
    scenarioRunStatus: ScenarioRunStatus      # Queued | Running | Complete | Errored | NotLaunched
    scenarioType: ScenarioOwner                # AURORA_SCENARIO | TENANTED_SCENARIO
    scenarioRunType: ScenarioRunType           # MYR_AND_FYR | MYR | FYR | NODAL | NODAL_PLACEMENT | REGIONAL_MYR | REGIONAL_FYR | REGIONAL_MYR_AND_FYR | NETWORK
    years: List[int]
    weatherYear: Optional[int]
    scenarioInputsAvailable: bool
    scenarioOutputsAvailable: bool
    scenarioLaunchable: bool
    ...
```
Two key flavours via `ScenarioOwner`:
- `AURORA_SCENARIO` — Aurora's official published forecasts (e.g. quarterly "central case" updates) — what `get_aurora_scenarios()` returns.
- `TENANTED_SCENARIO` — scenarios the customer (Ampyr) creates themselves.

`ScenarioRunType` codes hint at the model dimensions: MYR = Multi-Year Run, FYR = Forecast Year Run (?), NODAL = node-level price modelling, REGIONAL = zonal modelling, NETWORK = transmission network model.

---

## 3. Concrete code patterns

### 3.1 Setup
```python
from origin_sdk.OriginSession import OriginSession
session = OriginSession()
```
Auth via `$home/.aurora-api-key` file or `AURORA_API_KEY` env var.

### 3.2 Project list
```python
session.get_projects()
```
Returns `List[ProjectSummaryType]`.

### 3.3 Scenarios — list Aurora-published, filtered by region
The single most prominent example in `examples.ipynb`:
```python
session.get_aurora_scenarios(region="gbr")
```
Filters server-side to `scenarioType == "AURORA_SCENARIO"`. `region` is an optional three-letter region code.

### 3.4 Get the latest "central" scenario for a region (the canonical pattern)
This is the only non-trivial example in both the notebook and `common-patterns.mdx`:
```python
from datetime import datetime

def get_latest_central_for(region: str):
    scenarios_for_region = (
        session.get_aurora_scenarios(region=region)
        .get("data")
        .get("getScenarios")
    )
    central_cases = [
        scenario
        for scenario in scenarios_for_region
        if "central" in scenario.get("name").lower()
    ]
    central_cases.sort(
        key=lambda scenario: datetime.fromisoformat(
            scenario["publicationDate"]
        ).timestamp(),
        reverse=True
    )
    return central_cases[0]

get_latest_central_for("aus")
```
The `Scenario` service class wraps the same pattern as a static helper:
```python
Scenario.get_latest_scenario_from_region(session, region, name_filter=None)
```

### 3.5 Single scenario detail
```python
session.get_scenario_by_id("7bf6f951-def9-4745-ba92-d475f6f014ed")
```
Returns the full `ScenarioType` including `regions` (a `Dict[str, RegionDict]` keyed by region code, each containing `dataUrlBase` and `metaUrl` pointers to where the CSV outputs live).

### 3.6 Downloading scenario CSV outputs (the real "market price forecast" pattern)
This is the closest the SDK gets to "give me a forecast curve." From `Scenario.py` docstrings, three verbatim examples:

```python
# Annual system-level prices for Great Britain
csv_data = scenario.get_scenario_data_csv('gbr', 'system', '1y')
buffer = StringIO(csv_data)
df = pd.read_csv(buffer, header=[0,1])
```

```python
# Hourly nodal data for a specific node, in USD-2024
csv_data = scenario.get_scenario_data_csv(
    region='erc',
    download_type='nodal',
    granularity='1h',
    currency='usd2024',
    node='ZONDWD_6_B1',
)
buffer = StringIO(csv_data)
df = pd.read_csv(buffer, header=[0,1])
```

```python
# Hourly interconnector flows between PEU and Germany for year 2028
csv_data = scenario.get_scenario_data_csv(
    region='peu_deu',
    download_type='interconnector',
    granularity='1h',
    year=2028,
)
```

To find out what `download_type` / `granularity` / `sub_type` combinations are valid for a scenario region:
```python
scenario.get_download_types(region)        # e.g. [{'type': 'system', 'granularity': '1y', 'subType': None}, ...]
scenario.get_download_years(region)        # list of valid hourly-data years
scenario.get_downloadable_regions()        # list of region codes the scenario covers
```

The CSV has **two header rows** (column name + units), so consumers parse with `pd.read_csv(buffer, header=[0,1])`.

### 3.7 Battery / storage / capture-rate
**Not present in the SDK examples, common-patterns doc, or scenario_enums.** The available `download_type` examples in source code are `system`, `technology`, `nodal`, and `interconnector`. No explicit `battery` / `storage` / `capture_rate` / `tb_spread` download type is documented. Battery data, if it exists, would presumably be under `technology`-type downloads (filterable by technology name) or as a sub-tech in capacity/dispatch outputs — but no code example shows this and `scenario_enums.py` does not enumerate technology names.

### 3.8 Custom-scenario authoring (full mutation path)
The SDK supports a full read-modify-launch flow:
```python
session.create_project(InputProject(name=..., description=..., productId=...))
session.create_scenario(InputScenario(
    projectGlobalId=...,
    name=...,
    baseScenarioGlobalId=...,        # clone-from
    regionGroupCode=...,
    scenarioRunType=...,             # one of ScenarioRunType
    modelType=...,                   # aeres | nodal | regional | network
    years=[2025, 2030, 2040, 2050],
    weatherYear=...,
    ...
))

# Override inputs on the new scenario:
session.update_system_demand(scenario_id, region, variable, transform)
session.update_commodity_price(scenario_id, commodity, regions, transform)
session.update_technology_endogenous(...)
session.update_technology_exogenous(...)
session.update_interconnectors(scenario_id, from_region, to_region, variable, transform)

# Launch & poll
session.launch_scenario(scenario_id)
session.get_scenario_by_id(scenario_id)   # poll scenarioRunStatus until "Complete"

# Then download outputs as above
```
`InputsEditor` (BETA) wraps these as a per-scenario object with `get_demand_regions()`, `get_demand_technologies()`, `get_technology_names()`, `get_supply_technology()`, `update_*_variable()` methods.

### 3.9 Other utility ops
- `session.get_weather_year_list(scenario_id)` — supported weather years for a scenario
- `session.get_model_files(scenario_id)` — model file URLs across runs/years (from REST `/v1/modelFiles/{scenario_id}`)
- `session.get_workbook_download_url(scenario_id)` — generates and returns a download URL for an Excel inputs workbook

---

## 4. Time horizons

- Each scenario carries a `years: List[int]` field — the explicit list of model years (e.g. 2025, 2030, 2040, 2050 — Aurora's standard long-term outlook is **~30+ years out to 2050/2060** based on industry knowledge, though the SDK source does not hard-code the range).
- `weatherYear: Optional[int]` controls which historical weather year is used for renewables generation profiles.
- CSV downloads come in granularities of at least `1y` (annual) and `1m` (monthly) per docstrings, plus `1h` (hourly) for nodal and interconnector flows. Year parameter is required for some hourly downloads.
- Scenario `years` are also reflected in `get_download_years(region)` — the set of valid years for hourly data.

**Implication for BESS benchmarking**: Aurora scenarios are long-horizon forecasts (decadal), so they are the right fit for **forward-looking** BESS revenue benchmarks (TB spreads in 2030, 2040 etc.) — not for historical-actual benchmarking. They complement, not replace, Modo / ME-BESS-GB.

---

## 5. Geographies

Region codes appear as **three-letter ISO-like codes** plus aggregate codes:

Examples seen in source:
- `gbr` — Great Britain (used in `common-patterns.mdx`, `examples.ipynb`)
- `aus` — Australia
- `erc` — ERCOT (Texas)
- `peu_deu` — Pan-European Germany aggregate (used as a region "group")
- `deu` — Germany (referenced in URL replacement logic)

The codebase uses both **single-region codes** (`gbr`, `deu`) and **region-group codes** (e.g. `peu_*` for Pan-European groupings, `regionGroupCode` field on scenarios). Region grouping logic in `Scenario.__get_additional_scenario_regions` lets a scenario "expand" from its base region to all regions in the group.

**No explicit enum of all regions** exists in `scenario_enums.py` — regions are discovered dynamically via `session._get_regions()` and per-scenario via `get_downloadable_regions()`. So the actual list of supported countries is data-driven, not type-system-encoded.

`SimulationMode` enum in `scenario_enums.py` does list:
- `EUROPEAN_NETWORK`
- `NO_FLOW_CONSTRAINTS`
- `WITH_FLOW_CONSTRAINTS`
- `WITH_FLOW_CONSTRAINTS_AND_N1`

— which confirms Aurora models the European network as one of its options. The SDK's structure supports any region Aurora models internally; GB and continental Europe are first-class.

**Implication for Ampyr**: GB (Northwold), Germany (live Aug 2026 co-located solar), and Netherlands (live Sep-Oct 2026) are all in scope. UK / US / Australia / European-network are all proven in the docstrings.

---

## 6. Battery / BESS / storage / capture rate / TB spread mentions

**Honest finding**: across the entire SDK surface I pulled (source files, doc pages, examples notebook, type definitions, enums, GraphQL queries), there is **zero explicit mention** of:
- `battery`, `BESS`, `storage`
- `GB Battery Index`
- `TB spread` / `tb_spread`
- `capture rate` / `capture_price`

This does **not** mean Aurora lacks battery data — it means the SDK is structured as a *generic scenario-output retriever*, with batteries being one technology among many that show up in the **CSV download contents** rather than as named SDK methods. To access battery-relevant outputs you would:

1. Pick the latest GB Aurora scenario
2. Call `scenario.get_download_types("gbr")` to see what `technology`-type downloads are available
3. Download the relevant technology CSVs and parse them for battery / storage rows

The Aurora-Ampyr commercial conversation (per project memory: "Aurora benchmark: free with MPA Solar Europe email") may unlock **separately-distributed battery reports** (PDFs / Excel templates) that are not via this SDK. The SDK appears to be the **scenario engine access**, not Aurora's product-marketing-led battery reports.

---

## 7. The data shape developers actually work with

End-to-end the typical "get a forecast" flow is:

```python
from origin_sdk.OriginSession import OriginSession
from origin_sdk.service.Scenario import Scenario
from io import StringIO
import pandas as pd

session = OriginSession()

# 1. Pick latest GB central scenario
scenario = Scenario.get_latest_scenario_from_region(
    session, region="gbr", name_filter="central"
)

# 2. See what's downloadable
print(scenario.get_downloadable_regions())     # which sub-regions
print(scenario.get_download_types("gbr"))       # ["system" / "1y", "technology" / "1y", ...]
print(scenario.get_download_years("gbr"))       # valid hourly years

# 3. Pull annual system data (likely contains baseload, peakload, capture-style metrics)
csv = scenario.get_scenario_data_csv("gbr", "system", "1y")
df = pd.read_csv(StringIO(csv), header=[0, 1])

# 4. Pull hourly data for a specific year (likely the price curves)
csv = scenario.get_scenario_data_csv("gbr", "system", "1h", year=2030)
df = pd.read_csv(StringIO(csv), header=[0, 1])
```

Whether the **`system / 1y`** CSV contains battery TB spreads / capture rates is an empirical question — the SDK source doesn't say, and the meta-JSON for the scenario (fetched lazily inside `__get_download_meta_for_region`) is the definitive listing. To answer "does Aurora have BESS forecasts via this SDK?" requires running step 2 against a live token and inspecting the meta-JSON's `dataDefinitions`.

---

## 8. Implications for the APD benchmark stack

1. **Aurora-via-SDK is forward-looking, not historical**. It complements Modo (operational actuals + percentiles) and ME-BESS-GB (historical durations) — it doesn't replace them. Use case is "what will TB spreads look like in 2030?" not "what did GB batteries earn last month?".
2. **GB + DE + NL are all supported** in principle — the SDK's region system handles continental Europe (Germany live Aug 2026, NL live Sep-Oct 2026 per Ampyr roadmap).
3. **Free Aurora access via MPA membership** (per memory) likely means access to Aurora's **published Aurora Scenarios** (`AURORA_SCENARIO` type) — but probably *not* tenant-side scenario authoring (which would require a paid Origin/EOS license). The "central case" download flow is exactly the supported pattern under a free MPA tier.
4. **The CSV-as-text + two-header-row format** is straightforward to ingest into the APD Streamlit pipeline (similar pattern to the Modo Terminal Excel extract already integrated).
5. **No SDK-level battery/TB-spread shortcuts** — battery-specific metrics, if surfaced at all by the SDK, will live inside a `system` or `technology` CSV and need column-level parsing. Aurora's battery-specific publications (the GB Battery Outlook PDFs etc.) are a separate procurement channel.

---

## 9. Open questions worth answering with a live token

- What `download_type` / `granularity` combinations does a GB scenario actually expose? (Run `scenario.get_download_types("gbr")` once.)
- Are there `technology=battery` rows in the `technology` downloads with capture rates / TB spreads / dispatch hours?
- Does Aurora distribute their **GB Battery Outlook** (long-form report) through the SDK, or only via the web portal + PDF download? (Likely the latter, but worth confirming.)
- What's the actual scenario `regionGroupCode` for the European network — `peu_*`, `eu`, country-by-country?

These would land cleanly as a 30-minute notebook exercise once the Aurora API key arrives via Cyrus / the MPA Solar Europe email.
