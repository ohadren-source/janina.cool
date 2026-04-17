"""
janina_api.py — Janina HR Platform API
======================================
Simple Flask API that serves 108 HR responses and handles form submissions.
Deploys directly to Railway.

Environment variables:
  - DATABASE_URL: Postgres connection string
  - FLASK_ENV: 'production' or 'development'
  - LOG_LEVEL: 'INFO', 'DEBUG', etc.

Routes:
  - GET  /api/responses                  → get by category or all
  - GET  /api/responses/search           → search by keyword
  - POST /api/submit                     → submit web form
  - GET  /api/submissions                → list submissions
  - GET  /api/feedback                   → list feedback
  - GET  /api/stats                      → health check
  - GET  /health                         → liveness probe
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Tuple

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import psycopg2

# Import Janina's database layer
import janina_banks

# ─────────────────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder='static')
CORS(app)

# Logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# Ensure tables on startup
try:
    janina_banks.ensure_all_tables()
    logger.info("✓ All Janina tables initialized")
except Exception as e:
    logger.error(f"Failed to initialize tables: {e}")


# ─────────────────────────────────────────────────────────────────────────
# Home
# ─────────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET'])
def home():
    """Serve the Janina frontend."""
    return render_template('janina.cool.html')


@app.route('/charculterie', methods=['GET'])
def charculterie():
    """Serve the CHARCULTERIE MENUFESTO."""
    return render_template('charculterie.html')


@app.route('/privacy', methods=['GET'])
def privacy():
    """Serve the consolidated Privacy Policy PDF."""
    return send_from_directory(
        'templates',
        'PRIVACY_POLICY_CONSOLIDATED.pdf',
        mimetype='application/pdf',
    )


@app.route('/support', methods=['GET'])
def support():
    """Serve the consolidated Support page PDF."""
    return send_from_directory(
        'templates',
        'SUPPORT_PAGE_CONSOLIDATED.pdf',
        mimetype='application/pdf',
    )


# ─────────────────────────────────────────────────────────────────────────
# Health & Status
# ─────────────────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    """Liveness probe for Railway."""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'janina_api',
    }), 200


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get comprehensive stats across all Janina tables."""
    try:
        stats = janina_banks.get_janina_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────
# HR Responses
# ─────────────────────────────────────────────────────────────────────────

@app.route('/api/responses', methods=['GET'])
def get_responses():
    """
    Get responses by category or all.
    
    Query params:
      - category: filter by category (e.g., 'benefits')
      - limit: max results (default 50)
    """
    try:
        category = request.args.get('category')
        limit = int(request.args.get('limit', 50))
        
        if category:
            responses = janina_banks.get_response_by_category(category, limit)
        else:
            responses = janina_banks.get_all_responses(limit)
        
        return jsonify({
            'count': len(responses),
            'responses': responses,
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get responses: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/responses/search', methods=['GET'])
def search_responses():
    """
    Search responses by keyword (full-text search).
    
    Query params:
      - keyword: search term (required)
      - limit: max results (default 10)
    """
    try:
        keyword = request.args.get('keyword')
        if not keyword:
            return jsonify({'error': 'keyword parameter required'}), 400
        
        limit = int(request.args.get('limit', 10))
        responses = janina_banks.search_responses_by_keyword(keyword, limit)
        
        return jsonify({
            'keyword': keyword,
            'count': len(responses),
            'responses': responses,
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to search responses: {e}")
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────
# Form Submissions
# ─────────────────────────────────────────────────────────────────────────

@app.route('/api/submit', methods=['POST', 'OPTIONS'])
def submit_form():
    """
    Submit web form with email and message.
    
    Expected JSON:
      {
        "email": "customer@example.com",
        "name": "Customer Name",
        "subject": "Question about benefits",
        "message": "I have a question about...",
        "form_data": { ... } (optional, any extra fields)
      }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        # Validate email
        email = data.get('email', '').strip()
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email required'}), 400
        
        # Extract fields
        name = data.get('name', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        form_data = data.get('form_data', {})
        
        # Get client info
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        # Store submission
        success = janina_banks.store_submission(
            email=email,
            name=name or None,
            subject=subject or None,
            message=message or None,
            form_data=form_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        if success:
            logger.info(f"Form submission received from {email}")
            return jsonify({
                'status': 'received',
                'email': email,
                'timestamp': datetime.utcnow().isoformat(),
            }), 201
        else:
            return jsonify({'error': 'Failed to store submission'}), 500
    
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400
    except Exception as e:
        logger.error(f"Failed to submit form: {e}")
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────
# Submissions Management
# ─────────────────────────────────────────────────────────────────────────

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """
    Get form submissions.
    
    Query params:
      - status: filter by status ('received', 'processed', etc.)
      - limit: max results (default 50)
    """
    try:
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        submissions = janina_banks.get_submissions(status, limit)
        
        return jsonify({
            'count': len(submissions),
            'status_filter': status,
            'submissions': submissions,
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get submissions: {e}")
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────
# Feedback Management
# ─────────────────────────────────────────────────────────────────────────

@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    """
    Get feedback/complaints.
    
    Query params:
      - status: filter by status ('open', 'resolved', etc.)
      - limit: max results (default 50)
    """
    try:
        status = request.args.get('status', 'open')
        limit = int(request.args.get('limit', 50))
        
        feedback = janina_banks.get_feedback_by_status(status, limit)
        
        return jsonify({
            'count': len(feedback),
            'status_filter': status,
            'feedback': feedback,
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get feedback: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback', methods=['POST'])
def post_feedback():
    """
    Submit feedback/complaint.
    
    Expected JSON:
      {
        "feedback_type": "complaint",
        "complaint_text": "Issue with...",
        "sentiment": "negative",
        "priority": 1
      }
    """
    try:
        data = request.get_json()
        
        feedback_type = data.get('feedback_type', 'general')
        complaint_text = data.get('complaint_text', '').strip()
        sentiment = data.get('sentiment', 'neutral')
        priority = int(data.get('priority', 0))
        
        if not complaint_text:
            return jsonify({'error': 'complaint_text required'}), 400
        
        success = janina_banks.store_feedback(
            feedback_type=feedback_type,
            complaint_text=complaint_text,
            sentiment=sentiment,
            priority=priority,
        )
        
        if success:
            return jsonify({
                'status': 'recorded',
                'feedback_type': feedback_type,
                'timestamp': datetime.utcnow().isoformat(),
            }), 201
        else:
            return jsonify({'error': 'Failed to store feedback'}), 500
    
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400
    except Exception as e:
        logger.error(f"Failed to post feedback: {e}")
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────
# Error Handlers
# ─────────────────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    """Handle 404."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500."""
    logger.error(f"Server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


# ─────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Janina API on port {port} (debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)
