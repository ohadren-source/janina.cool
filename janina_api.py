"""
janina_api.py — Janina HR Platform API
======================================
Simple Flask API that serves 108 HR responses and handles form submissions.
Deploys directly to Railway.
"""

import os
import json
import logging
from datetime import datetime

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import psycopg2

import janina_banks

# Absolute path to the directory containing this file — use for all
# filesystem lookups so they are independent of the process CWD.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
PRIVACY_PDF = os.path.join(TEMPLATES_DIR, 'PRIVACY_POLICY_CONSOLIDATED.pdf')
SUPPORT_PDF = os.path.join(TEMPLATES_DIR, 'SUPPORT_PAGE_CONSOLIDATED.pdf')

app = Flask(__name__, static_folder='static')
CORS(app)

log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# Log PDF resolution at boot
logger.info(f"BASE_DIR = {BASE_DIR}")
logger.info(f"TEMPLATES_DIR = {TEMPLATES_DIR} (exists={os.path.isdir(TEMPLATES_DIR)})")
logger.info(f"PRIVACY_PDF = {PRIVACY_PDF} (exists={os.path.isfile(PRIVACY_PDF)})")
logger.info(f"SUPPORT_PDF = {SUPPORT_PDF} (exists={os.path.isfile(SUPPORT_PDF)})")
try:
    if os.path.isdir(TEMPLATES_DIR):
        logger.info(f"templates/ listing: {os.listdir(TEMPLATES_DIR)}")
    else:
        logger.error("templates/ directory is MISSING at runtime")
except Exception as e:
    logger.error(f"Could not list templates dir: {e}")

try:
    janina_banks.ensure_all_tables()
    logger.info("✓ All Janina tables initialized")
except Exception as e:
    logger.error(f"Failed to initialize tables: {e}")


@app.route('/', methods=['GET'])
def home():
    return render_template('janina.cool.html')


@app.route('/charculterie', methods=['GET'])
def charculterie():
    return render_template('charculterie.html')


@app.route('/privacy', methods=['GET'])
def privacy():
    logger.info(f"/privacy requested — checking {PRIVACY_PDF} (exists={os.path.isfile(PRIVACY_PDF)})")
    if not os.path.isfile(PRIVACY_PDF):
        logger.error(f"/privacy: file not found at {PRIVACY_PDF}")
        return jsonify({
            'error': 'Privacy PDF not found on server',
            'expected_path': PRIVACY_PDF,
            'base_dir': BASE_DIR,
            'templates_dir_exists': os.path.isdir(TEMPLATES_DIR),
            'templates_listing': os.listdir(TEMPLATES_DIR) if os.path.isdir(TEMPLATES_DIR) else None,
        }), 500
    try:
        return send_file(PRIVACY_PDF, mimetype='application/pdf')
    except Exception as e:
        logger.error(f"/privacy send_file failed: {e}")
        return jsonify({'error': f'send_file failed: {e}'}), 500


@app.route('/support', methods=['GET'])
def support():
    logger.info(f"/support requested — checking {SUPPORT_PDF} (exists={os.path.isfile(SUPPORT_PDF)})")
    if not os.path.isfile(SUPPORT_PDF):
        logger.error(f"/support: file not found at {SUPPORT_PDF}")
        return jsonify({
            'error': 'Support PDF not found on server',
            'expected_path': SUPPORT_PDF,
            'base_dir': BASE_DIR,
            'templates_dir_exists': os.path.isdir(TEMPLATES_DIR),
            'templates_listing': os.listdir(TEMPLATES_DIR) if os.path.isdir(TEMPLATES_DIR) else None,
        }), 500
    try:
        return send_file(SUPPORT_PDF, mimetype='application/pdf')
    except Exception as e:
        logger.error(f"/support send_file failed: {e}")
        return jsonify({'error': f'send_file failed: {e}'}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'janina_api',
    }), 200


@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats = janina_banks.get_janina_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/responses', methods=['GET'])
def get_responses():
    try:
        category = request.args.get('category')
        limit = int(request.args.get('limit', 50))
        if category:
            responses = janina_banks.get_response_by_category(category, limit)
        else:
            responses = janina_banks.get_all_responses(limit)
        return jsonify({'count': len(responses), 'responses': responses}), 200
    except Exception as e:
        logger.error(f"Failed to get responses: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/responses/search', methods=['GET'])
def search_responses():
    try:
        keyword = request.args.get('keyword')
        if not keyword:
            return jsonify({'error': 'keyword parameter required'}), 400
        limit = int(request.args.get('limit', 10))
        responses = janina_banks.search_responses_by_keyword(keyword, limit)
        return jsonify({'keyword': keyword, 'count': len(responses), 'responses': responses}), 200
    except Exception as e:
        logger.error(f"Failed to search responses: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/submit', methods=['POST', 'OPTIONS'])
def submit_form():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email required'}), 400
        name = data.get('name', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        form_data = data.get('form_data', {})
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
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
            return jsonify({'status': 'received', 'email': email, 'timestamp': datetime.utcnow().isoformat()}), 201
        else:
            return jsonify({'error': 'Failed to store submission'}), 500
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400
    except Exception as e:
        logger.error(f"Failed to submit form: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    try:
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        submissions = janina_banks.get_submissions(status, limit)
        return jsonify({'count': len(submissions), 'status_filter': status, 'submissions': submissions}), 200
    except Exception as e:
        logger.error(f"Failed to get submissions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    try:
        status = request.args.get('status', 'open')
        limit = int(request.args.get('limit', 50))
        feedback = janina_banks.get_feedback_by_status(status, limit)
        return jsonify({'count': len(feedback), 'status_filter': status, 'feedback': feedback}), 200
    except Exception as e:
        logger.error(f"Failed to get feedback: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback', methods=['POST'])
def post_feedback():
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
            return jsonify({'status': 'recorded', 'feedback_type': feedback_type, 'timestamp': datetime.utcnow().isoformat()}), 201
        else:
            return jsonify({'error': 'Failed to store feedback'}), 500
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400
    except Exception as e:
        logger.error(f"Failed to post feedback: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found', 'path': request.path}), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    logger.info(f"Starting Janina API on port {port} (debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)