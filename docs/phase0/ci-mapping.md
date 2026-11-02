# Mapping analyzer outputs onto causal-identifier/2 (for gate approval)

## Schema confirmed from the live page (2 Nov 2026)

Read from the page's embedded `DATA` object (`schema: "causal-identifier/2"`) with `scripts/check_ci_keys.py`.

Top level: schema, material, grade, date, fetchWorked, assumptions, snapshot, cost, supply, causes, delivered, episodes, workings, ruledOut, tracking, action, network, sources, couldNotVerify, confidence, weakestLink, nextData. **Matches the brief's list exactly.**

Nested keys:
- snapshot: benchmark, price, priceUSD, pricePKR, usdPkr, asOf, range52w, range3y, positionIn3y, weightBasis, unexplained, netPush, score, verdict, verdictRange, action, landedCostAdjustment, refs. (verdict, score and netPush live inside `snapshot`, not at top level.)
- cost: parts[{part, usdPerT, share, tag}], dominantLever, linkTest, parent, refs. Matches.
- causes[]: rank, id, label, name, weight, low, high, direction, strength, stale, horizon, grade, keyEvidence, mechanism, sensitivity, lag, current, alternative, watch, methodA, methodB, episodes[{when, what, priceEffect, refs}], indicators[{name, latest, date, frequency, bullishIf, neutral, bearishIf, score, refs}], refs. Matches.
- delivered[]: cause, usdPerSwing, pctLanded, direction, strength, grade, refs. Matches.
- episodes[]: id, start, end, startPrice, endPrice, pct, series, usedInMethodB, refs. Matches.
- supply: stages, sites, route, weather. workings: netPushArithmetic, coverage, methodBSplits, stabilityLow, stabilityHigh, decidedBy, sanity. tracking: timingTools, daily, weekly, monthly, scoringRule. action: contract, levelCaution, triggers. network: asOf, unit, scope, metrics, grades, sites, changes, flows, events, rules, unresolved. sources[]: n, name, usedFor, dataDate, tag, type, claim, group, url.

Current cause ids on the page: `cpl-supply`, `benzene`, `converter-capacity`, `cny`, `bias-demand`.

## Proposed mapping (one JSON per material and date)

| causal-identifier/2 field | From the analyzer |
| --- | --- |
| material, grade, date | purchase record material_key; breakdown purchase date |
| snapshot.priceUSD, pricePKR, usdPkr, asOf | breakdown nominal USD and PKR per tonne (× 1,000), and the FX used |
| snapshot.range52w, range3y, positionIn3y | real PO price over 52 weeks and 3 years (point-in-time) |
| snapshot.unexplained | breakdown unexplained share (%) |
| snapshot.weightBasis | "Verified (PO-based)" |
| cost.parts[] | one part per factor definition, contribution in USD/t and share; plus "Untracked: conversion and margin" (w_0) and "Unexplained remainder"; tag names config version and as-of date |
| causes[].weight, low, high | contribution shares now; after Phase 3, learned weights and their out-of-sample range |
| causes[].direction, strength | sign of the factor's 3-month change |
| causes[].current, stale, lag | latest verified value and date, staleness flag, declared lag |
| causes[].episodes[] | global events with learned impact, n_cases, estimate date and sources |
| causes[].indicators[] name, latest, date, frequency, refs | factor value series; the bullish/neutral/bearish bands and score stay the identifier's |
| delivered[] | freight and USD/PKR contributions, once Phase 3 settles the price basis |
| episodes[] | PO-price episodes (start/end month, prices, change), series named as the analyzer's |
| sources[], workings, couldNotVerify, confidence, weakestLink, nextData | provenance, explained share, config version, flags, coverage gaps |
| competitorGap (new, additive) | competitor records and the gap per factor (Phase 4); additive, so the current page still reads the JSON |

Left to the Causal Identifier: snapshot.verdict, snapshot.score, snapshot.netPush, action, supply, network, ruledOut, tracking.

## Linking factors to causes: what the data shows

The link runs through each ext series' `cause` field. As read on 2 Nov 2026:

| ext series | cause field | Matches a causes[].id? | Proposed target |
| --- | --- | --- | --- |
| cpl | cpl-supply | yes | causes[cpl-supply] |
| benzene | benzene | yes | causes[benzene] |
| brent | benzene | yes | causes[benzene] (the brief's list omitted brent) |
| usdcny | cny | yes | causes[cny] |
| freight | freight | no cause with that id | delivered[] "Sea freight China to Karachi" |
| usdpkr | pkr | no cause with that id | delivered[] "USD/PKR exchange rate" |
| haiyang | market | no | price benchmark (snapshot / episodes), not a factor |
| pama | "Bias-tyre demand" (a label, not an id) | label of causes[bias-demand] | causes[bias-demand]; the field should hold the id |

`converter-capacity` has no ext series; in v1 it sits inside w_0 (untracked conversion and margin). Proposal: each factor definition carries an optional `host_cause` (cause id or `delivered:<name>`) added at integration, so the mapping is explicit rather than inferred. Agreed (Q4): `host_cause` is in the factor_definition schema.

## Event category mapping (Causal Identifier → event_type)

| CI category | Docs | event_type |
| --- | --- | --- |
| conflict | 14 | conflict |
| macro-pk | 9 | fx_shock |
| logistics | 4 | shipping_disruption |
| industry | 3 | plant_outage (cpl-closures-2026, cpl-china-cut-2025); cpl-glut-2025 → capacity_cycle (Q5) |
| weather | 3 | weather |
| pandemic | 3 | disease |
| trade | 5 | trade_policy (us-china-trade-war, us-tariffs-2025); yuan-7-2019, yuan-below-7-2025, yuan-slide-2022 → fx_shock |
| policy | 8 | sanctions (us-iran-sanctions-2018); supply_policy for OPEC/OPEC+ cuts and unwinds (4, Q5), china-env-2017 and china-power-cuts → plant_outage; brexit-2020 (not relevant) → trade_policy |
| other | 4 | none fits (FIFA, Notre-Dame, Olympics, Queen's death; all relevant=false): not imported |

So 49 of 53 events map; the 4 "other" placebo events are not imported. Q5 added `supply_policy` and `capacity_cycle`, so every mapped event has an exact type.

## Two things for the page owner (reported, not fixed)

1. `po` stores each PO line twice (3,978 rows for 1,989 lines), one copy shifted a day earlier (373 Sundays vs 5 in the file).
2. `ext/freight` is tagged V but its history comes from a third-party GitHub dashboard compiling Korea NLIC data, not from the Shanghai Shipping Exchange; the analyzer will record it as such.
