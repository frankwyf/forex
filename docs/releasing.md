# Releasing

Releases are source distributions of the Django application, not PyPI packages or hosted deployments.

1. Update forex.__version__, CHANGELOG.md and docs/releases/vX.Y.Z.md together. Review any dependency snapshot changes.
2. Run python -m pip check and python scripts/verify.py. Review the diff for runtime files and secrets.
3. Open a PR and wait for every supported CI matrix job to pass. Merge the reviewed result.
4. Fetch main, confirm a clean tree, and create an annotated vX.Y.Z tag on the verified main commit. Use the maintainer's GitHub noreply email.
5. Push that tag. The Release workflow reruns the same complete CI matrix on the tag.
6. Only after all jobs pass, the workflow validates tag/version/HEAD agreement, builds ZIP and tar.gz archives from tracked Git files, calculates SHA256SUMS.txt, and publishes a GitHub release using the checked-in notes.
7. Inspect the workflow and published assets. Do not move an already published tag to fix a problem; publish a new patch version.

A local preview can be built with python scripts/build_release.py --output dist from a clean committed checkout. With --tag vX.Y.Z, the builder also enforces tag/version and commit equality.

The builder rejects tracked .env, SQLite databases, log files and .venv contents. Untracked files are excluded by git archive. File-name checks are defense in depth and are not a full secret scanner.

Third-party actions are pinned to official upstream revisions. Only the final release job receives contents:write; test jobs have contents:read. The release workflow does not deploy an application or modify an operator's database.

Verify downloaded assets by comparing their SHA-256 digest with SHA256SUMS.txt. The checksums establish transfer integrity; this release does not claim independent artifact signing or a reproducible build attestation.
