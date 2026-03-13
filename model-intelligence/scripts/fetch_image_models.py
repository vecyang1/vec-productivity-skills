#!/usr/bin/env python3
"""
Fetch best image/multimodal models from AA API
"""
import json
import subprocess

API_KEY = "aa_ktumuYkNLMYvZdymJrpbvKsJvhYMOrTP"

def fetch(endpoint):
    cmd = ['curl', '-s', '-X', 'GET',
           f'https://artificialanalysis.ai/api/v2/data/media/{endpoint}',
           '-H', f'x-api-key: {API_KEY}']
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None

# Fetch image models
print("Top Image Generation Models:\n")
img_gen = fetch('text-to-image')
if img_gen and 'data' in img_gen:
    for m in img_gen['data'][:5]:
        print(f"{m['elo']:4} | {m['model_creator']['name']:12} | {m['name']}")

print("\nTop Image Editing Models:\n")
img_edit = fetch('image-editing')
if img_edit and 'data' in img_edit:
    for m in img_edit['data'][:5]:
        print(f"{m['elo']:4} | {m['model_creator']['name']:12} | {m['name']}")

print("\nTop Multimodal LLMs (with vision):\n")
cmd = ['curl', '-s', '-X', 'GET',
       'https://artificialanalysis.ai/api/v2/data/llms/models',
       '-H', f'x-api-key: {API_KEY}']
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    data = json.loads(result.stdout)
    # Filter for models with vision and high intelligence
    vision_models = [m for m in data['data']
                     if m.get('evaluations', {}).get('artificial_analysis_intelligence_index')]
    vision_models = sorted(vision_models,
                          key=lambda x: x['evaluations']['artificial_analysis_intelligence_index'],
                          reverse=True)[:5]
    for m in vision_models:
        intel = m['evaluations']['artificial_analysis_intelligence_index']
        print(f"{intel:5.1f} | {m['model_creator']['name']:12} | {m['name']}")
