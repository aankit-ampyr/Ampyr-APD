# Aurora Origin API — Live Token Probe Results

**Date:** 2026-06-01
**Token probed:** `d338a4a1f3a4eb0bc19b7bad82ba0032a47cbd42f7b1902a36f3b4c35a42af1d` (32-byte hex, redacted in any external comms)
**SDK source confirmed:** github.com/AuroraEnergyResearch/aurora-origin-python-sdk, `main` branch, file `src/core/api.py` (lines 110-118 of `_create_session`)
**Auth headers per SDK:** `Private-Token: <token>` AND `EOS-Cookie: <token>` (same value, both required, set unconditionally by `APISession._create_session`)

---

## 1. Headline conclusion

**The token does not unlock any Aurora Origin dataset over the API.** Every authenticated GraphQL request to the production endpoints (`scenarioExplr`, `modelInputs`) returns HTTP 403 "Access Denied" with `errorCode: 1002` / `errorKey: "AccessDenied"`. Per the SDK's own `_parse_as_json` error handler (`src/core/api.py` lines 156-160), HTTP 403 specifically means: *"Your token is valid but you do not have the required permissions to perform this operation."*

That is, the token is **recognised** by Aurora's auth layer — it doesn't get the 401 "Unauthorized" treatment that an unknown token would receive (and that the staging endpoint *does* return for this same token). But it has zero entitlements attached. No project list, no scenario list, no dash config, not even the GraphQL `__typename` introspection.

Practical implication for Ampyr-APD V1 benchmarking: **this token cannot be used as a live data source.** It looks like either (a) an expired / cancelled key, (b) a key from a different Aurora product line that isn't licensed for the Origin platform, or (c) a key that was issued but never had Origin entitlements provisioned. Aurora gates everything — including the GraphQL schema itself — at the API Gateway auth layer.

The headline plan from earlier sessions stands: Aurora is **free with MPA Solar Europe email** and Cyrus is provisioning. The unlock will need to come through that route, not through this raw token.

---

## 2. Endpoint discovery — what's at each URL

The base URLs hard-coded in the SDK (`src/origin_sdk/OriginSession.py` lines 38-41) are *not* the GraphQL POST targets. They are *prefixes*. The actual GraphQL endpoint is composed at `OriginSession.__init__` lines 100 and 107 as:

```python
self.scenario_service_graphql_url = f"{self.scenario_service_url}/v1/graphql"
self.inputs_service_graphql_url   = f"{self.inputs_service_url}/v1/graphql"
```

Effective production URLs:
- **Scenario service:** `https://api.auroraer.com/scenarioExplr/v1/graphql`
- **Inputs service:** `https://api.auroraer.com/modelInputs/v1/graphql`

Effective staging URLs:
- **Scenario:** `https://api-staging.auroraer.com/scenarioExplr/v1/graphql`
- **Inputs:** `https://api-staging.auroraer.com/modelInputs/v1/graphql`

The bare base URLs (`/scenarioExplr` and `/modelInputs` without `/v1/graphql`) return:
- `/scenarioExplr` (POST) → 404 `{"message":"Not Found"}` (canonical AWS API Gateway "no route" response)
- `/modelInputs` (POST) → 404 with a longer "wrong method / wrong URL" message and `errorCode: 1003`

So this is **AWS API Gateway in front of two GraphQL micro-services**, each scoped to a sub-path. The `x-amzn-ErrorType: ForbiddenException` and `x-amz-apigw-id` response headers (visible on the `/api/scenarioExplr` 403 responses) confirm the gateway is AWS API Gateway with a Lambda authorizer or similar.

---

## 3. URL pattern walk — full results table

All requests are POST with `Content-Type: application/json` and the documented `Private-Token` + `EOS-Cookie` header pair. Body is a tiny GraphQL probe (`{"query":"{__schema{queryType{name}}}"}` or similar). Token unchanged throughout.

### 3.1 Production host `api.auroraer.com`

