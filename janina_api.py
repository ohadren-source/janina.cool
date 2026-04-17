# ─────────────────────────────────────────────────────────────
# REPLACE the existing /privacy and /support route handlers
# in janina_api.py with these two functions.
#
# Also delete the PRIVACY_PDF / SUPPORT_PDF path constants at
# the top of the file and the four boot-time logger.info lines
# that check for them — they're no longer relevant.
# ─────────────────────────────────────────────────────────────


@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template('privacy.html')


@app.route('/support', methods=['GET'])
def support():
    return render_template('support.html')
