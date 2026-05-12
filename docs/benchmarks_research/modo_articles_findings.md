# Modo Energy GB BESS Benchmark — Research Findings

**Research date:** 23 April 2026
**Researcher:** Claude (automated web research)
**Source:** Modo Energy monthly GB BESS Index research articles (https://modoenergy.com/research)
**Method:** Google web search (`site:modoenergy.com`) + WebFetch of individual article pages. All values are sourced directly from Modo's article preview text (above-the-paywall content). All seven article URLs were located and fetched successfully.

---

## Headline Findings (Summary)

| Month | Hardcoded (existing) | Modo actual (£/MW/yr) | Match? | Confidence |
|------|----------------------|------------------------|---------|------------|
| Sep 2025 | £70,000 | **£70,000** | OK | High |
| Oct 2025 | £77,000 | **£77,000** | OK | High |
| Nov 2025 | £59,000 | **£59,000** | OK | High |
| Dec 2025 | £47,000 | **£47,000** | OK | High (Modo's Jan 2026 article quotes Dec at £48k after revision — see Notes) |
| Jan 2026 | £88,000 | **£52,000** | **MISMATCH** | High (£88k is the **January 2025** figure, not January 2026) |
| **Feb 2026** | (missing) | **£41,000** | NEW | High (record low — lowest since Feb 2024) |
| **Mar 2026** | (missing) | **£70,000** | NEW | High |

### Critical correction
The hardcoded **January 2026 = £88,000** value is the **January 2025** Modo benchmark, not January 2026. Modo's actual published January 2026 headline is **£52k/MW/year**. The £88k January 2025 figure was reported in Modo's January 2025 GB research roundup: "Battery energy storage revenues in Great Britain reached a rate of £88k/MW/year in January 2025, marking a 5% increase from December 2024".

---

## Detailed Table

| Month | Value (£/MW/yr) | Source URL | Confidence | Notes |
|-------|-----------------|------------|------------|-------|
| Sep 2025 | £70,000 | https://modoenergy.com/research/battery-energy-storage-revenues-gb-september-2025-balancing-mechanism-frequency-response | High | +15% vs Aug; on par with year's average; frequency response hit £27k/MW/yr (highest in two years) |
| Oct 2025 | £77,000 | https://modoenergy.com/research/en/battery-energy-storage-revenues-gb-october-2025-record-balancing-mechanism-dispatch-rates | High | +11% vs Sep; +36% vs Jul 2025 low; frequency response £30k/MW/yr (two-year high) |
| Nov 2025 | £59,000 | https://modoenergy.com/research/en/me-bess-gb-battery-energy-storage-revenues-november-2025-balancing-mechanism-gas-wind | High | -21% vs Oct; 2nd-lowest month of 2025 (Jul was £55k); frequency response dropped 22% to £23k/MW/yr |
| Dec 2025 | £47,000 | https://modoenergy.com/research/en/me-bess-gb-battery-energy-storage-revenues-december-2025-low-demand-christmas | High | -19% vs Nov; lowest month of 2025; -45% YoY (Dec 2024 was £86k). NB: Modo's Jan 2026 article retrospectively quotes Dec 2025 as £48k — likely minor revision after settlement; £47k is the original publication figure |
| Jan 2026 | £52,000 | https://modoenergy.com/research/en/me-bess-gb-revenues-january-2026-balancing-mechanism-wholesale-prices-gas-carbon | High | +9% vs Dec (£48k restated); -44% YoY; Balancing Mechanism +£6.4k/MW/yr drove recovery; wholesale arbitrage at three-year low (£5.1k/MW/yr) |
| **Feb 2026** | **£41,000** | https://modoenergy.com/research/en/me-bess-gb-revenues-february-2026-wholesale-battery-energy-storage-balancing-mechanism | High | -23% vs Jan (£54k as restated in Feb article); -47% YoY; **lowest monthly figure since Feb 2024**; wholesale revenues went **negative for first time** at -£6k/MW/yr; wind avg 11.4 GW suppressed spreads |
| **Mar 2026** | **£70,000** | https://modoenergy.com/research/en/me-bess-gb-revenues-rise-march-2026-balancing-mechanism-record-gas-prices- | High | **+69% vs Feb**; among highest months of past year; **record Balancing Mechanism revenues of £46k/MW/yr**; day-ahead spreads £89/MWh (+123% MoM); intraday £95/MWh (+76% MoM); Middle East tensions drove gas prices |

---

## Restatement / Revision Notes

Modo's monthly figures are occasionally adjusted slightly in subsequent articles as settlement data finalises. Cross-referencing observed:

| Month | Original publication | Restated in later article |
|-------|---------------------|---------------------------|
| Dec 2025 | £47k | £48k (per Jan 2026 article opening paragraph) |
| Jan 2026 | £52k (per Jan 2026 article) | £54k (per Feb 2026 article opening paragraph) |

These ~£1–2k drifts are within normal settlement revision. Recommendation: store the **original publication figure** for historical consistency, or adopt Modo's most-recent restatement if a single source-of-truth field is preferred.

---

## Duration-Segmented Data (1H vs 2H)

Modo publishes **three GB BESS indices** (per https://modoenergy.com/methodology/gb):

| Index | Coverage | Available from |
|-------|----------|----------------|
| **ME BESS GB** | All qualifying assets (headline figure quoted above) | Full history |
| **ME BESS GB (1H)** | Assets with system duration < 1.5 hours | Full history |
| **ME BESS GB (2H)** | Assets with system duration 1.5–2.5 hours | 1 Jan 2023 onwards |

**Important:** The duration-segmented values (1H and 2H) are **NOT quoted** in any of the seven monthly headline articles reviewed. They are published on Modo's Terminal platform (subscriber product) and used as FCA-authorised benchmarks for revenue swap contracts. The methodology page confirms only that:

> "Battery energy storage in GB earned between £55,000 and £120,000 per MW in 2023–2025"
> (range across the indices, period: 2023-2025)

> "For a representative 2-hour asset, the ME BESS GB Index halves the basis risk compared to day-ahead spreads (average daily gap of £29/MW vs £61/MW)."

**Industry-average duration context (from Modo Q4 2025 Buildout Report):**
- Total energy capacity: 11 GWh
- Total rated power: 6.8 GW
- **Average GB BESS duration: 1.62 hours** (up from 1.57 hours at end of Q3 2025)

This means the headline ME BESS GB Index is weighted toward ~1.6h assets (closer to the 2H bucket than 1H). For a like-for-like comparison of Northwold Solar Farm BESS (8.4 MWh / 7 MW = **1.2-hour duration**), the **ME BESS GB (1H) index would be more appropriate** than the headline — but its values are paywalled.

**Action item:** To obtain 1H-segmented values, contact Modo Energy directly (subscription or one-off data request) — they are not surfaced in any public article preview.

---

## Source Articles Summary

All seven Modo articles successfully located:

1. **Sep 2025**: "ME BESS GB: Revenues increase to £70k/MW/year in September 2025"
2. **Oct 2025**: "ME BESS GB: Revenues climb to £77k/MW/year in October 2025"
3. **Nov 2025**: "ME BESS GB: Revenues fall to £59k/MW/year in November 2025"
4. **Dec 2025**: "ME BESS GB: Revenues fall to £47k/MW/year in December 2025"
5. **Jan 2026**: "ME BESS GB: Revenues Climb to £52k/MW/year in January 2026"
6. **Feb 2026**: "ME BESS GB: Revenues fall to £41k/MW/year in February 2026"
7. **Mar 2026**: "ME BESS GB: Revenues climb to £70k/MW/year in March 2026"

The pattern "ME BESS GB: [direction] to £[X]k/MW/year in [Month] [Year]" is consistent and machine-readable — could be exploited for future automated scraping. URL slugs have stabilised to `me-bess-gb-...-[month]-[year]-...` since November 2025.

---

## Recommendations for `streamlit_dashboard.py` / benchmarks data

1. **Fix Jan 2026**: Change hardcoded £88,000 to **£52,000** (the £88k value was Jan 2025).
2. **Add Feb 2026 row**: £41,000 — flag in UI as "record low — wholesale negative for first time".
3. **Add Mar 2026 row**: £70,000 — flag as "+69% MoM rebound on record Balancing Mechanism revenues".
4. **Consider revisions field**: Modo's monthly numbers can drift ±£1–2k in subsequent articles. Either freeze on original publication or always use latest restatement. Current Dec 2025 (£47k) and Jan 2026 (£52k) are original-publication values.
5. **Duration caveat**: Add a footnote that the ME BESS GB headline is industry-average (~1.6h duration); Northwold (1.2h) is closer to the 1H sub-index, which Modo does not publish publicly. The headline likely under-represents 1H asset revenues during high-volatility months (where 1H typically out-earns 2H on £/MW/yr).
