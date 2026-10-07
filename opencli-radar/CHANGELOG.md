# Changelog

All notable changes to `opencli-radar` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to Semantic Versioning.

## [1.0.0] - 2026-10-08

### Added
- **Multi-Source Discovery Engine**: Ingests GitHub search API (`opencli-plugin-*`, `opencli-adapter-*`, high-star repos), official `jackwener/OpenCLI-Hub`, npm registry, and local estate.
- **Diagnostic-First Triage (`diagnose`)**: Outputs structured verdict (`REUSE_LOCAL`, `INSTALL`, `FORK_AND_VENDOR`, `READ_ONLY`, `BUILD_NEW`) with exact CLI remediation commands.
- **License & Compliance Gate**: Categorizes open-source (MIT, Apache, AGPL, GPL) vs unlicensed All Rights Reserved repositories to prevent IP risks.
- **Pagination & Completeness Handling**: Verifies full traversal across GitHub search results without truncation.
- **Supply Chain Defense**: Documents `--ignore-scripts` mandate and network egress audit patterns.
- **Automated Test Suite**: 11 unit tests covering normalization, collision exclusion, license triage, and diagnostic dispatch.
