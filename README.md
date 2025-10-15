## Compliance Assessment Tool (Streamlit)

Multi‑regulation data protection compliance assistant built with Streamlit. Assess against DPDP (India), PDPPL (Qatar), NPC (Qatar), OAIC (Australia) and more, generate reports, analyze privacy policies, and track results.

### Features
- **Assessments**: Dynamic questionnaires by regulation/industry with weighted scoring and recommendations.
- **AI reports**: Azure OpenAI powered narrative reports (configurable via env/secrets).
- **Privacy Policy Analyzer**: Fetches and analyzes a public privacy policy against selected law; exports PDF.
- **Data discovery views** and **FAQ** pages.
- **Logging** to `logs/` and `logs/privacy_policy/`.

### Quick start
Prerequisites: Python 3.10+ (3.11 recommended), `uv` package manager, Google Chrome (for optional Selenium fallback), Git.

```bash
# 1) Create and activate a virtual environment (uv)
uv venv
# PowerShell (Windows):
. .venv\Scripts\Activate.ps1
# cmd.exe (Windows):
.venv\Scripts\activate.bat
# bash (Linux/macOS):
source .venv/bin/activate

# 2) Install dependencies
uv pip install -r requirements.txt

# 3) Configure environment (see next section)

# 4) Run the Streamlit app
streamlit run app.py
```

### Configuration
The app reads configuration from environment variables and/or Streamlit `secrets.toml`.

- Azure OpenAI (required for AI features):
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_API_VERSION` (default: `2024-12-01-preview`)
  - `AZURE_OPENAI_DEPLOYMENT` (default: `gpt-5-mini`)
- Optional OpenRouter rotation keys (if used elsewhere):
  - `OPENROUTER_API_KEY_1`, `OPENROUTER_API_KEY_2`, `OPENROUTER_API_KEY_3`
- Optional: `COMPLIANCE_AI_API_KEY` (legacy check).

You can provide these via a local `.env` file or `~/.streamlit/secrets.toml`.

Example (PowerShell):
```powershell
$env:AZURE_OPENAI_ENDPOINT = "https://YOUR_RESOURCE.openai.azure.com"
$env:AZURE_OPENAI_API_KEY = "YOUR_KEY"
$env:AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
$env:AZURE_OPENAI_DEPLOYMENT = "gpt-5-mini"
```

Example `secrets.toml`:
```toml
AZURE_OPENAI_ENDPOINT = "https://YOUR_RESOURCE.openai.azure.com"
AZURE_OPENAI_API_KEY = "YOUR_KEY"
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
AZURE_OPENAI_DEPLOYMENT = "gpt-5-mini"
OPENROUTER_API_KEY_1 = "..."  # optional
```

### Project structure
```
DPDP-main/
  app.py                      # Streamlit entrypoint and routing
  config.py                   # Paths, environment, AI client helpers
  assessment.py               # Questionnaire loading, scoring, recommendations
  privacy_policy_analyzer.py  # Web fetch + Azure analysis + PDF export
  views.py                    # UI components/pages
  helpers.py, utils.py        # Session/init helpers and utilities
  Questionnaire/              # Per‑regulation JSON questionnaires
  Assets/                     # Logos and documents for laws
  data/                       # organizations/*.json and reports storage
  reports/                    # Generated markdown reports
  logs/                       # Daily app logs; privacy_policy/* analyzer logs
  tests/                      # Pytest tests
  requirements.txt
  README.md
```

### Running tests
```bash
# Install test deps (if not already present)
uv pip install pytest pytest-cov

# Run the suite
pytest -q

# Example: run a specific test file
pytest tests/test_PPA.py -q
```

### Code style
- Use Ruff for linting/formatting.
```bash
uv pip install ruff
ruff check .
ruff format .
```

### Logging
- App logs: `logs/app_YYYYMMDD.log`
- Privacy analyzer logs: `logs/privacy_policy/`

### Privacy Policy Analyzer notes
- Fetches page content via `requests` + BeautifulSoup and will fallback to Selenium.
- For Selenium fallback, install Chrome and compatible ChromeDriver in PATH.

### Data and reports
- Organization JSON profiles are in `data/organizations/`.
- Generated assessment reports saved under `reports/`.

### Troubleshooting
- AI features disabled or failing: ensure Azure env vars are set; verify network access.
- Questionnaire not found: check `Questionnaire/<REGULATION>/` contains the expected `*.json` files.
- Selenium errors: ensure Chrome is installed and `chromedriver` matches your Chrome version.

### License
Proprietary – internal use only unless a license file is provided.
