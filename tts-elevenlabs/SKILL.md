---
name: tts-elevenlabs
description: Text-to-speech using ElevenLabs. Vivid, human-like voice output. Use when user wants to speak text aloud, generate audio, or convert text to speech.
author: Vee
---

# TTS — ElevenLabs

Converts text to natural human-like speech via ElevenLabs API, auto-plays on macOS.

## Setup

```bash
pip install requests
export ELEVENLABS_API_KEY="your_key_here"  # or add to ~/.zshrc
```

Get API key: https://elevenlabs.io → Profile → API Key (free tier: 10k chars/mo)

## CLI Usage

```bash
speak "Your text here"
speak "你好世界" --voice George
speak "Hello" --voice Daniel --out ~/out.mp3
speak --list-voices
```

### Options
- `--voice NAME` — partial name match (e.g. "George", "Alice"). Default: rachel
- `--model ID` — default: `eleven_v3` (70+ languages, most expressive)
- `--out PATH` — save to file instead of playing

## Models
| Model | Use case |
|-------|----------|
| `eleven_v3` | Default. Latest, 70+ languages, most expressive |
| `eleven_multilingual_v2` | Emotionally rich, 29 languages |
| `eleven_flash_v2_5` | Ultra-low latency, conversational |

## Voices (recommended)
| Name | Style |
|------|-------|
| George | Warm, British, narration |
| Daniel | Steady, British, educational |
| Alice | Clear, British, educational |
| Brian | Deep, American, social |
| Jessica | Playful, American, conversational |
