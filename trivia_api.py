import logging
import trivia
from flask import Flask, request, send_file, Response, jsonify
from flask_restx import Api, Resource, reqparse
logging.basicConfig(level=logging.ERROR)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

trivia.create_empty_tables()

app = Flask(__name__)
api = Api(app)

parsertriviaget = reqparse.RequestParser()
parsertriviaget.add_argument("author")
parsertriviaget.add_argument("amount")
parsertriviaget.add_argument("category")
parsertriviaget.add_argument("difficulty")
parsertriviaget.add_argument("type")

nstrivia = api.namespace('trivia', 'Accumulators Chatbot Trivia APIs')
@nstrivia.route('/getquiz')
class TriviaGet(Resource):
  @api.expect(parsertriviaget)
  def get(self):
    author = request.args.get("author")
    amount = request.args.get("amount")
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")
    typeq = request.args.get("type")
    return trivia.get_quiz(author, amount, category, difficulty, typeq)

if __name__ == '__main__':
  app.run()
