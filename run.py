from app import create_app, db
from app.models import Patient, Doctor  # User is the doctor model


app = create_app()

# Flask shell context for easy DB access
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Patient': Patient, 'Doctor': Doctor}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)


