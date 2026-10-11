# [TASK] Install and Configure LibreOffice Suite on CachyOS / KDE Plasma

**Status**: Resolved
**Priority**: Medium
**Affected Directory**: `/usr/lib/libreoffice`, `/usr/share/applications`, `/usr/bin/libreoffice`

## Description
User requested the installation of the LibreOffice productivity suite on CachyOS Linux (KDE Plasma 6 / Wayland environment). The objective is to provide a complete, feature-rich office suite comprising Writer (word processor), Calc (spreadsheets), Impress (presentations), Draw (vector graphics), Math (formula editor), and Base (database frontend), coupled with full desktop integration, spellchecking, hyphenation, and thesaurus support.

## Technical Details & Implementation
1. **Package Branch Selection (`libreoffice-fresh`)**:
   - The system runs CachyOS x86_64_v3 rolling release.
   - Selected `libreoffice-fresh` (`v26.8.0-2.1`), providing the latest upstream features, performance enhancements, and hardware acceleration compared to the conservative `libreoffice-still` branch.
2. **Desktop Integration (KDE Plasma 6 & Wayland)**:
   - LibreOffice leverages `qt6-multimedia` and `kio` (both pre-installed: KF6 6.30.0 / Qt 6.11.2) for native Qt6 rendering, Wayland window management, and seamless integration with KDE Plasma file dialogs.
3. **Linguistic & Spellchecking Tools**:
   - Deployed supplementary linguistic dictionaries to ensure full document authoring capabilities:
     - `hunspell-en_us` & `hunspell-en_gb`: US and UK English spell check dictionaries.
     - `hyphen-en`: High-quality English hyphenation and text justification rules.
     - `mythes-en` & `libmythes`: Full English thesaurus support.
4. **Desktop Launchers & MIME Database**:
   - Verified system-wide desktop launchers under `/usr/share/applications/`:
     - `libreoffice-writer.desktop`
     - `libreoffice-calc.desktop`
     - `libreoffice-impress.desktop`
     - `libreoffice-draw.desktop`
     - `libreoffice-math.desktop`
     - `libreoffice-base.desktop`
     - `libreoffice-startcenter.desktop`
   - Rebuilt the KDE Plasma application menu database using `kbuildsycoca6 --noincremental` and refreshed shared MIME information.
5. **Automation Script**:
   - Authored [`install_libreoffice.sh`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/install_libreoffice.sh) to encapsulate dependency installation, launcher validation, and desktop cache synchronization.

## Proposed Solution / Action Items
- [x] **Repository Analysis**: Probed available LibreOffice package branches (`cachyos-extra-v3/libreoffice-fresh`).
- [x] **Installed Productivity Suite**: Installed `libreoffice-fresh`, `hunspell-en_us`, `hunspell-en_gb`, `hyphen-en`, `mythes-en`, and `libmythes`.
- [x] **Verified KDE Plasma Integration**: Confirmed `kio` and `qt6-multimedia` compatibility for native KDE dialogs and Wayland rendering.
- [x] **Created Automated Script**: Added [`install_libreoffice.sh`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/install_libreoffice.sh) with launcher checks and cache triggers.
- [x] **Refreshed Sycoca Cache**: Executed `kbuildsycoca6 --noincremental` for instant availability in KDE Application Launcher and KRunner.
- [x] **Documented Commands**: Added Section 21 to [`unix_issues_cmds.txt`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/unix_issues_cmds.txt).
- [x] **Updated GEMINI.md**: Added `ISSUE_024` to the issue tracking index.

## Verification
- Validated binary version: `LibreOffice 26.8.0.3 e34ffb33db0c92181c79084d759a90d6bf45d9b3`.
- Tested headless document rendering and filter conversion pipeline:
  ```bash
  echo "Test LibreOffice conversion" > /tmp/test_libreoffice.txt
  libreoffice --headless --convert-to pdf /tmp/test_libreoffice.txt --outdir /tmp
  ```
  Verified output file `/tmp/test_libreoffice.pdf` generated cleanly with `writer_pdf_Export`.
- Verified presence of all 7 `.desktop` launcher files in `/usr/share/applications/`.
