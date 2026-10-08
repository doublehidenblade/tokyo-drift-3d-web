# Experimental quality and traffic preview

Release playtest-20261008-841ec6b. Source 841ec6b8dd7ac6150d81d21a0df95f7ea68602f3.

Includes reversible 3D resolution controls (50/75/100%, default75; choose50 in Pause) and bounded traffic deadlock/crossing-priority repairs. Reduced resolution does not establish an FPS improvement. Traffic retains seven baseline collision cases and nine shutdown errors; it is not a complete traffic fix.

Essential import, export and package integrity checks passed. Formal visual, browser gameplay, physical-phone and FPS acceptance remain unestablished. Camera, map, garage, damage and police bugs remain. No camera or map patch is included.

Previous release playtest-20261008-1a5d967 and historical rollback live-v46-4ecd2089 are retained. No game implementation was merged to main and no manual GitHub Actions dispatch was used.
