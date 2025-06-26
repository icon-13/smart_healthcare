from flask import Blueprint, jsonify
from app.models import Patient

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/check_uid/<uid>', methods=['GET'])
def check_uid(uid):
    patient = Patient.query.filter_by(rfid_uid=uid).first()
    return jsonify({"registered": bool(patient)})
