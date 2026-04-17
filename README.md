# JANINA — sauc-e.com Feedback Platform

Janina is the anti-RILIE. She's here to help, we guess. Shrug.

## What's Included

- **janina.cool.html** — The web interface (responses hardcoded)
- **janina_api.py** — Flask API for handling submissions and chat
- **janina_banks.py** — Postgres layer (responses, submissions, feedback)
- **load_responses.py** — Bulk loader for responses into the database
- **responses.json** — Your responses (customize this)
- **Procfile** — Railway deployment config
- **requirements.txt** — Python dependencies
- **.gitignore** — What to exclude from git

## Quick Start

### Local Development

1. **Install Python 3.11+**
2. **Create virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```
   export DATABASE_URL=postgres://user:password@localhost:5432/janina_dev
   export FLASK_ENV=development
   ```

5. **Run the API:**
   ```
   python janina_api.py
   ```

6. **Open janina.cool.html** in your browser

### Deploy to Railway

1. **Push to GitHub:**
   ```
   git init
   git add .
   git commit -m "Initial Janina setup"
   git remote add origin https://github.com/your-username/janina.git
   git push -u origin main
   ```

2. **Go to railway.app**
3. **Create new project → Select your janina GitHub repo**
4. **Railway auto-detects Procfile and deploys**
5. **Postgres is created automatically**
6. **Your API goes live**

## Customize responses.json

Edit `responses.json` to include your actual responses. Format:

```json
[
  {
    "category": "benefits",
    "query_type": "faq",
    "keywords": ["vacation", "pto"],
    "response_text": "Your response here",
    "quality_score": 0.95
  },
  ... (repeat as needed)
]
```

Categories: benefits, payroll, hiring, compliance, general, training, performance, etc.

## API Endpoints

- `GET /health` — Liveness probe
- `POST /api/submit` — Submit form with email
- `GET /api/stats` — Overall stats
- `GET /api/responses?category=benefits` — Get responses by category
- `GET /api/responses/search?keyword=vacation` — Search responses
- `GET /api/feedback` — List feedback
- `POST /api/feedback` — Submit feedback

## Notes

- All responses are stored in Postgres
- Form submissions go to `janina_submissions` table
- Feedback goes to `janina_feedback` table
- No authentication required (it's a feedback hub, not Fort Knox)
- Janina doesn't care about your problems, but she'll listen anyway

## Support

Read the code. It's surgical. Everything is clear.

---

**janina.cool** — Running on pure indifference and Candy Crush energy.
# janina.cool
