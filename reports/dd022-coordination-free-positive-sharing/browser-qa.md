# DD-022 Coordination-Free Positive Sharing Lab browser QA

Date: 2026-07-22. Route tested locally:
`labs/coordination-free-positive-sharing.html` from the validated 76-page site.

The default `p=3/5,rho=1/2` private view rendered discovery `72%=18/25`, payoff
`36%=9/25`, collision `76%=19/25`, diversity `24%=6/25`, and centralized gap
`28%=7/25`. Selecting `rho=3/4`, shared information, and the private-equilibrium
baseline changed discovery to `71.6%`, exact gain to `9/1672`, and the status to
positive. Selecting `p=2/3,rho=1/4` and the direct baseline changed discovery to
`75%`, gain to `-8.3%`, agreement posterior to `75%`, and both regime labels.
Exactly one of the 42 fallback rows remained visible after each selection.

All four controls changed substantive output. Native labels, the live status,
updated chart accessible name, exact secondary values, complete captioned
42-row table, no-JavaScript notice, and immutable downloads were present.
Browser console errors: none. Repository validation separately checks heading
order, unique IDs, internal links, local assets, downloads, no tracking,
reduced motion, visible focus, and responsive layout.
