# Agent Operating Guidelines for `yopu-cli`

## Scope & Purpose
`yopu-cli` provides an interface to query, parse, transpose, and serialize music chord charts from Yopu.co.

## Design Rules
1. **Zero Dependencies**: Keep dependencies limited to standard library Python 3.
2. **Deterministic Output**: JSON format (`--json`) must remain backwards compatible.
3. **Music Theory Soundness**: All chromatic shifts must accurately preserve interval distances and slash chord bass notes.