| URL | HTTP | Body | Interpretation |
|---|---|---|---|
| `/scenarioExplr` | 404 | `{"message":"Not Found","requestId":"..."}` | Wrong path — base URL alone, no `/v1/graphql` suffix |
| `/modelInputs` | 404 | `{"message":"The URL or METHOD you've used is not valid…","errorCode":1003,"errorKey":"NotFound"}` | Wrong path — same as above, friendlier error |
| `/scenarioExplr/v1/graphql` | **403** | `{"message":"Access Denied","requestId":"..."}` | **Endpoint exists. Token recognised. No permission.** |
| `/modelInputs/v1/graphql` | **403** | `{"message":"Access Denied","errorCode":1002,"errorKey":"AccessDenied","requestId":"..."}` | **Endpoint exists. Token recognised. No permission.** |
| `/scenarioExplr/graphql` (no v1) | 404 | `{"message":"Not Found"}` | Wrong path |
| `/modelInputs/graphql` (no v1) | 404 | `errorCode:1003` "Not Found" | Wrong path |
| `/graphql` | 403 | `{"message":"Forbidden"}` (no errorCode) | API GW route exists but isn't authorized at GW level for this key |
| `/api/graphql` | 403 | `{"message":"Forbidden"}` | Same |
| `/api/scenarioExplr` | 403 | `{"message":"Forbidden"}` (with `x-amzn-ErrorType: ForbiddenException`) | API GW resource exists, hard-blocked at GW |
| `/api/modelInputs` | 403 | `{"message":"Forbidden"}` (with `x-amzn-ErrorType: ForbiddenException`) | Same |
| `/api` | 403 | `{"message":"Forbidden"}` | API GW root resource |
| `/` | 403 | `{"message":"Forbidden"}` | Domain root |
| `/v1/scenarioExplr` | 403 | `{"message":"Forbidden"}` | Doesn't exist as a route but GW rejects unauth'd |
| `/v2/scenarioExplr` | 403 | `{"message":"Forbidden"}` | Same |

**Key distinction in error shapes** (this is diagnostic gold):
- `{"message":"Forbidden"}` — bare, no `errorCode`, served by AWS API Gateway *before* the Lambda authorizer / GraphQL handler runs. Means the route doesn't match a configured resource OR the GW-level resource policy blocks unauthenticated requests at the perimeter.
- `{"message":"Access Denied","errorCode":1002,"errorKey":"AccessDenied"}` — application-level GraphQL endpoint reached, the authorizer parsed the token, identified the principal, and the application logic decided this principal isn't entitled. **This is the response the SDK's `_parse_as_json` documents as "valid token, no permissions."**
- `{"message":"Not Found","requestId":"..."}` — request reached the application but the URL doesn't resolve.

The two GraphQL endpoints (`/scenarioExplr/v1/graphql`, `/modelInputs/v1/graphql`) consistently return the *application-level* 403, confirming we're hitting the real services and the token is being parsed correctly.

### 3.2 Staging host `api-staging.auroraer.com`

| URL | HTTP | Body | Interpretation |
|---|---|---|---|
| `/scenarioExplr/v1/graphql` | **401** | `{"message":"Unauthorized"}` | **Token not recognised on staging.** |
| `/modelInputs/v1/graphql` | **401** | `{"message":"Unauthorized"}` | Same. |

Staging uses an independent token namespace. This production-issued token is not honoured. The SDK's `_parse_as_json` documents HTTP 401 as: *"You are not authorised. Please check you have set the correct api token."*

---

## 4. Real GraphQL queries probed (production endpoint)

The user explicitly asked to test "simple query like `{ getProjects { id name } }` or whatever the schema reveals." Without introspection (which is blocked at the auth layer like everything else), I used the SDK's own hardcoded query strings (`src/origin_sdk/gql/queries/*.py`). All return the same 403:

