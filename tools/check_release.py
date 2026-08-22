from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

init_text = (ROOT / "src" / "cd2_matrix_studio" / "__init__.py").read_text(encoding="utf-8")
pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
iss_text = (ROOT / "installer" / "cd2_matrix_studio.iss").read_text(encoding="utf-8")

package = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)
pyproject = re.search(r'^version\s*=\s*"([^"]+)"', pyproject_text, re.M)
installer = re.search(r'#define MyAppVersion\s+"([^"]+)"', iss_text)

if not package or not pyproject or not installer:
    raise SystemExit("Could not read every version marker.")

versions = {
    "package": package.group(1),
    "pyproject": pyproject.group(1),
    "installer": installer.group(1),
}

print("Release versions:")
for name, version in versions.items():
    print(f"  {name:10} {version}")

if len(set(versions.values())) != 1:
    raise SystemExit("Version mismatch.")

print("Version check OK.")
