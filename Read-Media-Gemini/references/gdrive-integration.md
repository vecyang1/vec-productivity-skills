# Google Drive Integration

## Overview

Read-Media-Gemini now supports Google Drive URLs in addition to local file paths. The skill automatically detects Drive URLs, downloads the files to a temporary location, processes them, and cleans up afterward.

## Authentication Flow

The skill tries authentication methods in this order:

1. **gcloud** (preferred for developers)
   - Uses: `gcloud auth application-default print-access-token`
   - No setup needed if gcloud is already configured

2. **OAuth Flow** (for first-time users)
   - Requires: `~/oauth_creds.json` (download from Google Cloud Console)
   - Opens browser for authorization on first use
   - Saves token to `~/.gdrive_token.json` for future use

3. **Cached Token**
   - Reuses `~/.gdrive_token.json` from previous OAuth flow
   - Auto-refreshes if expired

## Supported URL Formats

```bash
# Full Drive URL
https://drive.google.com/file/d/1ABC...XYZ/view

# Open URL format
https://drive.google.com/open?id=1ABC...XYZ

# Direct file ID (25+ alphanumeric characters)
1ABC...XYZ
```

## Usage Examples

```bash
# Single Drive file
./scripts/run.sh "Describe this image" \
  --file "https://drive.google.com/file/d/1ABC...XYZ/view"

# Mix local and Drive files
./scripts/run.sh "Compare these videos" \
  --file "/path/to/local.mp4" \
  --file "https://drive.google.com/file/d/1ABC...XYZ/view"

# Audio transcription from Drive
./scripts/run.sh "Transcribe this" \
  --file "https://drive.google.com/file/d/1ABC...XYZ/view" \
  --type audio

# Direct file ID
./scripts/run.sh "Analyze" --file "1ABC...XYZ"
```

## Implementation Details

### File ID Extraction
- Regex patterns match common Drive URL formats
- Falls back to treating input as direct file ID if it matches the pattern

### Download Process
1. Authenticate using available credentials
2. Fetch file metadata (name, mime type)
3. Download to temp file with proper extension
4. Return local path for processing

### Cleanup
- Drive temp files are tracked separately from compression temp files
- Cleanup happens in `finally` block to ensure files are removed even on error
- Uses `cleanup_temp_files()` helper function

## Error Handling

- Missing credentials: logs error and exits
- Invalid file ID: logs warning and skips file
- Download failure: logs error and continues with other files
- Missing dependencies: logs warning at import time

## Dependencies

Added to `requirements.txt`:
- `google-auth` - Core authentication
- `google-auth-oauthlib` - OAuth flow
- `google-auth-httplib2` - HTTP transport
- `google-api-python-client` - Drive API client

## Migration from gdrive-gemini-analyzer

This integration replaces the standalone `gdrive-gemini-analyzer` skill by merging its functionality directly into Read-Media-Gemini. The authentication logic and download mechanism are preserved, but now integrated seamlessly with the existing media processing pipeline.
