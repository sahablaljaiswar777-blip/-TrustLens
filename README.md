# TrustLens

## Project status

**MVP COMPLETE / VERIFIED**

The current MVP has passed its 25-test automated suite and a live Flask/UI verification of its primary routes, analysis and simulation workflows, SQLite history, reports, static assets, and responsive layouts.

## Overview

TrustLens is an educational, explainable heuristic cybersecurity analysis platform. It helps people review suspicious message and email-context text, URL strings, sender details, and QR-code destinations they have already decoded. Analysis is deterministic and runs locally in the Flask application.

### The real-world problem

People regularly receive messages that create urgency, request credentials or payment, impersonate an organization, or direct them to an unfamiliar destination. It can be difficult to notice and interpret these warning signs quickly, especially when several appear together.

### The solution

TrustLens inspects the strings a user submits for known warning patterns, then shows the detected indicators, their categories, explanations, point contributions, combined score, risk band, decision, and suggested next steps. The evidence path makes the relationship between signals and the resulting guidance visible.

TrustLens provides educational guidance, not a security verdict. Its heuristic analysis does not guarantee threat detection or safety.

## Major features

- Offline analysis of message text, pasted email/context, URL strings, sender/claimed-organization text, and pasted QR destinations.
- Deterministic content, URL-structure, sender-text, and social-engineering heuristics, with explainable per-signal risk contributions.
- Correlated risk scoring capped at 100, six risk bands, plain-language decisions, and recommendations.
- Dashboard metrics, recent activity, filterable local history, analysis details, and printable reports.
- Three fictional Simulation Lab scenarios using reserved `.test` and `.example` hostnames; simulations only run the same safe, local analysis.
- SQLite persistence of compact previews and structured results, with common sensitive values removed from previews.
- Responsive interface with keyboard-accessible navigation and reduced-motion support.

## Architecture

The application is organized into small Python modules:

- `app.py` wires Flask routes, input validation, pages, and analysis persistence.
- `config.py` contains local configuration defaults and input limits.
- `engine/content_analyzer.py`, `url_analyzer.py`, `sender_analyzer.py`, and `social_engineering.py` independently identify string-based indicators.
- `engine/risk_engine.py` combines signal points and assigns a risk band; `decision_engine.py` maps the score to a decision and recommendation.
- `engine/report_engine.py` orchestrates the analyzers into a structured result.
- `database/db.py` initializes SQLite and stores compact history and structured analysis results.
- `templates/` contains the Jinja2 pages; `static/` contains the stylesheet, small interface script, and favicon.
- `tests/` contains the standard-library `unittest` suite.

Risk bands map as follows: **TRUST** (0–19), **LOW** (20–39), **CAUTION** (40–59), **SUSPICIOUS** (60–79), **HIGH RISK** (80–94), and **CRITICAL** (95–100). Decisions are **TRUST**, **VERIFY**, **CAUTION**, **STOP**, **STOP**, and **CRITICAL**, respectively.

## Technology stack

- Python 3.10 or newer
- Flask and Jinja2
- SQLite
- HTML, CSS, and vanilla JavaScript
- Python standard library for analysis, persistence, and tests

`requirements.txt` contains Flask as the only third-party dependency. Jinja2 is installed as a Flask dependency; SQLite support and `unittest` are provided by Python.

## Installation

In PowerShell, from the project folder:

```powershell
Set-Location 'C:\Users\Sanchit\CopilotProjects\TrustLens'
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Running the application

From the project folder, run:

```powershell
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000/). The default local database is created at `instance\trustlens.sqlite3`. Set `TRUSTLENS_DATABASE` to use another database path. For deployment beyond local development, set `TRUSTLENS_SECRET_KEY` to a private random value and use a production WSGI server and HTTPS.

## Testing

Run the complete automated test suite from the project folder:

```powershell
python -m unittest discover -v
```

The verified suite contains 25 tests covering safe and suspicious content, URL strings, sender-text signals, correlated scores and score boundaries, decision mappings, validation, persistence, routes, history, and fictional simulations.

## Safe simulations

The Simulation Lab contains three fictional examples for practicing recognition of common warning signs. Their sample names use reserved `.test` or `.example` domains. Running a scenario submits its fixed fictional strings to the local analysis pipeline and saves the result in local history. It does not contact a destination or perform any attack action.

QR destinations must be pasted as text after decoding them separately with a trusted tool; TrustLens does not scan or decode QR images.

## Limitations and security boundaries

- **Offline heuristic analysis only:** TrustLens checks submitted strings with deterministic local rules. It does not use an external analysis API, fetch submitted URLs, resolve DNS, follow redirects, open links, or inspect webpage contents.
- **No independent verification:** The application cannot confirm sender identity, domain ownership, message intent, or maliciousness. A sender-text match is not authentication.
- **No guarantee:** Heuristics can miss harmful content or flag benign content. A low score does not prove that a message or destination is safe, and a high score is not independent confirmation of a threat.
- **Input scope:** Email and QR content is analyzed only when users paste its text or a decoded destination; there is no mailbox integration or QR-image decoding.
- **Local storage:** SQLite stores a short title/preview and structured analysis signals, not the full submitted form. Common credential-like values, email addresses, and URL query/fragment parameters are removed from previews, but users should still avoid submitting sensitive information.
- **Deployment:** The built-in Flask server is for local demonstration, not production hosting. Public use needs an appropriate production server, HTTPS, a strong secret key, authentication, and a data-retention policy.

## Future scope

Possible future work includes optional import/export of sanitized reports, configurable retention controls, broader test coverage for additional heuristic edge cases, and usability research. Any future integrations should remain opt-in, clearly disclose data handling, and preserve explicit safeguards against fetching user-submitted links.

## Project structure

```text
TrustLens/
├── .gitignore
├── README.md
├── app.py
├── config.py
├── requirements.txt
├── database/
│   ├── __init__.py
│   └── db.py
├── engine/
│   ├── __init__.py
│   ├── content_analyzer.py
│   ├── decision_engine.py
│   ├── report_engine.py
│   ├── risk_engine.py
│   ├── sender_analyzer.py
│   ├── social_engineering.py
│   └── url_analyzer.py
├── reports/
│   └── .gitkeep
├── static/
│   ├── css/style.css
│   ├── favicon.svg
│   └── js/app.js
├── templates/
│   ├── about.html
│   ├── analyze.html
│   ├── base.html
│   ├── error.html
│   ├── history.html
│   ├── index.html
│   ├── reports.html
│   ├── result.html
│   └── simulation.html
└── tests/
    ├── __init__.py
    ├── test_app.py
    ├── test_content.py
    ├── test_decision.py
    ├── test_risk.py
    ├── test_sender.py
    └── test_url.py
```

`instance\trustlens.sqlite3` is created locally at runtime and is intentionally excluded from version control.
