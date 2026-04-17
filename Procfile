# Procfile — Railway deployment configuration for Janina
# 
# Phases:
#   release: Runs ONCE during deployment (load responses into DB)
#   web: Runs the main API service

# Load responses into Postgres during deployment
release: python load_responses.py --file responses.json

# Start the API server
web: gunicorn -w 4 -b 0.0.0.0:$PORT janina_api:app
