# CareerMatch Agent — Product v2

A deployable single-user job discovery application that finds jobs from permitted public sources, matches them against a resume, scores them 0–100, and alerts on HIGH matches.

## Product rules
- HIGH: **75–100**
- MEDIUM: **55–74.99**
- LOW: **0–54.99**
- HIGH matches trigger Telegram/email alerts once when first discovered.
- Matching is job-fit scoring, not a guaranteed probability of selection.

## Features
- Resume PDF/DOCX/TXT/Markdown upload and profile extraction
- Configurable target roles, locations, required/preferred skills and exclusions
- Source management UI
- RSS, HTML, Greenhouse, Lever and Ashby adapters
- Deduplication
- Deterministic weighted scoring + TF-IDF semantic similarity
- HIGH/MEDIUM/LOW dashboard
- Application tracker: SAVED / APPLIED / INTERVIEW / OFFER / REJECTED / WITHDRAWN
- Telegram and SMTP email alerts
- REST API
- SQLite for local development; PostgreSQL/Supabase for production
- GitHub Actions scan approximately every 5 hours
- Docker and Render configuration

## Run locally
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/macOS
python -m uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000`.

Set a strong `ADMIN_TOKEN` in `.env`. The UI asks for this token before scan/source/preference/application mutations.

## First setup
1. Open `/setup` and upload your resume.
2. Open `/preferences` and set roles, locations and filters.
3. Open `/sources` and add permitted public job feeds/career/ATS endpoints.
4. Run a scan from Dashboard.
5. Configure Telegram or SMTP in `.env` for alerts.

## Production
Use Supabase/PostgreSQL for persistence. Do not store the database on an ephemeral web-service filesystem. Store secrets in your hosting provider/GitHub repository secrets.

### GitHub Actions
The included workflow uses:
```yaml
schedule:
  - cron: "0 0,5,10,15,20 * * *"
    timezone: "Asia/Kolkata"
```
This is approximately every 5 hours. Scheduled CI can occasionally be delayed.

### Required GitHub secrets
`DATABASE_URL`, `ADMIN_TOKEN`, `SECRET_KEY`, and optionally Telegram/SMTP secrets.

## Source compliance
Only use sources you are permitted to access. Prefer official APIs, RSS feeds, public career pages and public ATS endpoints. Do not bypass login, CAPTCHA, paywalls, robots restrictions or anti-bot controls.

## Scoring
Default weighting:
- Skills 40%
- Experience 20%
- Education 10%
- Responsibility/semantic similarity 15%
- Technology 10%
- Preferences 5%

The thresholds and weights should be treated as ranking rules, not hiring probabilities.
