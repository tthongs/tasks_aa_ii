# [TASK] Fix Locale Encoding & XKB Compose Table Lookup Failures

**Status**: Resolved
**Priority**: Low
**Affected Directory**: `/etc/locale.conf`, `/etc/locale.gen`

## Description
During system initialization and terminal launch, KWin Wayland and Konsole emitted repeated warnings indicating missing compose tables:
```text
kwin_wayland: XKB: [XKB-679] No Compose file for locale "en_IN.ISO8859-1": locale is either invalid or not installed
kwin_wayland: XKB: [XKB-679] couldn't find a Compose file for locale "en_IN" (mapped to "en_IN.ISO8859-1")
konsole: failed to create compose table
```

## Root Cause
`/etc/locale.conf` was configured with unqualified locale strings (`LANG=en_IN`, `LC_*=en_IN`) missing the `.UTF-8` character encoding suffix. Because the encoding was omitted, `libxkbcommon` and Qt's XKB backend defaulted to legacy `ISO8859-1`, which possesses no compose table definition for Indian English.

## Proposed Solution / Action Items
- [x] Created `fix_locale_utf8.sh` automation script.
- [x] Configured `/etc/locale.conf` with explicit `.UTF-8` definitions for all locale parameters:
  - `LANG=en_IN.UTF-8`
  - `LC_ADDRESS=en_IN.UTF-8`
  - `LC_IDENTIFICATION=en_IN.UTF-8`
  - `LC_MEASUREMENT=en_IN.UTF-8`
  - `LC_MONETARY=en_IN.UTF-8`
  - `LC_NAME=en_IN.UTF-8`
  - `LC_NUMERIC=en_IN.UTF-8`
  - `LC_PAPER=en_IN.UTF-8`
  - `LC_TELEPHONE=en_IN.UTF-8`
  - `LC_TIME=en_IN.UTF-8`
- [x] Regenerated locale definitions using `locale-gen`.
- [x] Verified `locale -a` and `/etc/locale.conf` integrity.

## Verification
- Running `locale -a` confirmed `en_IN.utf8` is active and recognized.
- Executable script `/home/tthhongs/build_tthongs/tasks_aa_ii/issues/fix_locale_utf8.sh` applies and verifies the configuration.
