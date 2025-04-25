from decorators import admin_required

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin.html')
