# Setup & Configuration

## 1. Environment Variables

This skill uses **Vector Engine (向量引擎) as primary** and **Kie/Google as fallback** by default.

1.  Copy the example file:
    ```bash
    cp .env.example .env
    ```
2.  Edit `.env` and configure keys:
    ```bash
    PRIMARY_PROVIDER=vectorengine

    # Vector Engine (Primary)
    VECTORENGINE_API_KEY=your_vectorengine_key_here
    VECTORENGINE_BASE_URL=https://api.vectorengine.ai

    # Kie.ai (Alternative)
    KIE_API_KEY=your_kie_key_here
    KIE_MODEL=gemini-3-flash
    KIE_BASE_URL=https://api.kie.ai/gemini-3-flash/v1/chat/completions

    # Google (Fallback)
    GOOGLE_API_KEY=your_google_key_here
    GOOGLE_MODEL=gemini-3-flash-preview
    ```

Notes:
- If Vector Engine fails/unavailable, the runtime automatically falls back to Kie or Google.
- For multi-reference image analysis, pass multiple `--file` flags.

## 2. Dependencies & Runtime

We use a **Lazy-Loading** pattern to keep the global environment clean.

*   **Wrapper Script**: `scripts/run.sh`
*   **Mechanism**:
    1.  Checks for a local `.venv` folder.
    2.  If missing, creates it and installs `requirements.txt`.
    3.  Runs the python script inside this isolated environment.

## 3. Manual Installation (Optional)

If you prefer running without the wrapper:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Verify Tests

Run:
```bash
python3 -m unittest discover -s tests -v
# Or verify models independently
python3 tests/test_verify_models.py
```
