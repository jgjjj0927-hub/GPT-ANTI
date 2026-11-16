# Security remediation notes — ANTI-VURUS 3.2.0

## Dependency changes

- `requests` pinned to `2.34.2`, which is newer than the fixed versions for CVE-2024-47081 (`2.32.4`) and CVE-2026-25645 (`2.33.0`).
- `python-dotenv` pinned to `1.2.4`, newer than the fixed version for CVE-2026-28684 (`1.2.2`).
- `PyQt6` pinned to `6.12.1` and `watchdog` pinned to `7.1.0` based on the package releases available when this source archive was prepared.
- Removed `psutil` from runtime dependencies because no application module imports it.
- Added a weekly GitHub Actions `pip-audit` workflow; it checks direct requirements and their resolved dependencies.

## Code changes

- Removed `.env` from the project archive; retained only an empty `.env.example` template.
- Added `.env`, local state files, caches and build artifacts to `.gitignore`.
- Removed the hard-coded Telegram administrator password. Bot commands now require the configured numeric `ADMIN_ID`.
- Disabled Requests' implicit environment credential lookup in the Telegram session (`trust_env=False`).
- Replaced the shell-based hardware-ID command with local platform data hashing.
- Removed path interpolation from PowerShell invocation; the path is passed over standard input to a fixed script.
- Corrected the settings module import and moved Qt signals to class scope.
- Added bounded scanning, symlink avoidance, safer quarantine-path checks, atomic JSON writes and restore/delete rollback handling.
- Disabled automatic quarantine by default because heuristic detections can be false positives.
- Corrected the website CSS selectors and added `rel="noopener noreferrer"` to external new-tab links.

## Verification limits

- `compileall` and the included core unit tests pass in the build workspace.
- The GUI was not launched in this workspace because PyQt6 is not installed here. The Windows build workflow installs the pinned dependencies and compiles the app.
- `pip-audit` was not installed in the local workspace; the added GitHub Actions workflow performs that audit on pushes, pull requests and weekly.
- This scanner is heuristic and is not a certified antivirus engine. Local JSON licensing is not tamper-resistant; production licensing needs a server-side design.
- If the original `.env` file or archive was ever shared publicly, revoke its Telegram token. Removing the file from this new archive does not invalidate an already exposed token or erase repository history.
