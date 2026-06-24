"""Solar dashboard data/document requirements + Modo benchmark probe finding.

Generated from the tinte-data-requirements-and-modo workflow (9 agents, 2026-06-24).
For each of the 35 Solar KPIs: the data feeds + source documents needed for full
coverage, the provider, cadence, and current Tinte status (have/partial/missing).
"""

SOLAR_DATA_REQUIREMENTS = [{'category': 'Revenue & Profitability',
  'kpis': [{'id': 'revenue-vs-budget',
            'name': 'Revenue vs. Budget',
            'required_data': ['15-min metered export (MWh) per settlement period from the grid main-meter (HAVE in '
                              'feed)',
                              'Realised sale price per MWh: signed PPA strike/fixed price (EUR/MWh) and/or EPEX NL '
                              'day-ahead hourly clearing price (EUR/MWh) for any merchant/floating volume',
                              'Imbalance volumes and TenneT imbalance settlement prices (EUR/MWh, per ISP) for the '
                              'unhedged/balancing-responsible portion',
                              'GvO (Garantie van Oorsprong) certificate volume issued and unit sale price (EUR/GvO = '
                              'EUR/MWh)',
                              'SDE++ subsidy correction-amount entitlement (EUR/MWh) and base-vs-correction price '
                              'true-up for the period',
                              'Budgeted monthly revenue line from the project-finance / business plan model (EUR), '
                              'and budgeted price + budgeted generation underlying it',
                              'Curtailment compensation / constraint payments, if any, for the 122 curtailment '
                              'intervals already captured technically'],
            'source_documents': ['SCADA/PPC historian + grid main-meter (export MWh) — already in data/tinte feed',
                                 'Signed PPA / offtake agreement (price, indexation, tenor, settled volume '
                                 'definition)',
                                 'Monthly revenue / settlement statements from the offtaker / route-to-market trader',
                                 'TenneT imbalance settlement statements (eMFRR/imbalance price per ISP)',
                                 'GvO issuance records (CertiQ / Vertogas) + GvO sale invoices',
                                 'SDE++ award letter + RVO subsidy correction-price publications',
                                 "Project-finance model / annual budget (the 'Budgeted' baseline used in the monthly "
                                 'Technical Performance Report)'],
            'provider': 'Asset manager (budget) + offtaker/trader (price & settlement) + market-data vendor (EPEX '
                        'NL) + TSO TenneT (imbalance) + RVO/CertiQ (SDE++/GvO)',
            'cadence': 'monthly (settlement statements & budget comparison); daily/hourly underlying price & meter '
                       'data',
            'tinte_status': 'partial'},
           {'id': 'ebitda-margin',
            'name': 'EBITDA Margin',
            'required_data': ['Total revenue for the period (energy + PPA + imbalance + GvO + SDE++ + any '
                              'capacity/ancillary) — the Revenue-vs-Budget stack',
                              'Operating costs: O&M fixed fee + variable/availability-linked O&M, asset management '
                              'fee, insurance premium, land lease / grond rent, DSO/TSO grid & network charges, '
                              'ODE/energy taxes, metering & balancing-service fees, SPV admin/audit/bank costs',
                              'Period split so margin = (Revenue - OpEx) / Revenue is computed monthly and YTD'],
            'source_documents': ['Monthly management accounts / trial balance for the SPV (P&L above the EBITDA '
                                 'line)',
                                 'O&M contract + CMMS work-order log (fixed + variable fee, availability deductions)',
                                 'Asset management agreement, insurance schedule, land lease agreement',
                                 'Network/DSO invoices (grid connection & transport tariffs), tax/ODE assessments',
                                 'Revenue / settlement statements (from the Revenue-vs-Budget KPI)'],
            'provider': 'Accounting/finance team (management accounts) + EPC/O&M contractor (O&M cost) + asset '
                        'manager (fees, lease, insurance) + DSO/TSO (network charges)',
            'cadence': 'monthly (management accounts); annual (audited true-up)',
            'tinte_status': 'missing'},
           {'id': 'net-profit-after-tax',
            'name': 'Net Profit After Tax (PAT)',
            'required_data': ['EBITDA (revenue minus all OpEx) for the period',
                              'Depreciation & amortisation schedule for the solar plant assets (book D&A per period)',
                              'Senior debt interest expense and amortisation schedule; shareholder-loan (SHL) '
                              'interest',
                              'Other financing items: commitment/agency fees, hedge/MtM accruals, FX where '
                              'applicable',
                              'Dutch corporate income tax computation: 25.8% vennootschapsbelasting (with the lower '
                              'bracket on first EUR 200k), EIA/energy-investment-allowance, fiscal depreciation, '
                              'loss carry-forward (NOL) pool, interest-deduction limitation (earnings-stripping / '
                              'EBITDA cap)'],
            'source_documents': ['Audited management accounts / statutory P&L for the SPV (down to PAT)',
                                 'Project-finance model + senior facility agreement (debt amortisation & interest '
                                 'schedule)',
                                 'Shareholder loan agreement (SHL interest accrual)',
                                 'Fixed-asset register / depreciation policy',
                                 'Corporate tax computation / tax provision workpapers (Dutch CIT)'],
            'provider': 'Accounting/finance team (P&L, tax) + lender/agent bank (debt schedule confirmation) + asset '
                        'manager (model)',
            'cadence': 'monthly (management P&L estimate); quarterly/annual (tax provision & audited PAT)',
            'tinte_status': 'missing'},
           {'id': 'equity-irr',
            'name': 'Equity IRR (Project Lifetime)',
            'required_data': ['Equity investment cash outflows (timing & amount of equity contributions, including '
                              'any SHL drawn as quasi-equity)',
                              'Full-lifetime (51-year horizon-style) projected distributable cash flows to equity: '
                              'post-debt-service CFADS, dividends, SHL interest+repayment, terminal/residual value',
                              'Senior debt sizing, amortisation, DSCR/cash-sweep mechanics and gearing (drives '
                              'distributable equity cash)',
                              'Long-run revenue forecast inputs: contracted PPA volume/price/tenor + merchant price '
                              'curve (Baringa/Aurora-type forward curve, EUR/MWh) for post-PPA years, SDE++ tenor & '
                              'correction prices, GvO price curve, P50 generation profile and degradation',
                              'Long-run OpEx, tax, inflation/CPI and discount assumptions',
                              'Actuals-to-date vs original-underwrite to compute a refreshed lifetime IRR '
                              '(re-forecast)'],
            'source_documents': ['Project-finance model (the equity IRR engine) + senior facility agreement',
                                 'Signed PPA / offtake agreement (contracted price/volume/tenor)',
                                 'P50 yield/energy assessment report (lifetime generation + degradation)',
                                 'Merchant price-curve subscription / report (Baringa, Aurora, or equivalent NL '
                                 'forward curve)',
                                 'SDE++ award letter (subsidy tenor & cap) + RVO correction-price methodology',
                                 'Equity cash-flow / distribution ledger and shareholder agreement'],
            'provider': 'Asset manager / investment team (model & equity cash flows) + market-data vendor (long-run '
                        'price curve) + lender/agent bank (debt terms) + independent engineer (P50)',
            'cadence': 'quarterly re-forecast; annual full revaluation (underlying model)',
            'tinte_status': 'missing'},
           {'id': 'revenue-waterfall',
            'name': 'Monthly Revenue Waterfall (MTD)',
            'required_data': ['Gross theoretical/budget revenue starting point (budgeted generation x budgeted '
                              'price, EUR)',
                              'Volume variance bridge: actual vs budget MWh priced at realised/budget price (the '
                              'energy waterfall in MWh is HAVE — needs a EUR price applied to each loss bucket: '
                              'temperature, array, inverter, AC, plant breakdown, grid+curtailment)',
                              'Price variance bridge: realised capture price vs budget price (EPEX NL day-ahead + '
                              'imbalance + PPA settlement, EUR/MWh)',
                              'Revenue components stacked to net: wholesale/PPA energy revenue, imbalance +/-, GvO '
                              'revenue, SDE++ subsidy top-up, curtailment compensation, minus the 5%-type '
                              'route-to-market / trading fee and balancing costs',
                              'Month-to-date cumulative aggregation aligned to the settlement calendar'],
            'source_documents': ['Monthly revenue / settlement statements from the offtaker / trader (component '
                                 'breakdown)',
                                 'EPEX NL day-ahead price series + TenneT imbalance prices (market-data '
                                 'subscription)',
                                 'GvO sale invoices + SDE++ correction statements',
                                 'Project-finance model / budget (budgeted revenue & price baseline)',
                                 'SCADA/PPC historian energy-loss waterfall (the MWh waterfall already in the Tinte '
                                 'report)'],
            'provider': 'Offtaker/trader (settlement breakdown) + market-data vendor (EPEX/imbalance) + asset '
                        'manager (budget) + RVO/CertiQ (SDE++/GvO)',
            'cadence': 'monthly (with daily intra-month accrual from price + meter data)',
            'tinte_status': 'partial'},
           {'id': 'net-book-value',
            'name': 'Net Book Value & Asset Valuation',
            'required_data': ['Gross asset cost / capitalised CapEx for the plant (EPC + development + grid '
                              'connection + capitalised financing)',
                              'Accumulated depreciation to date and book depreciation schedule (NBV = gross cost - '
                              'accumulated depreciation)',
                              'Any impairment charges / revaluations',
                              'DCF valuation inputs for fair/market value: lifetime distributable cash flows, WACC / '
                              'discount rate, merchant price curve, terminal value, plus latest comparable '
                              'transaction multiples (EUR/MWp) for a market cross-check'],
            'source_documents': ['Fixed-asset register + audited balance sheet (NBV / carrying value)',
                                 'Project-finance / valuation model (DCF, discount rate, terminal value)',
                                 "Independent valuation report or lender's model audit (fair value)",
                                 'Merchant price-curve subscription (Baringa/Aurora) for the DCF revenue stack',
                                 'Market transaction-comparable data (EUR/MWp benchmarks)'],
            'provider': 'Accounting/finance team (NBV, fixed-asset register) + asset manager / investment team (DCF '
                        'valuation) + independent valuer + market-data vendor (price curve & comps)',
            'cadence': 'quarterly (NBV roll-forward); annual (audited NBV + full revaluation)',
            'tinte_status': 'missing'},
           {'id': 'fy-reforecast',
            'name': 'Full-Year Reforecast vs. Budget',
            'required_data': ['Actuals YTD: actual generation MWh (HAVE), actual realised revenue, actual OpEx YTD',
                              'Original full-year budget: budgeted generation (1,410 MWh/month baseline is in the '
                              'report), budgeted price, budgeted revenue, budgeted OpEx, budgeted EBITDA/PAT',
                              'Remaining-months forecast: P50 expected generation for the rest of FY (seasonal '
                              'profile), forward EPEX NL price curve + PPA contracted price for unsold volume, '
                              'SDE++/GvO expected income, expected OpEx',
                              'Weather-normalisation inputs (actual vs budget irradiation — HAVE: 161 vs 143 kWh/m2 '
                              'for April) to attribute variance to resource vs performance',
                              'Reforecast roll-up to full-year revenue, EBITDA and PAT vs budget with variance '
                              'bridge'],
            'source_documents': ['Project-finance model / annual budget (the budget baseline & FY targets)',
                                 'Monthly Technical Performance Report (actual vs budget generation & irradiation — '
                                 'already in feed)',
                                 'Monthly revenue / settlement statements (actual revenue YTD)',
                                 'Management accounts (actual OpEx YTD)',
                                 'P50 yield/energy assessment report (remaining-year generation profile)',
                                 'Forward price-curve subscription (EPEX NL + Baringa/Aurora) for unsold/merchant '
                                 'volume'],
            'provider': 'Asset manager / finance team (reforecast & budget) + offtaker/trader (realised revenue) + '
                        'market-data vendor (forward curve) + independent engineer (P50 profile)',
            'cadence': 'monthly or quarterly reforecast vs annual budget',
            'tinte_status': 'partial'}]},
 {'category': 'Cash & Distributions',
  'kpis': [{'id': 'cfads',
            'name': 'CFADS (Cash Flow Available for Debt Service)',
            'required_data': ['Operating revenue build-up: half-hourly/15-min metered export (MWh) by settlement '
                              'period [HAVE via main-meter] valued at the realised price stack',
                              'EPEX NL day-ahead hourly price (EUR/MWh) and/or contracted PPA price (EUR/MWh) '
                              'applied to exported volume',
                              'Signed PPA / offtake volume, price, escalation and tenor (and any merchant/balancing '
                              'split) for revenue split CfD/PPA vs merchant',
                              'GvO/Guarantees of Origin issued volume and unit price (EUR/GoO) and SDE++ subsidy '
                              'entitlement (EUR/MWh, base-price correction, cap hours)',
                              'Imbalance/balancing settlement (EUR) — TenneT imbalance volumes and prices for the '
                              'unbalanced position',
                              'Actual cash operating costs (OpEx): O&M fixed + variable fee, asset-management fee, '
                              'insurance, land lease/rent, grid connection & DSO/TSO transport tariffs, metering, '
                              'security, local property tax',
                              'Cash taxes paid (Dutch corporate income tax) and irrecoverable VAT timing',
                              'Movements in working capital (receivables/payables) over the period',
                              'Curtailment-driven lost revenue / compensation entries (PPC setpoint <100% periods) '
                              '[setpoint signal HAVE; EUR value MISSING]'],
            'source_documents': ['Monthly revenue/settlement statements from the offtaker/trader (energy + GoO + '
                                 'imbalance)',
                                 'TenneT imbalance settlement statements / DSO export-metering settlement',
                                 'SDE++ subsidy advance & annual reconciliation statements (RVO)',
                                 'Signed PPA / offtake agreement',
                                 'O&M contract + asset-management agreement + insurance & land-lease contracts (cost '
                                 'schedules)',
                                 'Monthly management accounts / general ledger (actual OpEx, tax, working capital)',
                                 'Project-finance model (CFADS build template)',
                                 'SCADA/PPC historian + grid main-meter (export MWh)',
                                 'Wholesale market-data subscription (EPEX NL day-ahead, imbalance prices)'],
            'provider': 'Offtaker/trader (revenue, GoO, imbalance) + asset manager & accounting/finance team (OpEx, '
                        'tax, WC) + EPC/O&M contractor (cost actuals) + market-data vendor (EPEX/TenneT prices) + '
                        'SCADA/PPC historian (export volume)',
            'cadence': 'monthly (settlement + management accounts); price feeds daily; SDE++ reconciliation annual',
            'tinte_status': 'partial'},
           {'id': 'liquidity-reserves',
            'name': 'Liquidity & Reserve Accounts',
            'required_data': ['Reserve account target/required balances and actual closing balances: DSRA (Debt '
                              'Service Reserve Account, typically 6 months forward debt service), MMRA/Maintenance '
                              'Reserve, and any Decommissioning/Inverter-replacement reserve',
                              'Operating/distribution/proceeds account closing cash balances (bank statements)',
                              'Reserve funding requirements and release/top-up mechanics defined in the facility '
                              '(target sizing formulae, lock-up triggers)',
                              'Cash-trap / lock-up status driven by DSCR vs covenant (e.g. < 1.10x lock-up) — '
                              'requires period DSCR',
                              'Letters of credit / guarantees standing in lieu of cash reserves (face value, expiry)',
                              'Forward debt service schedule (next 6 months principal + interest) to size DSRA '
                              'target',
                              'Inflows/outflows and interest earned on reserve balances over the period'],
            'source_documents': ['Senior facility agreement + accounts agreement (defines each reserve, target '
                                 'sizing, waterfall, lock-up triggers)',
                                 'Monthly/quarterly bank account statements for each project account (operating, '
                                 'DSRA, MMRA, distribution)',
                                 'Agent bank / security-trustee reserve account confirmations and reconciliation',
                                 'Project-finance model (debt service & reserve target schedules)',
                                 'Compliance certificate (covenant/DSCR + reserve confirmation)'],
            'provider': 'Lender / agent bank / security trustee (account confirmations) + accounting/finance team '
                        '(bank reconciliations) + asset manager (compliance certificate)',
            'cadence': 'monthly (bank balances) / quarterly or semi-annual (covenant & reserve confirmation around '
                       'debt service dates)',
            'tinte_status': 'missing'},
           {'id': 'distributions-equity',
            'name': 'Distributions to Equity (FCFE)',
            'required_data': ['CFADS for the period (see cfads KPI) as the starting point',
                              'Senior debt service paid: scheduled principal amortisation + cash interest + fees '
                              '(senior debt amortisation schedule)',
                              'Shareholder loan (SHL) interest and principal repayments (intercompany loan schedule)',
                              'Net reserve account movements (funding consumes cash; releases free cash) — DSRA/MMRA '
                              'top-ups & releases',
                              'Cash sweep amount applied (if mandatory-prepayment/sweep mechanism active)',
                              'Distribution lock-up / covenant test result for the distribution date (DSCR ≥ '
                              'threshold, reserves fully funded, no default) — distribution conditions',
                              'Actual dividends / capital returns / SHL repayments paid to equity (distribution '
                              'waterfall outturn)',
                              'Equity contribution / drawdown timing (for FCFE and equity IRR roll-forward)'],
            'source_documents': ['Project-finance model + senior facility agreement (debt amortisation, sweep, '
                                 'distribution conditions & waterfall)',
                                 'Shareholder loan agreement (SHL interest/repayment schedule)',
                                 'Accounts agreement (distribution lock-up tests, waterfall priority)',
                                 'Compliance / distribution certificate (DSCR test, lock-up clearance for the '
                                 'distribution date)',
                                 'Board minutes / dividend resolutions + distribution account bank statements',
                                 'Audited / management accounts (declared and paid distributions)'],
            'provider': 'Lender / agent bank (distribution clearance & waterfall) + accounting/finance team & asset '
                        'manager (declared/paid distributions, SHL movements) + equity sponsor/SPV board (dividend '
                        'resolutions)',
            'cadence': 'quarterly or semi-annual (aligned to debt service / distribution dates)',
            'tinte_status': 'missing'}]},
 {'category': 'Debt & Covenants',
  'kpis': [{'id': 'dscr',
            'name': 'DSCR (Debt Service Coverage Ratio)',
            'required_data': ['Cash Flow Available for Debt Service (CFADS) for the calculation period = operating '
                              'revenue minus cash opex minus cash taxes, adjusted for reserve movements',
                              'Gross operating revenue components: half-hourly/15-min metered export volume (MWh) '
                              'priced at the realised offtake — EPEX NL day-ahead capture, PPA/CfD settled price, '
                              'and any GvO/SDE++ subsidy top-up',
                              'TenneT imbalance settlement amount (EUR, positive or negative) for the period',
                              'Cash operating costs actually paid: O&M fee, asset-management fee, land lease/grond '
                              'rent, insurance, DSO/TSO grid connection and transport charges, '
                              'balancing-responsible-party (BRP) and trading fees, local taxes (OZB/WOZ)',
                              'Cash taxes paid (Vpb corporate income tax) for the period',
                              'Scheduled debt service for the period: senior principal repayment + senior cash '
                              "interest paid (per the amortisation schedule and the period's drawn balance × "
                              'applicable rate)',
                              'Movements in/out of the Debt Service Reserve Account (DSRA) and maintenance reserve, '
                              'if included in the covenant CFADS definition',
                              'Reporting-period definition and lock-up/default DSCR covenant thresholds (e.g. 1.10x '
                              'lock-up / 1.05x default) from the facility agreement'],
            'source_documents': ['monthly revenue/settlement statements from the offtaker/trader (PPA invoices, EPEX '
                                 'NL settlement, TenneT imbalance settlement)',
                                 'SDE++/GvO subsidy statements (RVO / CertiQ)',
                                 'O&M contract + CMMS work-order log and monthly opex/asset-management ledger',
                                 'project-finance model + senior facility (loan/common-terms) agreement — CFADS '
                                 'definition, debt service schedule, covenant ratios',
                                 "lender's quarterly compliance/covenant certificate and bank account statements "
                                 '(DSRA balances)',
                                 'audited/management accounts (cash taxes, accruals)',
                                 'wholesale market-data subscription (EPEX NL day-ahead) to value/verify capture'],
            'provider': 'asset manager (compiles CFADS); offtaker/trader and TenneT (revenue & imbalance); EPC/O&M '
                        'contractor (opex); accounting/finance team (taxes, accounts); lender/agent bank (debt '
                        'service schedule, DSRA, covenant levels); market-data vendor (EPEX NL prices)',
            'cadence': 'Quarterly (covenant test/certificate), with monthly revenue, settlement and opex inputs '
                       'feeding it',
            'tinte_status': 'partial'},
           {'id': 'llcr',
            'name': 'LLCR / PLCR',
            'required_data': ['Forward CFADS projection — period-by-period to loan maturity (LLCR) and to project '
                              'end-of-life (PLCR) — built from the P50 energy forecast, contracted/merchant price '
                              'curve and projected cash opex/taxes',
                              'P50 (and P90) annual energy yield with degradation profile, to drive forward '
                              'generation volume (MWh)',
                              'Forward price assumptions: contracted PPA/CfD price + tenor, merchant EPEX NL forward '
                              'curve for the uncontracted tail, SDE++/GvO subsidy schedule and remaining tenor',
                              'Discount rate for the NPV of CFADS (typically the senior all-in cost of debt / loan '
                              'margin + swap rate)',
                              'Outstanding senior debt balance at the test date (and the projected balance for the '
                              'PLCR project tail)',
                              'Remaining loan tenor / final maturity date (LLCR window) and project operating-life '
                              'end date (PLCR window)',
                              "Balance of any reserve accounts (DSRA/MRA) added to the NPV per the facility's LLCR "
                              'definition',
                              'Minimum LLCR/PLCR covenant thresholds from the facility agreement'],
            'source_documents': ['P50 yield / energy assessment report (independent engineer)',
                                 'project-finance model (forward CFADS, base-case banking case) + senior facility '
                                 'agreement (LLCR/PLCR definition and thresholds)',
                                 'signed PPA / offtake agreement (contracted price, volume, tenor) and SDE++/GvO '
                                 'subsidy decision letters',
                                 'wholesale market-data subscription (EPEX NL forward/futures curve for the merchant '
                                 'tail)',
                                 'lender/agent-bank statements (outstanding debt balance, reserve balances) and the '
                                 'quarterly covenant certificate',
                                 'management accounts / opex budget for forward cost assumptions'],
            'provider': 'asset manager / financial modeller (forward CFADS, NPV); independent engineer (P50 yield); '
                        'offtaker/trader (contract terms); market-data vendor (forward curve); lender/agent bank '
                        '(debt balance, reserves, thresholds)',
            'cadence': 'Quarterly (recomputed at each covenant test; forward curve and reforecast updated '
                       'periodically)',
            'tinte_status': 'partial'},
           {'id': 'gearing-amortization',
            'name': 'Gearing & Debt Amortization',
            'required_data': ['Outstanding senior debt balance at the reporting date (drawn principal)',
                              'Original facility size / total debt drawn at financial close and the sculpted/annuity '
                              'senior amortisation schedule (principal repayment per period to maturity)',
                              'Total project capital structure: equity contributed + shareholder loans + any '
                              'junior/mezzanine debt (to compute gearing / debt-to-total-capitalisation and '
                              'debt-to-equity)',
                              'Net book value / total assets or enterprise value for the gearing denominator (Net '
                              'Debt / (Net Debt + Equity), or Net Debt / EBITDA)',
                              'Cash and cash equivalents (for net-debt) and reserve-account balances',
                              'EBITDA for the trailing period if Net-Debt/EBITDA leverage is tracked',
                              'Repayment/prepayment and cash-sweep history (actual principal repaid vs scheduled)'],
            'source_documents': ['project-finance model + senior facility agreement (drawdown amount, '
                                 'amortisation/sculpting schedule, cash-sweep terms)',
                                 'lender/agent-bank loan statements and the quarterly compliance certificate '
                                 '(outstanding balance, scheduled vs actual repayments)',
                                 'audited / management accounts and the equity & shareholder-loan funding records '
                                 '(capital structure)',
                                 'treasury/finance ledger (cash balances, reserve accounts)'],
            'provider': 'lender/agent bank (debt balance & amortisation schedule); accounting/finance team (equity, '
                        'NBV, cash, EBITDA); asset manager / financial modeller (capital structure and gearing '
                        'computation)',
            'cadence': 'Quarterly (debt balance and gearing at each reporting/test date; amortisation schedule is '
                       'fixed at close)',
            'tinte_status': 'missing'},
           {'id': 'cost-of-debt',
            'name': 'Cost of Debt & Hedge Status',
            'required_data': ['Senior debt margin/spread (bps over reference rate) and the reference rate basis '
                              '(e.g. EURIBOR / SONIA-equivalent) per the facility agreement',
                              'Interest-rate hedge details: notional schedule of the interest-rate swap(s)/cap, '
                              'fixed swap rate, hedge start/maturity dates, and the percentage of debt hedged vs '
                              'floating',
                              'Current floating reference-rate fixings to compute the blended all-in interest cost '
                              'on the unhedged portion',
                              'Period interest expense actually accrued/paid and the average drawn balance, to '
                              'derive the realised effective/weighted-average cost of debt',
                              'Mark-to-market (MtM) valuation of the hedge instruments and any hedge-ratio covenant '
                              '(minimum % of debt that must be hedged)',
                              'Commitment/agency/other facility fees that feed the all-in cost',
                              'Hedge counterparty and credit-support/CSA terms'],
            'source_documents': ['senior facility agreement + hedging agreement (ISDA/schedule, confirmations) — '
                                 'margin, reference rate, swap notional/rate, hedge-ratio covenant',
                                 'project-finance model (all-in cost-of-debt build-up)',
                                 'lender/agent-bank and hedge-counterparty statements (interest charged, swap '
                                 'settlements, MtM valuations)',
                                 'treasury reference-rate data / market-data subscription (EURIBOR fixings, swap '
                                 'curve)',
                                 'management accounts (interest expense, fees accrued/paid)'],
            'provider': 'lender/agent bank and hedge counterparty (interest charged, swap rate, MtM); asset manager '
                        '/ treasury (hedge schedule, blended cost computation); accounting/finance team (interest '
                        'expense, fees); market-data vendor (reference-rate/swap-curve fixings)',
            'cadence': 'Quarterly (effective cost and hedge status reported each period; MtM and floating fixings '
                       'move daily/monthly)',
            'tinte_status': 'missing'}]},
 {'category': 'Revenue Contracting',
  'kpis': [{'id': 'contracted-revenue-horizon',
            'name': 'Contracted Revenue Horizon',
            'required_data': ['Signed PPA / offtake contract terms: contracted volume (MWh/yr or % of generation), '
                              'price (EUR/MWh, fixed or indexed), tenor (start/end dates), escalation/indexation '
                              'clauses',
                              'Contract structure split: fixed-price hedge volume vs floating/merchant exposure, '
                              'baseload vs pay-as-produced shape',
                              'Volume-firming / floor and cap terms (collar, minimum offtake)',
                              'Forward contract / hedge book covering the asset (any GoO/PPA forward sales already '
                              'transacted) with their expiry dates',
                              'Weighted-average remaining contract life and % of forward P50 generation that is '
                              'contracted vs uncontracted, by year out to end of PPA tenor',
                              "P50 (and P90) annual energy yield projection to anchor 'contracted % of expected "
                              "generation'"],
            'source_documents': ['Signed PPA / offtake agreement (corporate or utility PPA)',
                                 'Route-to-market / aggregator offtake agreement and any forward GoO sale '
                                 'confirmations',
                                 'Project-finance model (base-case revenue assumptions, contracted vs merchant '
                                 'split)',
                                 'P50 yield / energy assessment report (independent technical advisor)',
                                 'Hedge book / trading desk position report'],
            'provider': 'Asset manager / commercial team (contract terms); offtaker / trader (forward positions); '
                        "lender's model & independent engineer (P50 yield)",
            'cadence': 'Quarterly (re-stated when contracts are signed, amended, or hedges transacted)',
            'tinte_status': 'missing'},
           {'id': 'revenue-mix',
            'name': 'Revenue Mix by Channel',
            'required_data': ['Channel definitions for an NL solar asset: PPA/contracted energy, merchant wholesale '
                              '(EPEX NL day-ahead + intraday), imbalance (TenneT-settled), and subsidy/certificate '
                              'revenue (SDE++ feed-premium + GvO/GoO sales)',
                              'Metered export volume allocated to each channel (MWh): PPA-delivered MWh vs '
                              'merchant-sold MWh vs imbalance volume',
                              'Achieved/captured price per channel (EUR/MWh): PPA contract price, volume-weighted '
                              'EPEX NL day-ahead capture price, intraday capture price, imbalance settlement price',
                              "EUR revenue per channel and each channel's % share of total period revenue",
                              'GvO/GoO certificate quantities issued and sale price (EUR/certificate)',
                              'SDE++ subsidy entitlement and correction-amount (basisbedrag minus correctiebedrag) '
                              'per MWh'],
            'source_documents': ['Monthly revenue / settlement statements from offtaker or route-to-market '
                                 'aggregator (channel breakdown)',
                                 'Signed PPA / offtake agreement (contracted price & volume)',
                                 'EPEX NL day-ahead and intraday market-data subscription (achieved-price '
                                 'benchmarking)',
                                 'TenneT imbalance settlement statements / eMFRR-aFRR pricing data',
                                 'CertiQ GvO/GoO register statements + GoO trade confirmations',
                                 'RVO SDE++ award letter and subsidy correction-amount publications'],
            'provider': 'Offtaker / trader / aggregator (channel revenues & volumes); market-data vendor (EPEX '
                        'prices); TSO TenneT (imbalance); CertiQ / RVO (certificates & subsidy)',
            'cadence': 'Monthly (settlement statements); daily (market prices)',
            'tinte_status': 'partial'},
           {'id': 'ppa-delivery-accuracy',
            'name': 'PPA Delivery Accuracy',
            'required_data': ['Contracted/nominated delivery profile under the PPA (MWh per settlement period, or '
                              'the agreed pay-as-produced shape and any baseload nomination)',
                              'Actual half-hourly / 15-min metered export delivered to the PPA channel (MWh) — the '
                              'volume actually settled against the contract',
                              'Forecast vs actual generation per settlement period (where the PPA imposes a '
                              'forecasting/nomination obligation) to compute forecast error and deviation %',
                              'Curtailment / PPC setpoint log to attribute under-delivery to grid/curtailment vs '
                              'plant availability vs forecast error',
                              'Imbalance volumes and TenneT imbalance charges arising from delivery deviations (cost '
                              'of inaccuracy)',
                              'Any take-or-pay / firming penalties or shortfall charges defined in the PPA'],
            'source_documents': ['Signed PPA / offtake agreement (delivery/nomination obligations, penalty/firming '
                                 'clauses)',
                                 'SCADA / PPC historian (actual export + curtailment setpoint)',
                                 'Generation forecast vs actual reconciliation (from trader/aggregator forecasting '
                                 'service)',
                                 'TenneT imbalance settlement statements',
                                 'Monthly settlement statements from offtaker (delivered volume vs contracted, '
                                 'penalties applied)'],
            'provider': 'Offtaker / route-to-market trader (contracted profile, forecasts, penalties); asset manager '
                        '+ SCADA/PPC historian (actual delivery & curtailment); TSO TenneT (imbalance)',
            'cadence': 'Daily (delivery vs forecast); monthly (settlement reconciliation & penalties)',
            'tinte_status': 'partial'},
           {'id': 'realized-revenue-channel',
            'name': 'Realized Revenue by Channel',
            'required_data': ['Settled EUR revenue per channel for the period: PPA-delivered revenue, merchant '
                              'day-ahead revenue, intraday revenue, imbalance settlement (credit/charge from '
                              'TenneT), SDE++ subsidy accrual, GvO/GoO certificate sales',
                              "Settled volume (MWh) and achieved price (EUR/MWh) underlying each channel's revenue",
                              'Less-than-gross adjustments: route-to-market / aggregator fees, balancing/imbalance '
                              'costs, trading fee or revenue-share %, grid feed-in/connection charges',
                              'Net realized revenue and realized capture rate vs EPEX NL day-ahead baseline '
                              '(achieved EUR/MWh ÷ time-weighted market price)',
                              'Reconciliation of settled revenue to metered export volume (EUR/MWh implied vs '
                              'metered MWh)'],
            'source_documents': ['Monthly revenue / settlement statements from offtaker, trader and aggregator '
                                 '(per-channel settled amounts & fees)',
                                 'TenneT imbalance settlement statements',
                                 'CertiQ GvO register + GoO sale invoices; RVO SDE++ payment/advance statements',
                                 'Audited management accounts / SPV ledger (revenue recognition true-up)',
                                 'EPEX NL day-ahead market data (capture-rate benchmark)'],
            'provider': 'Offtaker / trader / aggregator (settlement statements); accounting / finance team '
                        '(management accounts); TSO TenneT (imbalance); CertiQ & RVO (certificates & subsidy); '
                        'market-data vendor (benchmark price)',
            'cadence': 'Monthly (settlement & accounting close); quarterly (audited true-up)',
            'tinte_status': 'missing'},
           {'id': 'subsidy-certificate-revenue',
            'name': 'Subsidy & Certificate Revenue',
            'required_data': ['SDE++ award parameters: granted subsidy intensity / base amount (basisbedrag, '
                              'EUR/kWh), subsidised production cap (max kWh/yr), correction amount (correctiebedrag) '
                              'per applicable period, remaining subsidy years/budget',
                              'Eligible subsidised generation (MWh) for the period and cumulative against the SDE++ '
                              'cap/ceiling',
                              'Computed SDE++ feed-premium = (basisbedrag − correctiebedrag) × eligible MWh, plus '
                              'advance vs final-settlement reconciliation',
                              'GvO/GoO (Guarantees of Origin) issued volume (number of certificates, 1 per MWh) from '
                              'CertiQ and sale price (EUR/GoO)',
                              'GoO sale revenue and any unsold/banked certificate inventory',
                              'Reference electricity price used by RVO for the correction amount (to validate the '
                              'EUR/MWh top-up)'],
            'source_documents': ['RVO SDE++ award letter / beschikking (base amount, cap, tenor) and published '
                                 'correction-amount (correctiebedrag) tables',
                                 'RVO SDE++ advance-payment and annual settlement statements',
                                 'CertiQ Guarantees-of-Origin register statements (issued GoO volume)',
                                 'GoO trade confirmations / sale invoices (certificate price)',
                                 'SCADA / metered export (eligible MWh basis)'],
            'provider': 'RVO (SDE++ subsidy & correction amounts); CertiQ (GoO issuance); offtaker / certificate '
                        'trader (GoO sale price); asset manager / finance team (reconciliation)',
            'cadence': 'Monthly (production accrual); quarterly/annual (RVO settlement & correction-amount '
                       'finalisation)',
            'tinte_status': 'missing'}]},
 {'category': 'Market & Trading',
  'kpis': [{'id': 'portfolio-capture-rate',
            'name': 'Portfolio Capture Rate',
            'required_data': ['Metered net export volume per settlement period, aggregated to the period '
                              '(PTU/hourly) — already in the Tinte 15-min grid main-meter (kWh), resampled to MWh',
                              'Realized price actually received per MWh by channel (EPEX NL day-ahead clearing price '
                              'for merchant volume, plus any PPA/fixed price and SDE++/GvO uplift) to build the '
                              'volume-weighted realized price (the numerator)',
                              'EPEX NL (TenneT bidding zone) day-ahead hourly baseload price (EUR/MWh) — simple time '
                              'average over the period = the baseload denominator',
                              'Generation-weighted vs time-weighted reconciliation: the same metered-volume series '
                              'used as the weights so cannibalisation (solar mid-day price dip) is captured',
                              'Revenue-channel split (merchant / PPA / subsidy) so the realized price reflects the '
                              'true blended price, not just spot',
                              'Period/zone definition (month, EUR, Netherlands NL bidding zone) to align numerator '
                              'and denominator currencies and timestamps (CET/CEST)'],
            'source_documents': ['SCADA/PPC historian + 15-min grid main-meter (metered export — already in Tinte '
                                 'feed)',
                                 'EPEX NL day-ahead market-data subscription (or ENTSO-E Transparency Platform NL '
                                 'day-ahead prices)',
                                 'Monthly revenue/settlement statements from the offtaker/trader (realized price & '
                                 'volume by channel)',
                                 'Signed PPA / offtake agreement (contracted price/volume for the PPA-hedged share)',
                                 'SDE++ subsidy decision letter + GvO/Guarantee-of-Origin sales statements '
                                 '(subsidy/certificate uplift)'],
            'provider': 'Asset manager (volume from SCADA/meter); offtaker/trader (realized price & settlement); '
                        'market-data vendor / EPEX / ENTSO-E (baseload reference price); RVO (SDE++) and GvO '
                        'registry / certificate trader (subsidy & certificate revenue)',
            'cadence': 'Monthly',
            'tinte_status': 'partial'},
           {'id': 'capture-price',
            'name': 'Daily Capture Price',
            'required_data': ['Metered net export volume per settlement period (15-min PTU → MWh) for the day — '
                              'present in the Tinte grid main-meter feed',
                              'EPEX NL day-ahead hourly spot price (EUR/MWh), time-aligned to each generation '
                              'interval, to compute Σ(Generationₜ × Spotₜ) / Σ Generationₜ',
                              'EPEX NL day-ahead daily baseload average (EUR/MWh) as the comparison benchmark, to '
                              'derive the profile/capture discount (EUR/MWh)',
                              'Consistent interval mapping between the 15-min meter (PTU) and the hourly EPEX price '
                              '(price held flat across the 4 PTUs in each hour), in local CET/CEST time',
                              'If volume is sold partly under PPA at a fixed price, the per-channel price so the '
                              "'realized' capture price can be shown vs the pure spot-weighted capture price"],
            'source_documents': ['SCADA/PPC historian + 15-min grid main-meter (interval export volume — already in '
                                 'Tinte feed)',
                                 'EPEX NL day-ahead market-data subscription (hourly prices) — or ENTSO-E '
                                 'Transparency Platform NL day-ahead',
                                 'Daily/monthly settlement statements from the offtaker/trader (to reconcile '
                                 'realized vs modelled spot capture)',
                                 'Signed PPA / offtake agreement (fixed-price share, if any)'],
            'provider': 'Asset manager (volume); market-data vendor / EPEX / ENTSO-E (day-ahead spot & baseload); '
                        'offtaker/trader (settlement reconciliation)',
            'cadence': 'Daily',
            'tinte_status': 'partial'},
           {'id': 'imbalance-cost',
            'name': 'Imbalance Cost per MWh',
            'required_data': ['Contracted/nominated (E-programme) position per imbalance settlement period (15-min '
                              'PTU) submitted to TenneT by the BRP/trader',
                              'Actual metered net export per 15-min PTU (the imbalance volume = metered − nominated) '
                              '— metered side is in the Tinte feed; the nomination side is not',
                              'TenneT imbalance settlement prices per PTU (onregelprijs — feed-in/afnemen prices, '
                              'regulation state, and the single/dual imbalance price) in EUR/MWh',
                              'Total imbalance settlement cost (EUR) for the period and total delivered MWh, to '
                              'compute Total Imbalance Settlement Costs / Total Delivered MWh',
                              'Sign convention for short vs long imbalance (paying System Buy vs receiving System '
                              'Sell equivalent under the Dutch dual/single pricing regime)',
                              'Forecast vs actual generation (the forecast that drove the nomination) to attribute '
                              'imbalance cost to forecast error'],
            'source_documents': ['Monthly imbalance settlement statements from the BRP / offtaker-trader '
                                 '(nominations + imbalance volumes + charges)',
                                 'TenneT imbalance settlement data (onbalansprijs / settlement prices per PTU) via '
                                 'the BRP or TenneT data platform',
                                 'SCADA/PPC historian + 15-min grid main-meter (actual metered export — already in '
                                 'Tinte feed)',
                                 'Signed offtake / route-to-market (BRP) agreement defining who carries imbalance '
                                 'and the pass-through terms',
                                 'Day-ahead nomination / E-programme records from the trader'],
            'provider': 'Offtaker/trader (Balance Responsible Party — nominations & imbalance charges); TSO TenneT '
                        '(imbalance settlement prices); asset manager (actual metered volume)',
            'cadence': 'Daily',
            'tinte_status': 'partial'},
           {'id': 'negative-price-exposure',
            'name': 'Negative Price Hour Exposure',
            'required_data': ['EPEX NL day-ahead hourly spot price (EUR/MWh) time series, to count settlement '
                              'periods where price < 0',
                              'Metered net export per interval (15-min PTU → MWh) during those negative-price '
                              'periods, to quantify MWh generated and EUR exposure (generation × negative price) — '
                              'present in the Tinte meter feed',
                              'Optionally intraday / imbalance prices to capture periods that go negative after the '
                              'day-ahead auction',
                              'PPC active-power setpoint / curtailment signal aligned to negative-price periods, to '
                              "distinguish 'curtailed away' from 'generated into a negative price' — the setpoint is "
                              'already in the Tinte SCADA feed',
                              'Subsidy interaction flag: SDE++ negative-price rule (subsidy suspended after a '
                              'defined run of consecutive negative-price hours) to value the true revenue impact of '
                              'each negative-price hour'],
            'source_documents': ['EPEX NL day-ahead market-data subscription (hourly prices) — or ENTSO-E '
                                 'Transparency Platform NL day-ahead (and intraday where used)',
                                 'SCADA/PPC historian + 15-min grid main-meter + PPC setpoint (generation & '
                                 'curtailment during negative-price hours — already in Tinte feed)',
                                 'SDE++ subsidy decision letter / RVO scheme rules (negative-price cessation '
                                 'conditions)',
                                 'Settlement statements from the offtaker/trader (to confirm realized negative '
                                 'revenue)'],
            'provider': 'Market-data vendor / EPEX / ENTSO-E (negative spot prices); asset manager (generation & '
                        'curtailment from SCADA/PPC); RVO (SDE++ negative-price rule); offtaker/trader (realized '
                        'settlement)',
            'cadence': 'Daily',
            'tinte_status': 'partial'}]},
 {'category': 'Generation & Availability',
  'kpis': [{'id': 'cumulative-yield-deviation',
            'name': 'Cumulative Yield Deviation from P50',
            'required_data': ['P50 energy-yield curve (monthly MWh and/or specific yield kWh/kWp) from the bankable '
                              'energy assessment, ideally with P90/P75/P10 bands',
                              'Actual cumulative metered export (MWh) from plant commissioning / financial-year '
                              'start to date — main-meter 15-min export kWh aggregated',
                              'Long-term-average (LTA / P50) plane-of-array irradiation (kWh/m2) per month to '
                              'weather-normalise the deviation',
                              'Actual POA irradiation (kWh/m2) per month from SCADA (have)',
                              'Plant nameplate (12.6 MWp DC / 9.8 MW AC) and commissioning date for cumulative '
                              'baseline anchoring'],
            'source_documents': ['P50 yield / energy assessment report (bankable resource assessment, e.g. from '
                                 'technical advisor / PVsyst study)',
                                 'SCADA/PPC historian (main-meter export + POA irradiance)',
                                 'Monthly Technical Performance Report (budget vs actual generation & irradiation)',
                                 'Project-finance base-case model (P50 generation profile used for budgeting)'],
            'provider': 'asset manager / technical advisor (P50 assessment); EPC/O&M contractor + asset manager '
                        '(SCADA metered export)',
            'cadence': 'monthly',
            'tinte_status': 'partial',
            'source_documents_present': 'Actual metered export and actual POA irradiance are in the feed; the '
                                        'P50/P90 yield-assessment curve and long-term-average irradiation are NOT — '
                                        "the dashboard currently substitutes the report's monthly budget (1,410 MWh) "
                                        'as a proxy. One month of data only, so no true cumulative baseline.'},
           {'id': 'epi-budget',
            'name': 'Budget EPI (BEPI)',
            'required_data': ['Actual generation (MWh) per period — main-meter 15-min export aggregated to '
                              'day/week/month (have)',
                              'Budgeted generation (MWh) per period from the financial-year budget, ideally at '
                              'daily/weekly granularity (only monthly 1,410 MWh available)',
                              'Budget basis / phasing curve (how the annual budget is spread across months/days to '
                              'compare at the required weekly cadence)'],
            'source_documents': ['Monthly Technical Performance Report (budget vs actual generation)',
                                 'Annual operating budget / business plan generation forecast',
                                 'SCADA/PPC historian (actual metered export)'],
            'provider': 'asset manager / finance team (budget); EPC/O&M contractor + asset manager (actual '
                        'generation)',
            'cadence': 'weekly',
            'tinte_status': 'have',
            'source_documents_present': 'Actual generation (1,343 MWh) and the monthly budget (1,410 MWh = 95.2%) '
                                        'are both present from the report and SCADA. Only gap is sub-monthly '
                                        '(weekly/daily) budget phasing — currently linearised — which is a '
                                        'granularity refinement, not a missing data source.'},
           {'id': 'epi',
            'name': 'Energy Performance Index (EPI)',
            'required_data': ['Actual generation (MWh) per day — main-meter 15-min export aggregated (have)',
                              'Weather-corrected MODEL-expected generation (MWh) per day — PVsyst (or equivalent) '
                              'simulation driven by the actual measured POA irradiance and module temperature for '
                              'the same period',
                              'Measured POA irradiance (W/m2) and module temperature (degC) at the modelling '
                              'interval (have)',
                              'As-built PVsyst model parameters (system losses, tilt/orientation, DC/AC ratio, '
                              'temperature coefficients) so expected yield can be recomputed against actual weather'],
            'source_documents': ['PVsyst / energy-model expected-yield report (weather-corrected design model)',
                                 'SCADA/PPC historian (actual export + POA irradiance + module temperature)',
                                 'Monthly Technical Performance Report (energy loss waterfall, theoretical max)'],
            'provider': 'asset manager / technical advisor (PVsyst expected-yield model); EPC/O&M contractor + asset '
                        'manager (SCADA actuals)',
            'cadence': 'daily',
            'tinte_status': 'partial',
            'source_documents_present': 'Actual daily generation plus measured POA irradiance and module temperature '
                                        'are present; the weather-corrected PVsyst expected-yield curve (the EPI '
                                        'denominator) is NOT in the feed. The report supplies a monthly '
                                        'theoretical-max (2,029 MWh) and a temperature-adjusted line, but not a '
                                        'per-day model-expected series, so the dashboard falls back to budget pace.'},
           {'id': 'availability',
            'name': 'System Availability',
            'required_data': ['Per-inverter operational status / fault flags time-series (online / tripped / '
                              'offline) at 1-min or 15-min resolution',
                              'Plant-level grid-connection availability (TSO/DSO outage windows, grid-loss events)',
                              'Curtailment / PPC-setpoint signal to exclude commanded down-time from availability '
                              'denominator (have — setpoint %)',
                              'Availability definition / guaranteed-availability formula from the O&M contract '
                              '(time-based vs energy-based, daylight-only, contractual exclusions)',
                              'O&M work-order / outage log (downtime cause, start/end timestamps, planned vs forced)',
                              'Per-inverter and plant AC power + POA irradiance to derive a production-based uptime '
                              'where status flags are absent (have — current proxy)'],
            'source_documents': ['SCADA/PPC historian (inverter status flags, PPC setpoint, power, irradiance)',
                                 'O&M contract + CMMS / work-order log (outage events, availability definition, '
                                 'guarantees)',
                                 'Monthly Technical Performance Report (plant-breakdown loss −90 MWh)',
                                 'Grid operator outage notifications'],
            'provider': 'EPC/O&M contractor (inverter status, work-orders, contractual availability); asset manager '
                        '(collation); TSO TenneT / DSO (grid outages)',
            'cadence': 'daily',
            'tinte_status': 'partial',
            'source_documents_present': 'Power, irradiance and PPC setpoint are present, enabling only a coarse '
                                        'daylight-uptime proxy (intervals producing > 1% of AC). True availability '
                                        'needs per-inverter status/fault flags, the O&M-contract availability '
                                        'definition/guarantee, and the work-order outage log — none of which are in '
                                        "the feed. The report's plant-breakdown loss (−90 MWh) is the only "
                                        'availability-loss indication.'},
           {'id': 'curtailment-rate',
            'name': 'Curtailment Rate',
            'required_data': ['PPC active-power setpoint time-series (% or kW ceiling) flagging curtailment '
                              'intervals (have)',
                              'Actual plant AC power and metered export during curtailed intervals (have)',
                              'Available/expected power (model or irradiance-implied potential) during each '
                              'curtailed interval to quantify lost MWh (curtailed = potential − actual)',
                              'Curtailment-instruction source/attribution: TSO/DSO grid-constraint dispatch vs '
                              'negative-price/economic vs internal — to split grid curtailment from commanded '
                              'down-regulation',
                              "Grid-outage vs curtailment separation so the report's combined 'Grid + curtailment "
                              "−148 MWh' line can be split"],
            'source_documents': ['SCADA/PPC historian (setpoint signal + actual power)',
                                 'Monthly Technical Performance Report (combined Grid + curtailment loss −148 MWh, '
                                 'flagged tentative)',
                                 'TSO/DSO curtailment / redispatch instructions (grid-constraint dispatch records)',
                                 'Energy-model / irradiance-implied available-power estimate'],
            'provider': 'EPC/O&M contractor + asset manager (SCADA/PPC setpoint); TSO TenneT / DSO (grid-constraint '
                        'curtailment instructions); technical advisor (available-power estimate)',
            'cadence': 'daily',
            'tinte_status': 'partial',
            'source_documents_present': 'The PPC setpoint signal flags curtailment intervals (122 in April) and is '
                                        'in the feed, but the curtailed-energy magnitude (potential − actual MWh) '
                                        'and the grid-vs-economic attribution are not directly captured — the report '
                                        'combines grid + curtailment (−148 MWh) and flags the split as tentative. '
                                        'Need TSO/DSO instructions and an available-power estimate to compute a true '
                                        'curtailment-rate %.'},
           {'id': 'degradation-warranty',
            'name': 'Module Degradation vs. Warranty',
            'required_data': ['Multi-year time-series of weather-corrected performance ratio or '
                              'temperature-corrected specific yield (kWh/kWp) to fit an annual degradation trend '
                              '(needs >=1-2 years; only 1 month available)',
                              'Module manufacturer warranty curve (year-1 induced loss + linear annual degradation '
                              '%, e.g. ~0.5%/yr over 25-30 yr) for the installed module type',
                              'Baseline / commissioning performance reference (PR or specific yield at COD, year-0 '
                              'flash-test data)',
                              'POA irradiance + module temperature for weather/temperature normalisation (have)',
                              'String-level DC current / Z-score health data to separate module degradation from '
                              'soiling, faults and curtailment (partially have via report string Z-scores)'],
            'source_documents': ['Module supply contract / product & performance warranty (degradation guarantee '
                                 'curve)',
                                 'Commissioning / provisional-acceptance test report (year-0 baseline PR, flash-test '
                                 'data)',
                                 'Multi-year SCADA historian (corrected PR / specific-yield trend)',
                                 'Monthly Technical Performance Report (string Z-score health proxy)'],
            'provider': 'asset manager (multi-year SCADA + baseline); EPC/O&M contractor / module supplier (warranty '
                        'curve, commissioning data); technical advisor (degradation analysis)',
            'cadence': 'annual',
            'tinte_status': 'missing',
            'source_documents_present': 'Only one month of data and no multi-year corrected-PR trend, no module '
                                        'warranty degradation curve, and no commissioning year-0 baseline are '
                                        "present. The report's string Z-score health (143 underperforming / 17 "
                                        'faulty / 1 severe) is shown as a related proxy only and cannot measure true '
                                        'module degradation vs warranty.'}]},
 {'category': 'Cost Control',
  'kpis': [{'id': 'total-opex-budget',
            'name': 'Total OpEx vs. Budget',
            'required_data': ['Actual operating expenditure by cost line, monthly (EUR): O&M fixed fee + '
                              'correctives, asset/technical management fee, land lease/grondvergoeding, insurance, '
                              'security & monitoring, business rates/local property tax (OZB) & WOZ levies, '
                              'TenneT/DSO grid connection & metering charges (aansluiting + transport), GvO '
                              'certificate issuance/registration fees, SDE++ administration, accounting/audit/legal, '
                              'spares & consumables, balancing/imbalance cost pass-throughs',
                              'Approved annual OpEx budget for the same cost lines, with monthly phasing (EUR)',
                              'Period-by-period budget vs actual variance (EUR and %) and YTD roll-up',
                              'Accruals for incurred-but-not-yet-invoiced costs and any one-off/non-recurring items '
                              'flagged separately',
                              'Currency/FX basis if any cost is invoiced outside EUR'],
            'source_documents': ['Monthly management accounts / general ledger OpEx actuals (SPV trial balance, '
                                 'cost-centre coded)',
                                 'Approved annual operating budget (project-finance model OpEx schedule / '
                                 'board-approved budget)',
                                 'O&M contract + asset/technical-management agreement (fee schedules)',
                                 'Land lease agreement, insurance policy schedule, grid connection/transport '
                                 'agreement (TenneT/DSO)',
                                 'Accounts-payable invoice register',
                                 'Audited annual financial statements (year-end true-up)'],
            'provider': 'Accounting/finance team (SPV) for actuals & accruals; asset manager for the approved '
                        'budget; EPC/O&M contractor and other counterparties for fee schedules feeding the budget',
            'cadence': 'monthly',
            'tinte_status': 'missing'},
           {'id': 'om-cost-mwh',
            'name': 'O&M Cost per MWh',
            'required_data': ['Actual O&M cost per period (EUR): O&M base fee + corrective/unplanned maintenance + '
                              'spares — defined consistently (O&M-only vs full OpEx; recommend O&M-scope only for '
                              'this KPI)',
                              'Metered net generation for the same period (MWh) — half-hourly/15-min metered export '
                              'aggregated to monthly, net of station/parasitic load',
                              'Computation EUR(O&M) / MWh(net export), with a budget/P50 reference cost-per-MWh for '
                              'comparison'],
            'source_documents': ['O&M contract (fee schedule + corrective rate card) and corrective work-order '
                                 'invoices/cost log',
                                 'Monthly management accounts / GL (O&M cost lines)',
                                 'SCADA/PPC historian + grid main-meter (15-min metered export) — already '
                                 'materialised as data/tinte/meter_15min.parquet',
                                 'Monthly Technical Performance Report (actual generation MWh)',
                                 'Project-finance model (budgeted O&M cost-per-MWh benchmark)'],
            'provider': 'EPC/O&M contractor (O&M cost & corrective work orders); accounting/finance team (booked O&M '
                        'actuals); asset manager (metered generation from SCADA/meter + budget benchmark)',
            'cadence': 'monthly',
            'tinte_status': 'partial'},
           {'id': 'mttr',
            'name': 'Mean Time To Repair (MTTR)',
            'required_data': ['Per-incident work-order records with fault/alarm raised timestamp, '
                              'response/acknowledgement timestamp, repair-start and repair-complete '
                              '(return-to-service) timestamps',
                              'Repair duration per work order (clock-time, with site-access/parts-wait/weather '
                              'clock-stops flagged so a net repair time can also be derived)',
                              'Asset/equipment level affected (inverter, string/combiner box, transformer, MV '
                              'switchgear, PPC, comms) and fault classification/severity',
                              'Count of completed corrective work orders in the period to compute the mean = '
                              'sum(repair times)/number of repairs',
                              'Optional cross-link to SCADA/PPC inverter status & alarm flags to validate downtime '
                              'windows (inverter status flags are NOT in the current Tinte feed — only a power>1% '
                              'uptime proxy exists)'],
            'source_documents': ['O&M contractor CMMS / work-order management system (corrective work-order log with '
                                 'timestamps)',
                                 'Ticketing/incident log and field-service reports / site visit reports',
                                 'SCADA/PPC historian alarm & inverter-status log (for downtime corroboration)',
                                 'O&M contract SLA schedule (defines response/repair-time targets to benchmark MTTR '
                                 'against)'],
            'provider': 'EPC/O&M contractor (CMMS work orders, field reports, alarm log); asset manager (SLA '
                        'targets, aggregation/reporting)',
            'cadence': 'monthly',
            'tinte_status': 'missing'}]},
 {'category': 'Counterparty & Risk',
  'kpis': [{'id': 'merchant-exposure',
            'name': 'Merchant Exposure (%)',
            'required_data': ['Half-hourly / 15-min metered export volume (MWh) per settlement period — splittable '
                              'by revenue channel (PRESENT in Tinte feed as the grid main-meter 15-min export kWh)',
                              'Contracted (hedged) volume schedule: signed PPA/offtake nominated volume profile '
                              '(MWh) by period, plus pay-as-produced vs baseload/fixed-shape terms',
                              'Contracted price(s) and tenor: PPA strike price (EUR/MWh), CfD/SDE++ '
                              'contract-for-difference strike and reference price, escalation/indexation terms',
                              'Subsidy framework volumes/price: SDE++ subsidised MWh and base/correction-amount '
                              '(basisbedrag/correctiebedrag) so subsidised output is classed as contracted not '
                              'merchant',
                              'Merchant (uncontracted) volume = metered export minus contracted/subsidised volume '
                              'per period',
                              'EPEX NL day-ahead hourly price and intraday/imbalance reference prices (EUR/MWh) to '
                              'value the merchant-settled volume and revenue',
                              'Revenue split by channel (EUR): contracted-PPA revenue, subsidy revenue, '
                              'merchant/wholesale revenue — to express exposure on a value (not just volume) basis'],
            'source_documents': ['SCADA/PPC historian + grid main-meter export (Tinte technical feed — volume only)',
                                 'Signed PPA / offtake agreement (volume, price, tenor, shape, indexation)',
                                 'SDE++ subsidy grant / GvO certificate register (RVO) for subsidised volume and '
                                 'base amount',
                                 'Monthly revenue/settlement statements from the offtaker/route-to-market trader '
                                 '(channel revenue split)',
                                 'Wholesale market-data subscription (EPEX NL day-ahead / imbalance prices)',
                                 'Project-finance / hedging policy model (target hedge ratio benchmark)'],
            'provider': 'Offtaker/route-to-market trader (contracted volume + settlement split) and asset manager '
                        '(hedge policy); EPEX NL price via market-data vendor; SDE++/GvO via RVO and finance team; '
                        'metered volume from asset manager/TSO TenneT-DSO metering',
            'cadence': 'Monthly (exposure %), with daily/15-min volume and price inputs aggregated up',
            'tinte_status': 'partial'},
           {'id': 'dso-receivables',
            'name': 'DSO & Aged Receivables',
            'required_data': ['Accounts receivable / open invoice ledger: invoice date, due date, amount (EUR), '
                              'counterparty, and paid/cleared date per invoice',
                              'Issued sales invoices to offtaker/trader for energy, PPA, subsidy (SDE++ correction '
                              'payment) and GvO certificate sales (EUR)',
                              'Cash receipts / bank statements showing settlement of each invoice (to age unpaid '
                              'balances and compute DSO)',
                              'Total credit sales / revenue for the period and number of days in period (DSO = '
                              'average AR / credit sales × days)',
                              'Aging buckets (current, 1-30, 31-60, 61-90, 90+ days past due) and '
                              'disputed/credit-note adjustments',
                              'Underlying delivered MWh per counterparty to reconcile invoiced volume back to the '
                              'metered export (the metered export volume IS in the Tinte feed; the priced invoice/AR '
                              'layer is not)'],
            'source_documents': ['Accounts-receivable subledger / ERP (e.g. invoice ledger + aging report)',
                                 'Monthly revenue/settlement statements and self-bills from the offtaker/trader',
                                 'SDE++ correction-amount payment advices (RVO/CertiQ) and GvO sale invoices',
                                 'Bank statements / treasury cash-receipt records',
                                 'Audited / management accounts (period revenue and AR balance)'],
            'provider': 'Accounting/finance team (AR ledger, aging, cash receipts); offtaker/trader and RVO/CertiQ '
                        'for invoice and subsidy-payment confirmations',
            'cadence': 'Monthly (with invoice/payment events captured as they occur)',
            'tinte_status': 'missing'},
           {'id': 'counterparty-credit',
            'name': 'Counterparty Credit Exposure',
            'required_data': ['Identity and concentration of each revenue counterparty: offtaker/trader (PPA), TSO '
                              'TenneT (imbalance/programme responsibility), DSO, subsidy payer (RVO), GvO buyer — '
                              'with % of revenue each represents',
                              'Outstanding exposure per counterparty: open receivables + accrued-but-uninvoiced '
                              'delivered energy (mark-to-market of unsettled volume at EPEX NL price)',
                              'Counterparty credit quality: external credit rating, internal credit score, or parent '
                              'guarantee status',
                              'Credit support / collateral held: PPA security package (parent guarantee, letter of '
                              'credit, cash deposit, payment-security amounts) and netting terms',
                              'Contract tenor and replacement-cost / mark-to-market of the PPA vs current forward '
                              'curve (exposure if the counterparty defaults and the offtake must be re-contracted)',
                              'Payment history / default events per counterparty (from the AR aging and settlement '
                              'record)',
                              'Concentration limits / credit policy thresholds to RAG-flag breaches'],
            'source_documents': ['Signed PPA / offtake agreement (counterparty identity, credit support, security '
                                 'package, netting)',
                                 'Project-finance model + senior facility agreement (permitted-counterparty / '
                                 'credit-policy covenants)',
                                 'Monthly revenue/settlement statements from the offtaker (outstanding balances)',
                                 'Credit-rating reports / counterparty credit assessments (rating agency or '
                                 'internal)',
                                 'Forward price curve / wholesale market-data subscription (MtM replacement cost)',
                                 'Audited / management accounts and AR aging (current exposure)'],
            'provider': 'Asset manager / treasury & credit-risk function (exposure, limits, credit assessment); '
                        'offtaker/trader and TSO TenneT for counterparty balances; market-data vendor for forward '
                        'curve / MtM; lender/agent bank for covenant thresholds',
            'cadence': 'Quarterly (credit review), with monthly exposure/MtM refresh',
            'tinte_status': 'missing'}]}]

