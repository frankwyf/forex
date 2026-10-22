"""Build source-only release archives from a clean, tracked Git revision."""

import argparse
import ast
import hashlib
import os
from pathlib import Path
import re
import subprocess


def git(root, *arguments):
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    return subprocess.check_output(
        ["git", "-C", str(root), *arguments], text=True, encoding="utf-8", env=env,
    ).strip()


def build(root, output, tag=None):
    root, output = Path(root).resolve(), Path(output).resolve()
    version = None
    for node in ast.parse((root / "forex" / "__init__.py").read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__version__" for t in node.targets):
            version = ast.literal_eval(node.value)
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("A semantic __version__ is required")
    if tag is not None:
        if tag != f"v{version}":
            raise ValueError("Release tag must match forex.__version__")
        if git(root, "rev-parse", f"{tag}^{{commit}}") != git(root, "rev-parse", "HEAD"):
            raise ValueError("Release tag must point to HEAD")
    if git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Release requires a clean tracked working tree")
    paths = git(root, "ls-files", "-z").split("\0")
    forbidden = [
        name for name in paths
        if name and (Path(name).name == ".env" or name.endswith((".sqlite3", ".log"))
                     or ".venv" in Path(name).parts)
    ]
    if forbidden:
        raise ValueError("Runtime or sensitive files must not be tracked: " + ", ".join(forbidden))
    output.mkdir(parents=True, exist_ok=True)
    archives = []
    for extension, archive_format in (("tar.gz", "tar.gz"), ("zip", "zip")):
        archive = output / f"forex-{version}.{extension}"
        with archive.open("wb") as stream:
            subprocess.run([
                "git", "-C", str(root), "archive", f"--format={archive_format}",
                f"--prefix=forex-{version}/", "HEAD",
            ], stdout=stream, check=True)
        archives.append(archive)
    sums = []
    for archive in archives:
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        sums.append(f"{digest}  {archive.name}\n")
    (output / "SHA256SUMS.txt").write_text("".join(sums), encoding="utf-8")
    return archives


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="Require this tag to match the version and HEAD")
    parser.add_argument("--output", default="dist")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    for archive in build(root, args.output, args.tag):
        print(archive)


if __name__ == "__main__":
    main()
