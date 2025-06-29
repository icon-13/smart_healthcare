# seed.py
from app import create_app, db
from app.models import Department

# Create the Flask app context
app = create_app()

departments_to_add = [
    "Laboratory",
    "Radiology",
    "Eye Clinic",
    "Cardiology",
    "Physiotherapy",
    "Surgery",
    "ENT",  # Ear, Nose, Throat
    "Orthopedics",
]

with app.app_context():
    for dept_name in departments_to_add:
        existing = Department.query.filter_by(name=dept_name).first()
        if not existing:
            new_dept = Department(name=dept_name)
            db.session.add(new_dept)
            print(f"Added department: {dept_name}")
        else:
            print(f"Department already exists: {dept_name}")

    db.session.commit()
    print("✅ Departments seeding complete!")