MODO_FINDING = {'solar_benchmark_found': False,
 'finding': "Modo's accessible API is GB battery-storage only (the ME-BESS-GB monthly revenue index). It exposes "
            'exactly ONE working data endpoint — GET /pub/v1/gb/modo/benchmarking/monthly-index-live — which returns '
            'a BESS revenue benchmark. Its "markets" are battery revenue stacks: bm (Balancing Mechanism), cm '
            '(Capacity Market), frequency_response, imbalance, reserve, wholesale (BESS wholesale-trading revenue, '
            'NOT a solar capture price), and total. Every other path probed returns 404 with a generic HTML error '
            'page: all directory-listing paths (/pub/v1/, /pub/v1/gb/, /pub/v1/gb/modo/, '
            '/pub/v1/gb/modo/benchmarking/) give no index; geography swaps gb->nl, gb->eu, gb->de all 404; every '
            'solar / capture-price / day-ahead / wholesale-price / solar-index path shape 404; no openapi.json / '
            'docs / schema discovery endpoint is reachable. Adding a technology=solar query param to the working GB '
            'endpoint is silently IGNORED — it returns the identical battery dataset, proving there is no solar '
            'filtering. CONCLUSION: there is NO Netherlands (or any non-GB) benchmark, and NO solar capture price / '
            'capture rate / generation-weighted wholesale / solar revenue index of any kind available via this API '
            'token. The accessible Modo API cannot benchmark Ampyr Tinte (NL solar). A separate data source (e.g. '
            'Aurora, EPEX/ENTSO-E NL day-ahead, or a Modo product not exposed on this token) would be required.',
 'endpoints_tried': [{'path': '/pub/v1/gb/modo/benchmarking/monthly-index-live?month_from=2026-04&month_to=2026-05&duration=*',
                      'status': '200',
                      'note': 'KNOWN-GOOD. Returns GB BESS revenue index. 7 market rows: bm, cm, frequency_response, '
                              'imbalance, reserve, wholesale, total. Battery-only (all per-MW battery revenue '
                              "stacks). 'wholesale' = BESS trading revenue, not solar capture price."},
                     {'path': '/pub/v1/',
                      'status': '404',
                      'note': 'No root directory listing (generic HTML 404 page).'},
                     {'path': '/pub/v1/gb/', 'status': '404', 'note': 'No gb listing.'},
                     {'path': '/pub/v1/gb/modo/', 'status': '404', 'note': 'No gb/modo listing.'},
                     {'path': '/pub/v1/gb/modo/benchmarking/', 'status': '404', 'note': 'No benchmarking listing.'},
                     {'path': '/pub/v1/nl/modo/benchmarking/monthly-index-live?month_from=2026-04&month_to=2026-05&duration=*',
                      'status': '404',
                      'note': 'Geography swap gb->nl: no NL equivalent exists.'},
                     {'path': '/pub/v1/nl/', 'status': '404', 'note': 'No NL namespace at all.'},
                     {'path': '/pub/v1/eu/modo/benchmarking/monthly-index-live',
                      'status': '404',
                      'note': 'EU geography swap: no EU index.'},
                     {'path': '/pub/v1/de/modo/benchmarking/monthly-index-live',
                      'status': '404',
                      'note': 'Germany swap: no DE index either (GB-only).'},
                     {'path': '/openapi.json', 'status': '404', 'note': 'No OpenAPI schema for endpoint discovery.'},
                     {'path': '/pub/v1/openapi.json', 'status': '404', 'note': 'No OpenAPI schema.'},
                     {'path': '/docs', 'status': '404', 'note': 'No docs/Swagger UI.'},
                     {'path': '/pub/v1/schema', 'status': '404', 'note': 'No schema endpoint.'},
                     {'path': '/pub/v1/gb/modo/benchmarking/solar-index-live',
                      'status': '404',
                      'note': 'No solar index analog to the BESS index.'},
                     {'path': '/pub/v1/gb/modo/solar/monthly-index-live',
                      'status': '404',
                      'note': 'No gb/modo/solar namespace.'},
                     {'path': '/pub/v1/gb/modo/benchmarking/solar', 'status': '404', 'note': 'No solar benchmark.'},
                     {'path': '/pub/v1/gb/modo/solar-capture', 'status': '404', 'note': 'No solar capture endpoint.'},
                     {'path': '/pub/v1/gb/modo/capture-price', 'status': '404', 'note': 'No capture-price endpoint.'},
                     {'path': '/pub/v1/gb/modo/benchmarking/capture-price',
                      'status': '404',
                      'note': 'No capture-price benchmark.'},
                     {'path': '/pub/v1/gb/modo/prices/day-ahead',
                      'status': '404',
                      'note': 'No day-ahead price series.'},
                     {'path': '/pub/v1/gb/modo/prices/wholesale',
                      'status': '404',
                      'note': 'No standalone wholesale price series.'},
                     {'path': '/pub/v1/nl/modo/benchmarking/solar-index-live',
                      'status': '404',
                      'note': 'No NL solar index.'},
                     {'path': '/pub/v1/nl/solar/benchmarking/monthly-index-live',
                      'status': '404',
                      'note': 'No NL solar benchmark (alt path shape).'},
                     {'path': '/pub/v1/nl/modo/solar/capture-price',
                      'status': '404',
                      'note': 'No NL solar capture price.'},
                     {'path': '/pub/v1/gb/modo/benchmarking/monthly-index-live?...&technology=solar',
                      'status': '200',
                      'note': 'technology=solar param SILENTLY IGNORED — returns identical battery dataset. Confirms '
                              'no solar filtering capability exists on the working endpoint.'}],
 'pull_instructions': ''}