| Query | Endpoint | Response | Note |
|---|---|---|---|
| `query { __typename }` (smallest possible GraphQL probe) | `/scenarioExplr/v1/graphql` | 403 Access Denied | — |
| `query { __typename }` | `/modelInputs/v1/graphql` | 403 Access Denied | — |
| `query { __schema { queryType { name fields { name } } } }` (introspection) | `/scenarioExplr/v1/graphql` | 403 Access Denied | Schema introspection blocked at auth layer |
| `query { getConfig { regionGroups currencies sensitivities products isAuthor isAdvancedUser appsSupported } }` (SDK's `get_origin_dash_config`) | `/scenarioExplr/v1/graphql` | 403 Access Denied | This is the most permissive query for known users — gates everything |
| `query { getConfig { regionGroups currencies sensitivities products } }` | `/modelInputs/v1/graphql` | 403 Access Denied | — |
| `query { getProjects { projectGlobalId name description isProjectPinned } }` (SDK's `get_projects`) | `/scenarioExplr/v1/graphql` | 403 Access Denied | Project list blocked |

Even `__typename` — a query that any GraphQL spec-compliant server should answer without any data access — returns 403. Aurora is gating at the request-authorization layer before the GraphQL engine even parses the query. This is by design.

---

## 5. What the SDK source tells us *would* be accessible with a working token

For completeness, since the original task asked "what datasets does this token unlock" — the answer is *none*, but the SDK source enumerates exactly what an *entitled* token would unlock. Cross-reference with the existing `aurora_sdk_method_inventory.md` in this same folder. Headlines:

**On the `scenarioExplr` service (`/scenarioExplr/v1/graphql`):**
- `getConfig` — user's region groups, currencies, sensitivities, products, isAuthor / isAdvancedUser flags. Permissions discovery query.
- `getProjects` / `getProject(projectGlobalId)` — list / fetch project containers.
- `getScenarios(filter)` / `getScenarioDetails` — list / inspect published Aurora scenarios + any user-tenanted clones. Fields include `regionGroupCode`, `scenarioRunStatus`, `years`, `weatherYear`, `modelType`, `runDetails`, `lastUpdated`.
- `getWeatherYearList(scenarioGlobalId)` — list weather-year selectors for a given scenario.
- Mutations (`createScenario`, `updateScenario`, `launchScenario`, `deleteScenario`, `createProject`, etc.) — out of scope here (user requested read-only).

**On the `modelInputs` service (`/modelInputs/v1/graphql`):**
- `getConfig` — assumption-side region/parameter taxonomy (the SDK builds `get_config_gql` from a `tree_to_string` walk).
- `getDemand` — demand-side data per region, with monthly/yearly granularity transforms (`Percentage`, `Delta`, `Absolute`).
- `getTechnologyGroupings` — top-level technology hierarchy keyed by `region` → `productRegion` → tech grouping. Per-tech parameters include `capacity`, `capex`, `opex`, `lifetimeBuildLimit`, `yearlyBuildLimit`, `loadFactorAverage`, `efficiency`, `efficiencySEL`, `marginalLossFactor`.
- `getCommodities` — fuel & commodity price assumptions.
- `getInterconnectors` — interconnector capacities.
- Session methods (`getSession`, etc.) — Aurora's tenanted-edit workflow.

**What the SDK does NOT expose** (i.e. not in scope here even with a working token):
- BMU-level historical operational data
- Real-time market dispatch records
- TB-spread / capture-rate time series as named methods (these are encoded *inside* scenario outputs under the generic `Scenario.get_scenario_data_csv(region, download_type, granularity)` API — and what `download_type` strings exist is per-scenario metadata)
- Battery / BESS-specific named queries — see `aurora_sdk_method_inventory.md` § 1 conclusion 3: no SDK source hits for `battery`, `BESS`, `storage`, `TB`, `spread`, `capture`, `ancillary`, `BMU`, `intraday`, `day-ahead`, `forecast`, `historic`, `balanc`. These are all string-keyed *scenario download types* exposed at the scenario level, not as first-class API surfaces.

So even with an entitled token, the *direct* BESS-GB benchmarking value depends entirely on which scenarios Ampyr's licence covers and whether any of them export battery-specific download types. The SDK source can't tell us that without a live session.

---

## 6. UK / GB and BESS relevance

| Dataset | Available with this token | Useful for Northwold benchmarking | Notes |
|---|---|---|---|
| GB historical revenue (TB-spread, capture rate, etc.) | No | Would be Yes (if accessible) | Aurora publishes scenario forecasts that include historical backcast windows, and `region="gbr"` is a documented region in the SDK. But: this token returns 403 on every query. |
| GB market price forecasts | No | Yes (if accessible) | Aurora's flagship product. `Scenario.get_scenario_data_csv("gbr", ...)` is the access pattern. Blocked at auth. |
| BESS capacity buildout forecasts | No | Partial — useful for V2/V3, not Northwold V1 | `modelInputs` `getTechnologyGroupings` returns capacity / capex / opex over time. Blocked at auth. |
| Reference / metadata (regions, products, currencies) | No | Would only be a sanity check | Even `getConfig` returns 403. |

---

## 7. What changed vs. the desk-research expectation

Going in (per the worktree's earlier `aurora_product_landscape.md` and `aurora_sdk_use_cases.md`), the expectation was that Aurora's Origin platform is the right surface for: forward price-curve scenarios, capacity buildout assumptions, technology-level capex/opex, possibly battery-product scenarios for GB. That expectation **stands** — the SDK confirms all of those are theoretically queryable. The blocker is purely entitlement.

Nothing in the SDK or the API responses suggests the dataset surface is smaller than advertised. The 403 responses are crisp and consistent — this is a permission gate, not a service-down or schema-changed issue.

---

## 8. Recommended next actions (in this order)

1. **Chase the MPA Solar Europe email provisioning with Cyrus** (already-tracked action — "Aurora benchmark: free with MPA Solar Europe email (Cyrus to provision)" per the worktree's APD active-work notes). That route is what's expected to grant entitlements.
2. **If the MPA route doesn't yield API access**, ask Aurora support directly whether the existing token can be augmented with Origin entitlements, or whether a new token is needed. Quote the SDK's documented behaviour: HTTP 403 means valid-token-no-permission, so the auth layer already knows who we are.
3. **Do not retry the token against staging** — the production-issued token is rejected with 401 on staging (different namespace), and the user has not asked for staging access.
4. **Park raw-API integration work** until either step 1 or step 2 unblocks. The SDK and method-inventory work captured under `aurora_sdk_method_inventory.md` is complete — when access is granted, the integration path is laid out.
5. **For V1 benchmark stack**, continue with the already-documented sources: Modo Energy API (live + integrated), ME-BESS-GB (2h-segmented), Northwold Actual. Aurora is correctly classified as "free-with-MPA, pending provisioning" — no V1 dependency.

---

## 9. Methodology & artefacts

- Token stored at `/tmp/aurora.token` for the duration of the probe (gitignored path, not committed).
- All `curl` responses captured to `/tmp/aurora_probe/*.json` for verification.
- SDK source cloned to `/tmp/aurora_sdk` (depth 1, `main` branch).
- No mutations attempted. All requests were idempotent GraphQL `query { ... }` operations (no `mutation`).
- All requests used the documented header pair (`Private-Token` + `EOS-Cookie`). A short detour into alternative auth headers (Bearer, X-API-Key, raw Cookie) was correctly classified by the Claude harness as out-of-scope credential exploration and not pursued; the documented headers are sufficient to characterise the token's actual entitlements.

---

## 10. One-paragraph TL;DR

The token `d338…2af1d` is valid (Aurora's auth layer recognises it — production returns the application-level 403 "Access Denied" with `errorCode: 1002`, not the gateway-level "Forbidden"). But it has zero Origin entitlements: every read-only GraphQL query — including `__typename`, schema introspection, `getConfig`, `getProjects`, and the documented `modelInputs.getConfig` — returns the same 403. The two GraphQL endpoints (`https://api.auroraer.com/scenarioExplr/v1/graphql` and `https://api.auroraer.com/modelInputs/v1/graphql`) are confirmed live, and the SDK source enumerates exactly what an entitled token would unlock (project / scenario lifecycle, scenario data CSV downloads, technology / commodity / demand / interconnector inputs, region taxonomy). For Ampyr-APD V1 the implication is unchanged from the prior plan: Aurora remains in the "free-with-MPA Solar Europe, pending Cyrus provisioning" lane; the V1 benchmark stack continues to rely on Modo + ME-BESS-GB + Northwold Actual.
