# YouTube + Gemini Quick Reference

## Fast YouTube Video Analysis with Gemini

### Method 1: Using Read-Media-Gemini Skill (Recommended)

```bash
cd ~/.gemini/antigravity/skills/Read-Media-Gemini
./scripts/run.sh "Your question here" --file "YOUTUBE_URL"
```

**Examples:**
```bash
# Summarize
./scripts/run.sh "Summarize this video" --file "https://www.youtube.com/watch?v=VIDEO_ID"

# Ask specific question
./scripts/run.sh "What are the main points?" --file "https://youtu.be/VIDEO_ID"

# Analyze content
./scripts/run.sh "Describe the visual elements and key information" --file "https://youtube.com/shorts/VIDEO_ID"
```

### Method 2: Direct Python API Call

```python
from google import genai
from google.genai import types
import os

# Setup
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Analyze YouTube video
response = client.models.generate_content(
    model='gemini-3-flash-preview',  # Latest Flash model
    contents=[
        types.Part.from_uri(
            file_uri='https://www.youtube.com/watch?v=VIDEO_ID',
            mime_type='video/mp4'
        ),
        types.Part.from_text('What is this video about?')
    ]
)

print(response.text)
```

### Method 3: Using google-generativeai Library

```python
import google.generativeai as genai
import os

# Configure
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Create model
model = genai.GenerativeModel('gemini-3-flash-preview')

# Analyze
response = model.generate_content([
    'What is this video about?',
    {'mime_type': 'video/mp4', 'uri': 'https://www.youtube.com/watch?v=VIDEO_ID'}
])

print(response.text)
```

## Supported YouTube URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/shorts/VIDEO_ID`
- `https://youtube.com/embed/VIDEO_ID`

## Requirements

1. **API Key**: Set `GEMINI_API_KEY` environment variable
2. **Video Access**: Video must be public and not geo-restricted
3. **Model**: Use `gemini-3-flash-preview` or `gemini-2.5-flash`

## Key Advantages

- ✅ **No download required** - Gemini accesses YouTube directly
- ✅ **Fast processing** - No local storage or upload needed
- ✅ **Works with long videos** - Gemini handles full video analysis
- ✅ **Multimodal understanding** - Analyzes both visual and audio content

## Common Use Cases

```bash
# Get timestamps of key moments
./scripts/run.sh "List the key moments with timestamps" --file "YOUTUBE_URL"

# Extract specific information
./scripts/run.sh "What products are mentioned in this video?" --file "YOUTUBE_URL"

# Analyze presentation style
./scripts/run.sh "Describe the visual style and production quality" --file "YOUTUBE_URL"

# Transcribe and summarize
./scripts/run.sh "Transcribe the main dialogue and summarize" --file "YOUTUBE_URL"
```

## Troubleshooting

**Error: "Cannot access video"**
- Video must be public (not private or unlisted)
- Check if video is geo-restricted
- Verify the URL is correct

**Error: "Rate limit exceeded"**
- Wait a few seconds and retry
- Check your API quota at https://aistudio.google.com/

**Slow response**
- Long videos (>30 min) take longer to process
- First request may be slower (Gemini processes the video)
- Subsequent questions about the same video are faster

## Performance Tips

1. **Be specific** - Ask targeted questions for faster responses
2. **Use latest model** - `gemini-3-flash-preview` is optimized for speed
3. **Batch questions** - Ask multiple questions in one prompt
4. **Cache results** - Save responses for repeated analysis

## Source

- Discovered via: `yt-analysis-mcp` by Legorobotdude
- Implementation: Read-Media-Gemini v2.3.0+
- Official docs: https://ai.google.dev/gemini-api/docs/vision
