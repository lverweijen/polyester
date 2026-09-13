# The platform-specific fallback search is partly inspired by:
# https://github.com/bsgarcia/run-r
# Copyright (c) 2024 Brandon Garcia
# Licensed under the MIT License.

import os
import shutil
import sys
from pathlib import Path


def find_rscript() -> str | None:
    """Find the Rscript executable.

    The search order is:
    1. Rscript on PATH
    2. Rscript below R_HOME
    3. Platform-specific common installation locations
    """
    # First use the Rscript that would normally be invoked by the system.
    rscript = shutil.which("Rscript")
    if rscript is not None:
        return rscript

    # R_HOME identifies an R installation root.
    if r_home := os.environ.get("R_HOME"):
        rscript = Path(r_home) / "bin" / "Rscript"
        if rscript.is_file():
            return str(rscript)

    # Platform-specific fallbacks.
    if os.name == "nt":
        return _find_rscript_windows()

    if sys.platform == "darwin":
        for path in (
            "/usr/bin/Rscript",
            "/usr/local/bin/Rscript",
            "/opt/homebrew/bin/Rscript",
            "/Library/Frameworks/R.framework/Resources/bin/Rscript",
        ):
            if Path(path).is_file():
                return path

    else:
        for path in (
            "/usr/bin/Rscript",
            "/usr/local/bin/Rscript",
        ):
            if Path(path).is_file():
                return path

    return None


def _find_rscript_windows() -> str | None:
    """Find Rscript on Windows."""

    # The R installer registers the installation in Software\R-core\R.
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\R-core\R",
        ) as key:
            r_home, _ = winreg.QueryValueEx(key, "InstallPath")

        rscript = Path(r_home) / "bin" / "Rscript.exe"
        if rscript.is_file():
            return str(rscript)

    except (FileNotFoundError, OSError):
        pass

    # Fall back to scanning common locations...
    bases = (
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "R",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "R",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "R",
    )

    for base in bases:
        if not base.is_dir():
            continue

        versions = sorted(
            (p for p in base.iterdir() if p.is_dir()),
            reverse=True,
        )

        for version in versions:
            rscript = version / "bin" / "Rscript.exe"
            if rscript.is_file():
                return str(rscript)

    return None