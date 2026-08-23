#!/usr/bin/env python3
import os, sys, argparse, tempfile, subprocess, requests

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
BASE = "https://api.elevenlabs.io/v1"

VOICES = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "adam":   "pNInz6obpgDQGcFmaJgB",
    "bella":  "EXAVITQu4vr4xnSDxMaL",
    "antoni": "ErXwobaYiN019PkySvjV",
}

def get_voices():
    r = requests.get(f"{BASE}/voices", headers={"xi-api-key": API_KEY})
    r.raise_for_status()
    for v in r.json()["voices"]:
        print(f"{v['name']:<20} {v['voice_id']}")

def speak(text, voice_name="rachel", out=None, model="eleven_v3"):
    vid = VOICES.get(voice_name.lower())
    if not vid:
        # try lookup by name from API
        r = requests.get(f"{BASE}/voices", headers={"xi-api-key": API_KEY})
        for v in r.json()["voices"]:
            if v["name"].lower().startswith(voice_name.lower()):
                vid = v["voice_id"]
                break
    if not vid:
        sys.exit(f"Voice '{voice_name}' not found. Run --list-voices.")

    r = requests.post(
        f"{BASE}/text-to-speech/{vid}",
        headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
        json={"text": text, "model_id": model},
        stream=True,
    )
    r.raise_for_status()

    if out:
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=4096):
                f.write(chunk)
        print(f"Saved: {out}")
    else:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            for chunk in r.iter_content(chunk_size=4096):
                f.write(chunk)
            tmp = f.name
        subprocess.run(["afplay", tmp])
        os.unlink(tmp)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("text", nargs="?")
    p.add_argument("--voice", default="rachel")
    p.add_argument("--out", default=None)
    p.add_argument("--model", default="eleven_v3")
    p.add_argument("--list-voices", action="store_true")
    args = p.parse_args()

    if not API_KEY:
        sys.exit("Set ELEVENLABS_API_KEY env var first.")
    if args.list_voices:
        get_voices()
    elif args.text:
        speak(args.text, args.voice, args.out, args.model)
    else:
        p.print_help()
