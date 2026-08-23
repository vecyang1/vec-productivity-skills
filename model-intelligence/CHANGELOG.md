# Changelog

## 2026-03-08 - Discovery Scripts Standardization

### Added
- **discover_openai.py**: Query OpenAI models API with registry enrichment
  - List all: `oo` or `python3 scripts/discover_openai.py`
  - Specific: `oo --model gpt-5.4-pro`
  - Shows context window for models in registry (20/90 models)
  
- **discover_claude.py**: Query Claude models from registry
  - List all: `cc` or `python3 scripts/discover_claude.py`
  - Specific: `cc --model claude-opus-4-6`
  - Registry-only (no Anthropic API for model listing)
  
- **Release date tracking**: Added `release_date` field to model registry
  - Format: YYYY-MM-DD
  - Displayed in model_info.py and discovery scripts
  - Example: gpt-5.4-pro released 2026-03-05

### Changed
- **discover_gemini_all.py**: Enhanced with registry enrichment
  - Now supports `--model` flag for specific model queries
  - Shows context window inline for models in registry
  - Maintains categorized list view (Text/Image/Experimental)

### Environment
- OPENAI_API_KEY: Added to ~/.zshrc
- ANTHROPIC_API_KEY: Added to ~/.zshrc
- GOOGLE_API_KEY: Already configured in Nano-Banana/.env

### Aliases
- `gg` - Gemini discovery
- `oo` - OpenAI discovery  
- `cc` - Claude discovery

### Limitations
- Provider APIs return minimal metadata (id, created timestamp only)
- Full specs (context, pricing, capabilities) require manual registry updates
- Coverage: OpenAI 20/90, Claude 7/7, Gemini ~10/30 models with full specs
- For unlisted models, use WebFetch on provider documentation pages
