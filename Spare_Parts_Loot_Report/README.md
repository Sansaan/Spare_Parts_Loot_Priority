# Setup virtual environment

source venv/bin/activate

# Run flask app in dev mode

FLASK_APP=app.py FLASK_ENV=development flask run

# Run flask app in production mode

FLASK_APP=app.py flask run
