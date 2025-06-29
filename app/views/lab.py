from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Patient, LabTest, TestResult

lab_bp = Blueprint('lab', __name__, url_prefix='/lab')

# ✅ Lab dashboard - see pending tests
@lab_bp.route('/dashboard')
@login_required
def dashboard():
    tests = TestResult.query.filter_by(status='pending').all()
    return render_template('lab/dashboard.html', tests=tests)

# ✅ Update test result
@lab_bp.route('/result/<int:test_id>', methods=['GET', 'POST'])
@login_required
def update_result(test_id):
    test = TestResult.query.get_or_404(test_id)

    if request.method == 'POST':
        test.result = request.form['result']
        test.status = 'completed'
        db.session.commit()
        flash('Test result updated!', 'success')
        return redirect(url_for('lab.dashboard'))

    return render_template('lab/update_result.html', test=test)
