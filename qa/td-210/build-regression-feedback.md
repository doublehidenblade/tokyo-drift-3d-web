# td-210 — broad build regression finding

Root observed the completed after-build result in `regressions.json`: exit1, `FAIL: dressing: eaves (0)`, while the before-build passes. Source runtime intentionally suppresses old procedural Kamome eaves when authored market eaves replace them.

Resolve this as a substantive compatibility check: verify replacement eaves are present across the claimed lots in actual expanded geometry, and make the broad build assertion recognize that authorized replacement path without allowing missing eaves to pass. Preserve the original failing run and add a negative control if the existing focused coverage cannot detect their removal. Do not merely suppress the failure or label a new failure inherited. Re-run only affected checks after the evidence-backed change; retain the same production architecture unless the check reveals a real gap.

This is review preparation, not an independent acceptance verdict. Commit this finding with the worker's ordinary checkpoint.
