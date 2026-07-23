# Agents v1 OpenRouter exact-route audit

This is a public operational endpoint audit, not a campaign amendment or scientific result.

- Audit time: `2026-07-23T22:37:03Z`
- Execution commit: `e7304cdd9a1c7242facebaa466ff388c243dce52`
- Campaign manifest authorizes OpenRouter: `false`
- Decision: `optional-public-calibration-only`
- Model-family diversity: `true` when both route audits are present
- Gateway diversity: `false`

Every selected request pins one returned provider slug, disables fallback, requires structured-output parameters, denies data collection, requires ZDR, and freezes the returned endpoint price as a maximum.

## Route results

### `mistralai/mistral-small-3.1-24b-instruct`

- Discovery: `pass`
- Selected exact provider slug: `none`
- Endpoints returned: `1`

### `google/gemini-2.5-pro`

- Discovery: `pass`
- Selected exact provider slug: `Google`
- Endpoints returned: `8`
