# Nano-Banana Proxy Model Fix (2026-03-08)

## Issue
Nano-Banana was using `gemini-3.1-flash-image-preview` for Antigravity proxy, causing HTTP 404 errors and fallback to paid providers ($0.05/image).

## Fix
- Added `PROXY_FLASH_MODEL = "gemini-3.1-flash-image"` constant
- Updated `run_proxy_task()` to use proxy-specific model name (no `-preview` suffix)

## Proxy Model Support
✅ `gemini-3.1-flash-image` - Works
❌ `gemini-3.1-flash-image-preview` - 404
❌ `gemini-3-pro-image` - 404

## 4K Aspect Ratio Support (Tested & Confirmed)
✅ 1:1, 16:9, 9:16, 4:3, 3:4, 21:9

## Impact
- FREE proxy generation now works correctly
- No unexpected fallback to paid providers
- Full 4K support across all common aspect ratios

## Related Skills
- Nano-Banana (image generation)
- Nano-Banana-Pro (deprecated, use Nano-Banana)

## Key Takeaway
**Antigravity proxy requires model names WITHOUT `-preview` suffix**
