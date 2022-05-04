#/bin/sh
source .venv/bin/activate
FLASK_APP=./trivia_api.py flask run --host=0.0.0.0
