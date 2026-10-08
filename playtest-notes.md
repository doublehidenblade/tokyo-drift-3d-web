# Experimental personal playtest

Runtime source: `1a5d967ca81d285aecf07be830811aff4fbef48f`.

This build is published for personal playtesting at the owner's request without waiting for CI or full gameplay acceptance. Publication checks establish artifact identity and serving, not gameplay approval.

Known limitations and open checks:
- Phone DPR sizing remains a known concern; physical-phone sizing/performance are not verified here.
- Gig completion and station/fuel flows are not fully verified for this combined release.
- Traffic collision blame remains an unresolved playtest concern.
- Reload-reset behavior remains a known limitation; do not assume progress or transient state survives reload.

Delivery uses 8 MiB chunks with per-chunk and assembled-pack SHA256 checks. Only the matching chunk-size constants changed in the existing packager and loader; runtime game source was not changed for publication. See `packaging-provenance.json` at site root.

The prior v46 client is retained at `releases/live-v46-4ecd2089/index.html`. Prior files and unrelated galleries are preserved.
