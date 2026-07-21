# Aurora Origin Python SDK — Method Inventory

**Source repo:** `github.com/AuroraEnergyResearch/aurora-origin-python-sdk`
**Branch fetched:** `main` (as of 2026-06-01)
**Pip install:** `pip install git+https://github.com/AuroraEnergyResearch/aurora-origin-python-sdk`
**Auth:** API key in `$HOME/.aurora-api-key` or env var `AURORA_API_KEY`.

---

## 1. Headline conclusions for APD / BESS-GB use

1. **The SDK is a "Origin platform" scripting wrapper, not a market-data feed.** Every method is structured around three concepts: **Projects** (containers), **Scenarios** (Aurora's published market simulations OR user-tenanted scenarios), and **Inputs** (the assumption side: demand, technology, commodities, interconnectors). It is **not** a TB-spread / capture-rate REST API and it does **not** expose BMU-level historical operational data.
2. **All actual numerical output** (prices, dispatch, capacities, etc.) comes through **one generic method** — `Scenario.get_scenario_data_csv(region, download_type, granularity, year=None, node=None, sub_type=None, currency=None)` — which returns a CSV string. What is *actually* downloadable depends on per-scenario `dataDefinitions` metadata (which the SDK doesn't enumerate statically — you have to call `get_download_types(region)` on a live scenario).
3. **No keyword hits** for `battery`, `BESS`, `storage`, `TB`, `spread`, `capture`, `ancillary`, `BMU`, `intraday`, `day-ahead`, `forecast`, `historic`, `balanc` in the SDK source code. These are all encoded as scenario-output strings (`download_type` + `sub_type`) that Aurora's backend defines per region/product — not as named SDK methods.
4. **All Aurora scenarios are forward-looking forecasts**, not historical observation feeds. `scenarioRunType` enum is `MYR` (multi-year run), `FYR` (full-year run), and combinations — these are projection types. The lone `isHistoricRun` flag in `AdvancedScenarioSettings` is marked "internal only." There is **no method like `get_historical_prices`** on the SDK.
5. **GB region is fully supported** — `region="gbr"` is used throughout the examples notebook. UK/GB-specific battery products would be queryable IF (a) Ampyr's API key has access to a battery-product Aurora scenario for GB and (b) the scenario's `dataDefinitions` exposes a battery `type` such as `"battery"` or `"storage"`. This needs to be confirmed empirically with a live key — the SDK source does not advertise it.
6. **Multi-tenanted modifications are supported** — the SDK can clone Aurora scenarios, edit demand/technology/commodity assumptions via `Transform` (Percentage / Delta / Absolute), launch the run, and download output CSVs. Useful for *what-if* portfolio modelling, **not** for benchmarking actual recent Northwold revenue against a market index.

---

## 2. OriginSession — public method inventory

`OriginSession` is the main entry point. Lives in `src/origin_sdk/OriginSession.py`. Inherits from `core.api.APISession`. Holds two GraphQL endpoints:
- **Scenario service:** `https://api.auroraer.com/scenarioExplr` (or `api-staging`)
- **Inputs service:** `https://api.auroraer.com/modelInputs` (or `api-staging`)

Methods are organised below by concern. All methods are instance methods on `OriginSession` unless noted.

### 2.1 Session lifecycle

| # | Method | Purpose | Args | Returns |
|---|--------|---------|------|---------|
| 1 | `__init__(config: OriginSessionConfig = {})` | Construct session, load API key, pick endpoints. | `config`: optional dict with `universe` (staging/production), custom URLs, etc. | `OriginSession` |
| 2 | `__getstate__()` / `__setstate__(state)` | Pickle support (token re-injection on unpickle). | — | — |

### 2.2 Project methods (scenario containers)

| # | Method | Purpose | Args | Returns |
|---|--------|---------|------|---------|
| 3 | `get_projects()` | List all projects owned by the user. | — | `List[ProjectSummaryType]` (each: `projectGlobalId`, `name`, `description`, `productId`, `productName`, `isProjectPinned`) |
| 4 | `get_project(project_id)` | Fetch full project incl. nested scenario summaries. | `project_id: str` | `ProjectType` (= summary + `scenarios: List[ScenarioSummaryType]`) |
| 5 | `create_project(project: InputProject)` | Create new project. | `project`: `{name, description?, productId?}` | `ProjectSummaryType` |
| 6 | `update_project(project_update)` | Update project metadata. | dict matching `UpdateProjectInputGroup` GQL type | `ProjectSummaryType` |
| 7 | `delete_project(project_id)` | Delete a project. | `project_id: str` | GQL response |
| 8 | `pin_project(project_id)` / `unpin_project(project_id)` | Pin/unpin project in UI. | `project_id: str` | GQL response |
| 9 | `get_project_product_id(product)` | Resolve a product name or ID to its canonical ID (uses dash config cache). | `product: str \| int` | `productId: str` |

### 2.3 Scenario discovery + lifecycle

| # | Method | Purpose | Args | Returns |
|---|--------|---------|------|---------|
| 10 | `get_aurora_scenarios(region=None)` | **List all *Aurora-published* scenarios** (the central cases / sensitivities Aurora publishes). Optional region filter. | `region`: optional ISO code e.g. `"gbr"`, `"aus"`, `"deu"`. Region examples from notebook. | `List[ScenarioSummaryType]` |
| 11 | `get_scenario_by_id(scenario_id)` | Detailed view of one scenario (Aurora or tenanted). | `scenario_id: str` | `ScenarioType` (extends summary with `regions: Dict[str, RegionDict]`, `defaultCurrency`, `baseScenarioGlobalId`, `runDetails`, etc.) |
| 12 | `create_scenario(scenario: InputScenario)` | Create user-tenanted scenario as a clone of a base (Aurora or own). | `scenario`: see `InputScenario` schema below | `ScenarioType` |
| 13 | `update_scenario(scenario_update)` | Update scenario metadata. | dict matching `UpdateScenarioInput` | `ScenarioType` |
| 14 | `delete_scenario(scenario_id)` | Delete tenanted scenario. | `scenario_id: str` | GQL response |
| 15 | `launch_scenario(scenario_id)` | Trigger Aurora backend to run the simulation. | `scenario_id: str` | `ScenarioType` (run status will progress to `Queued → Running → Complete`) |
| 16 | `get_weather_year_list(scenario_id)` | List weather years supported (only certain `useExogifiedInputs=True` scenarios). | `scenario_id: str` | `List[int]` (e.g. historical weather years usable as a profile). |
| 17 | `_get_regions()` *(lru_cached)* | Internal: lookup region grouping table from Origin config. | — | dict of region groups |
| 18 | `get_meta_json(meta_url)` | Internal helper: fetch download manifest JSON for a region. | `meta_url: str` | dict (`dataDefinitions`, `years`, etc.) |

### 2.4 Scenario output / model file download

| # | Method | Purpose | Args | Returns |
|---|--------|---------|------|---------|
| 19 | `get_model_files(scenario_id)` | **Internal use only.** Returns the URL list of all model files per run / year. | `scenario_id: str` | `Dict[run_type, Dict[year, file_metadata]]` |
| 20 | `get_model_file_download_url(file_url)` | **Internal use only.** Resolve a model file URL to its downloadable signed URL. | `file_url: str` | URL string |

> **Note:** These two are flagged "internal use only" in docstrings. The user-facing path to outputs is via the `Scenario` service class (section 4 below).

### 2.5 Inputs Service — session + config

| # | Method | Purpose | Args | Returns |
|---|--------|---------|------|---------|
| 21 | `get_inputs_session(scenario_id)` | Rehydrate inputs editor session for a scenario; returns metadata, regions enabled, currency, transforms log. | `scenario_id: str` | `InputsSession` (see schema below) |
| 22 | `get_workbook_download_url(scenario_id)` | Generate + return URL to Excel workbook of inputs assumptions. Polls until ready. | `scenario_id: str` | URL string |

### 2.6 Inputs Service — Technology (supply-side)

The "technology" side is the supply stack — fuel/tech assumptions for `capacity`, `capex`, `opex`, `loadFactorAverage`, `efficiency`, etc. Both endogenous (model builds the capacity) and exogenous (you fix it) variants are supported.

| # | Method | Purpose | Args | Returns |
|---|--------|---------|------|---------|
| 23 | `get_technology_names(scenario_id)` | List technology names per region, with sub-technology groupings and subsidies. | `scenario_id: str` | `TechnologyNames` = `Dict[region, Dict[techName, {subTechnologiesExogenous, subTechnologiesEndogenous, subRegions: {...}}]]` |
| 24 | `get_technology(scenario_id, technology_name, region, subregion?, exogenous_sub_technology?, subsidy?, endogenous_sub_technology?)` | Get detailed yearly + monthly parameter values for one technology. | as listed | dict with `name, region, isRenewable, technologyGrouping, getExogenous{...}, getEndogenous{...}` — each with yearly `capacity / capex / opex / lifetimeBuildLimit / yearlyBuildLimit / loadFactorAverage / efficiency / efficiencySEL / marginalLossFactor` |
| 25 | `update_technology_endogenous(scenario_id, technology_name, parameter, transform, region, sub_region?, sub_technology?)` | Mutate endogenous technology assumption. | `parameter` is one of the technology parameters; `transform`: `List[Transform]` where each `Transform = {transform: {type: Percentage\|Delta\|Absolute, value: float}, year: int, month?: int}` | updated subtree |
| 26 | `update_technology_exogenous(scenario_id, technology_name, parameter, transform, region, sub_region?, subsidy?, sub_technology?)` | Mutate exogenous technology assumption. | as above + subsidy | updated subtree |

### 2.7 Inputs Service — Demand

| # | Method | Purpose | Args | Returns |
|---|--------|---------|------|---------|
| 27 | `get_demand_regions(scenario_id)` | List regions where demand assumptions can be inspected/edited. | `scenario_id: str` | `List[str]` |
| 28 | `get_demand(scenario_id, demand_filter=None, aggregate_regions=False)` | Get system demand + demand-tech variables for region(s). | `demand_filter`: `{region: str}` or `{regions: List[str]}` | `List[InputsDemand]` = `[{region, peakLoadDemand, variables: [yearly], technologies: [yearly]}]` |
| 29 | `update_system_demand(scenario_id, region, variable, transform, auto_capacity_market_target=None)` | Mutate a system-demand variable (e.g. baseDemand). | as above | updated subtree |
| 30 | `get_demand_technology_names(scenario_id, demand_technology_filter=None)` | List just demand-technology names per region (EVs, heat pumps, etc.). | `scenario_id, demand_technology_filter?` | list |
| 31 | `get_demand_technologies(scenario_id, demand_technology_filter=None)` | Get demand-technology variables (no system demand). | as above | list |
| 32 | `update_demand_technology_variable(scenario_id, region, technology, variable, transform, auto_capacity_market_target=None)` | Mutate a demand-tech variable. | as above | updated subtree |

### 2.8 Inputs Service — Commodities (fuel + carbon prices)

| # | Method | Purpose | Args | Returns |
|---|--------|---------|------|---------|
| 33 | `get_commodities(scenario_id, native_units_flag=None, regions=None, commodities=None)` | Get yearly commodity prices (gas, coal, carbon, biomass, etc.) for region(s). Defaults to global average. | `native_units_flag`: bool (MWh vs native), `regions`, `commodities`: optional filters | `{commodities: [{commodity, regions, prices: [{year, original, transform, validationWarnings, validationErrors}]}]}` |
| 34 | `update_commodity_price(scenario_id, commodity, regions, transform, native_units_flag=None)` | Mutate yearly commodity price. | as above | updated subtree |
| 35 | `change_base_commodities_assumptions(scenario_id, rebase_reference_id)` | Swap underlying commodity base data wholesale (transforms still apply on top). | `rebase_reference_id: str` | result |

### 2.9 Inputs Service — Interconnectors

| # | Method | Purpose | Args | Returns |
|---|--------|---------|------|---------|
| 36 | `get_interconnectors_connections(scenario_id)` | Adjacency dict: `{region: [connected_regions]}`. | `scenario_id: str` | `Dict[str, List[str]]` |
| 37 | `get_interconnectors(scenario_id, region, connection_region)` | Get yearly interconnector variables (capacity, etc.) between two regions, both directions. | as listed | dict with `ends, from, to, asymmetric, variables: [yearly]` |
| 38 | `update_interconnectors(scenario_id, from_region, to_region, variable, transform)` | Mutate an interconnector variable. | as listed | updated subtree |

**Total public methods on OriginSession: 38**

---

## 3. Convenience wrapper classes

### 3.1 `Project` (`src/origin_sdk/service/Project.py`)

Wraps a single project with a stateful interface.

| # | Method | Purpose | Args | Returns |
|---|--------|---------|------|---------|
| P1 | `__init__(project_id, session)` | Auto-fetches project. | `project_id, session: OriginSession` | `Project` |
| P2 | `get(key)` | Shortcut to underlying dict access. | `key: str` | value |
| P3 | `refresh()` | Re-fetch project. | — | `self` |
| P4 | `pin()` / `unpin()` | Idempotent pin/unpin. | — | `self` |
| P5 | `create_scenario(scenario_opts: InputScenario)` | Create scenario inside this project. | `scenario_opts` | `Scenario` |
| P6 | `get_scenario_by_name(scenario_name)` | Lookup scenario by name. | `scenario_name: str` | `Scenario` |
| P7 | `get_or_create_scenario_by_name(scenario_name, base_scenario_id)` | Idempotent scenario creation. | as listed | `Scenario` |
| P8 | `Project.get_project_by_name(session, name)` *(static)* | Lookup by name. | — | `Project` |
| P9 | `Project.create(session, project)` *(static)* | Create + wrap. | — | `Project` |
| P10 | `Project.get_or_create_project_by_name(session, name, create_config={}, pin_project=False)` *(static)* | Idempotent. | as listed | `Project` |

### 3.2 `Scenario` (`src/origin_sdk/service/Scenario.py`) — **the output-data accessor**

This is where actual market output CSVs are pulled.

| # | Method | Purpose | Args | Returns |
|---|--------|---------|------|---------|
| S1 | `__init__(scenario_id, session)` | Auto-fetches scenario details. | — | `Scenario` |
| S2 | `get_downloadable_regions()` | List region codes with downloads. | — | `List[str]` |
| S3 | `get_scenario_regions()` | Full region metadata dict, including auto-derived sibling regions (same regionGroup). | — | `Dict[str, RegionDict]` |
| S4 | `get_scenario_region(region)` | Single region metadata. | `region: str` | `RegionDict` (`regionCode, metaUrl, dataUrlBase`) |
| S5 | `get_download_types(region)` | **Lists what output products are available**: returns list of `{type, granularity, subType}` for the region. *Examples surfaced by docstrings: `type ∈ {"system", "technology", "interconnector", "nodal", …}`; `granularity ∈ {"1y", "1m", "1h"}`.* | `region: str` | `List[{type, granularity, subType}]` |
| S6 | `get_download_years(region)` | Valid years for downloads (e.g. forecast horizon). | `region: str` | `List[int]` |
| S7 | **`get_scenario_data_csv(region, download_type, granularity, currency=None, year=None, node=None, sub_type=None, force_no_cache=False, params=None)`** | **THE MAIN DATA METHOD.** Downloads a CSV (with two header rows: column + units). Examples from docstring shown below. | as listed | CSV as `str` |
| S8 | `get_scenario_dataframe(...)` | Deprecated; same args as S7 but parses with pandas. | as S7 | `pd.DataFrame` |
| S9 | `refresh()` | Re-fetch scenario state (for polling launch progress). | — | `self` |
| S10 | `get(key)` | Underlying dict shortcut. | `key: str` | value |
| S11 | `Scenario.get_latest_scenario_from_region(session, region, name_filter=None)` *(static)* | Get most recently published Aurora scenario for a region; can filter by name substring(s). | as listed | `Scenario` |

#### Documented `get_scenario_data_csv` examples (verbatim from docstring)

```python
# Annual GB system-level summary
csv_data = scenario.get_scenario_data_csv('gbr', 'system', '1y')

# Hourly nodal data for ERCOT, in USD2024, for a specific node
csv_data = scenario.get_scenario_data_csv(
    region='erc', download_type='nodal', granularity='1h',
    currency='usd2024', node='ZONDWD_6_B1',
)

# Hourly interconnector data between Peninsular Europe / Germany for year 2028
csv_data = scenario.get_scenario_data_csv(
    region='peu_deu', download_type='interconnector',
    granularity='1h', year=2028,
)
```

> The `download_type` values **`"system"`, `"technology"`, `"interconnector"`, `"nodal"`** are confirmed by docstring examples. **`"battery"`, `"storage"`, `"capture"`, or `"tb_spread"` are not mentioned anywhere in the SDK source.** Whether such types exist depends on the per-scenario `dataDefinitions` metadata published by Aurora's backend for the GB region.

### 3.3 `InputsEditor` (`src/origin_sdk/service/InputsEditor.py`) — BETA

Friendlier wrapper around the inputs methods on `OriginSession`. Docstring marks this **BETA**, contract may change.

| # | Method | Purpose |
|---|--------|---------|
| I1 | `__init__(scenario_id, session)` | Auto-loads inputs session. |
| I2 | `refresh()` | Re-fetch. |
| I3 | `get_demand_regions()` | Pass-through to `OriginSession.get_demand_regions`. |
| I4 | `get_demand_for_region(region)` | Pass-through to `OriginSession.get_demand`. |
| I5 | `get_demand_technologies()` | Pass-through. |
| I6 | `update_system_demand_variable(region, variable, transform, auto_capacity_market_target=None)` | Pass-through. |
| I7 | `update_demand_technology_variable(region, technology, variable, transform, auto_capacity_market_target=None)` | Pass-through. |
| I8 | `get_technology_names()` *(cached)* | Pass-through. |
| I9 | `get_supply_technology(technology_name, region, subregion?, exogenous_sub_technology?, subsidy?, endogenous_sub_technology?)` | Pass-through. |
| I10 | `update_exogenous_technology_variable(...)` | Pass-through. |
| I11 | `update_endogenous_technology_variable(...)` | Pass-through. |
| I12 | `get_commodities(*args, **kwargs)` | Pass-through. |
| I13 | `update_commodity_price(*args, **kwargs)` | Pass-through. |
| I14 | `change_base_commodities_assumptions(*args, **kwargs)` | Pass-through. |

**Total wrapper-class methods: 10 + 11 + 14 = 35.**

---

## 4. GraphQL queries shipped with the SDK (raw query strings)

Listed for completeness — these are what each session method dispatches under the hood.

### 4.1 `project_queries.py` (7 queries)
- `get_origin_dash_config` — returns `{regionGroups, currencies, sensitivities, products, isAuthor, isAdvancedUser, appsSupported}`. Used internally by `get_project_product_id`.
- `get_projects` — list projects.
- `get_project($projectId)` — one project + scenarios.
- `create_project($project: InputProject!)` — mutation.
- `update_project($project: UpdateProjectInputGroup!)` — mutation.
- `delete_project($projectGlobalId: String!)` — mutation.
- `pin_project` / `unpin_project($projectGlobalId)` — mutations.

### 4.2 `scenario_queries.py` (7 queries)
- `get_scenarios($filter: ScenarioFilter)` — list by filter (region, scenarioType).
- `get_scenario_details($filter: ScenarioFilter)` — detailed.
- `create_scenario / update_scenario / delete_scenario / launch_scenario` — mutations.
- `get_weather_years($scenarioGlobalId)` — list supported weather years.

### 4.3 `config_queries.py` (1)
- `get_origin_regions` — returns `regionGroups`.

### 4.4 `input_queries/` (sub-modules)
- `session.py` → `create_get_session_gql(...)`, `get_session_information_gql` (gets session meta + `productRegionInformation.enabledRegions` with **`hasCapacityMarket`** flag per region).
- `config.py` → `get_config_gql` (returns global config: technology parameter list, demand variables, commodities region mapping, interconnectors variables, userPermissions). Plus helpers `get_endo_exo_param_list_from_config`, `get_demand_variables_from_config`, `get_interconnector_variables_from_config`.
- `technology.py` → `get_technology_names_gql`, `get_technology_gql`, `update_endo_technology_gql`, `update_exo_technology_gql`. Yearly parameters: `capacity, capex, opex, lifetimeBuildLimit, yearlyBuildLimit, loadFactorAverage, efficiency, efficiencySEL, marginalLossFactor`. Definitions: `discountRate, discountRateLow`.
- `demand.py` → `get_demand_regions_gql`, `get_demand_gql`, `update_system_demand_gql`. Demand object has `region, peakLoadDemand, variables, technologies`.
- `tech_demand.py` → `get_demand_technology_names`, `get_demand_technologies_gql`, `update_demand_technology`. Tech variables include `region, technology, originTechnology`.
- `commodities.py` → `get_commodities_gql`, `update_commodity_gql`, `rebase_commodities_gql`.
- `interconnectors.py` → `get_interconnectors_gql`, `get_interconnectors_regions_gql`, `update_interconnectors`. Vars: `ends, from, to, asymmetric, variables`.
- `workbook.py` → `get_workbook_status`.
- `utils.py` → tree-building helpers, `Transform` field shapes.

---

## 5. Key data types

### 5.1 `InputScenario` (creating a clone of an Aurora scenario)

```python
{
  "projectGlobalId": str,       # required: containing project
  "name": str,                   # required
  "baseScenarioGlobalId": str,   # required for non-Aurora: which Aurora central case to clone
  "description": str,            # optional
  "regionGroupCode": str,        # e.g. "GBR", "AUS", "DEU"
  "useExogifiedInputs": bool,    # True = "Model Determined Capacity OFF" (faster, fixed capacity)
  "defaultCurrency": str,
  "weatherYear": int,            # only valid for useExogifiedInputs=True
  # Internal-only: scenarioRunType, modelType, modelPriceSpikiness, years, advancedSettings, retentionPolicy
}
```

### 5.2 `ScenarioSummaryType` (key fields)

- `scenarioGlobalId, name, regionGroupCode, publishType, publicationDate`
- `scenarioRunStatus`: `Queued / Running / Complete / Errored / NotLaunched`
- `scenarioType`: `AURORA_SCENARIO` or `TENANTED_SCENARIO`
- `scenarioRunType`: `MYR / FYR / MYR_AND_FYR / NODAL / NODAL_PLACEMENT / REGIONAL_*  / NETWORK`
- `inputTypesSupported`: `EXOGENOUS_ONLY / ENDOGENOUS_ONLY / ENDOGENOUS_AND_EXOGENOUS`
- `modelPriceSpikiness`: `None / Low / Medium / High` (AUS only per docstring)
- `weatherYear, years, runDetails, scenarioOutputsAvailable`

### 5.3 `RegionDict`

`{regionCode, metaUrl, dataUrlBase, __meta_json}` — `metaUrl` is the manifest that defines `dataDefinitions[]` for available CSV downloads.

### 5.4 `Transform`

`{transform: {type: "Percentage" | "Delta" | "Absolute", value: float}, year: int, month?: int}` — used in every `update_*` mutation.

### 5.5 `InputsSession.productRegionInformation.enabledRegions[*]`

Each enabled region exposes:
- `code, isFocusRegion, isEndogenous, isMainRegion, hasCapacityMarket` ← capacity market flag is the closest thing to an ancillary/market-product hint at session level.

### 5.6 Exceptions
`ScenarioNotFound`, `ProjectNotFound`, `ProjectProductNotFound`.

---

## 6. Findings table mapped to APD/BESS-GB benchmarking needs

| Capability we need | SDK method | Accessible w/ token | Forecast/historical | GB/UK | BESS-relevant |
|---|---|---|---|---|---|
| List GB Aurora central cases | `OriginSession.get_aurora_scenarios(region="gbr")` | yes | forecast (scenario) | yes | partial — depends on product |
| Pull GB system price curves (annual, monthly, hourly) | `Scenario.get_scenario_data_csv("gbr", "system", "1y"\|"1m"\|"1h")` | yes (if scenario allows) | forecast | yes | partial — system price ≠ TB spread |
| Pull battery / storage outputs as a `download_type` | `Scenario.get_scenario_data_csv(...)` w/ `download_type="battery"` (??) | **unknown** — not declared in SDK; must check `Scenario.get_download_types("gbr")` against a battery-product scenario | forecast | yes | yes IF supported by product |
| Pull interconnector flows | `Scenario.get_scenario_data_csv("gbr_xxx", "interconnector", "1h", year=YYYY)` | yes | forecast | yes | no |
| Pull nodal price data | `Scenario.get_scenario_data_csv(region, "nodal", "1h", node=...)` | yes (markets like ERCOT shown; **GB-nodal availability unknown**) | forecast | partial | no |
| TB spreads (top-bottom spread by duration) | none — not a named concept in SDK | **unknown — must be a `download_type` if at all** | n/a | n/a | yes |
| Capture rate (battery / solar / wind) | none — not a named concept in SDK | **unknown — must be a `download_type` if at all** | n/a | n/a | partial |
| Day-ahead vs intraday split | none — not a named concept in SDK | **probably not** | n/a | n/a | yes |
| Ancillary service revenues (FFR, DC, DM, DR) | none — not a named concept in SDK | **probably not** | n/a | n/a | yes |
| BMU-level historical output / dispatch | none | **no** — SDK is forecast/scenario-only | n/a | n/a | n/a |
| Modify commodity prices (gas, carbon) and rerun | `update_commodity_price` + `launch_scenario` + `get_scenario_data_csv` | yes | forecast | yes | partial — useful for sensitivity studies |
| Modify capacity build (e.g. add 1 GW BESS) and rerun | `update_technology_exogenous`/`endogenous` + `launch_scenario` | yes | forecast | yes | yes — useful for PSP what-if |
| Historical wholesale (DA/ID) actuals | none | **no** | n/a | n/a | yes |
| Workbook of inputs assumptions (Excel) | `get_workbook_download_url` | yes | n/a | yes | yes |

---

## 7. What is NOT in the SDK

Confirmed via full-text search of the source (no matches):

- `battery`, `BESS`, `storage` — zero occurrences
- `TB`, `top.bottom`, `spread` — zero occurrences
- `capture` (rate / price) — zero occurrences
- `ancillary` (services / revenues) — zero occurrences
- `balanc` (balancing market) — zero occurrences
- `day.ahead`, `intraday` — zero occurrences
- `forecast`, `historic` (in user-facing methods) — only an internal `isHistoricRun` flag inside `AdvancedScenarioSettings`
- `BMU`, `Elexon`, `NESO`, `MID` — zero occurrences

This does **not** prove Aurora's backend doesn't serve these — only that the SDK does not surface them as named methods. To test, one would need a live API key, call `get_download_types("gbr")` on each of the GB-region Aurora scenarios available to the tenant, and inspect what `type` / `subType` values appear in the manifest.

---

## 8. Next step (for the parent agent / Ankit)

1. **Empirical step needed.** The static inventory above maxes out what the source reveals. To know whether GB battery / TB-spread / capture-rate / ancillary outputs are accessible via `get_scenario_data_csv`, run (with a live key):
   ```python
   from origin_sdk.OriginSession import OriginSession
   from origin_sdk.service.Scenario import Scenario
   s = OriginSession()
   gb_scenarios = s.get_aurora_scenarios(region="gbr")
   # Inspect each scenario's product/name; instantiate Scenario(id, s); call get_download_types("gbr").
   ```
   The MPA Solar Europe email Cyrus is provisioning (per APD CLAUDE.md status note) is the key blocker.

2. **Reasonable expectation.** Aurora publishes a **GB battery / storage product** in Origin (this is publicly advertised on their commercial site). The SDK gives no static affirmation; the per-scenario `dataDefinitions` is where any `"battery"` or `"storage"` `type` would surface. Need to verify live.

3. **No retrieval of Northwold-grade actuals.** Aurora Origin is for *forward-looking simulations*. Use it for benchmarking *projected* TB spread / capture / ancillary stacks, **not** historic Northwold-vs-benchmark comparison (Modo Energy / EPEX / GridBeyond invoice remain the primary actuals sources).

---

*Inventory compiled 2026-06-01 by deep-research subagent against repo HEAD on `main`.*
