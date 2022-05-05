import logging
import trivia
from flask import Flask, request, send_file, Response, jsonify, abort, json
from flask_restx import Api, Resource, reqparse
logging.basicConfig(level=logging.ERROR)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

trivia.create_empty_tables()

app = Flask(__name__)
api = Api(app)

parserquizcreate = reqparse.RequestParser()
parserquizcreate.add_argument("author", type=str)
parserquizcreate.add_argument("author_id", type=int)
parserquizcreate.add_argument("amount", type=int)
parserquizcreate.add_argument("category", type=str)
parserquizcreate.add_argument("difficulty", type=str)
parserquizcreate.add_argument("type", type=str)

nstrivia = api.namespace('trivia', 'Accumulators Chatbot Trivia APIs')
@nstrivia.route('/quiz/create')
class QuizCreate(Resource):
  @api.expect(parserquizcreate)
  @api.response(200, 'Success')
  @api.response(400, 'Generic Error')
  def get(self):
    try:
      author = request.args.get("author")
      author_id = request.args.get("author_id")
      amount = request.args.get("amount")
      category = request.args.get("category")
      difficulty = request.args.get("difficulty")
      typeq = request.args.get("type")
      quiz_data = trivia.create_quiz(author, author_id, amount, category, difficulty, typeq)
      resp = Response(json.dumps(quiz_data), mimetype='application/json')
      resp.status_code = 200
      return resp
    except Exception as e:
      abort(400, str(e))
      
parserquizinsert = reqparse.RequestParser()
parserquizinsert.add_argument("quiz_id", type=int)

@nstrivia.route('/quiz/get')
class QuizInsert(Resource):
  @api.expect(parserquizinsert)
  @api.response(200, 'Success')
  @api.response(400, 'Generic Error')
  def get(self):
    try:
      quiz_id = request.args.get("quiz_id")
      quiz_data = trivia.get_quiz(quiz_id)
      resp = Response(json.dumps(quiz_data), mimetype='application/json')
      resp.status_code = 200
      return resp
    except Exception as e:
      abort(400, str(e))


parserusersaveanswer = reqparse.RequestParser()
parserusersaveanswer.add_argument("questionid", type=int)
parserusersaveanswer.add_argument("answerid", type=int)
parserusersaveanswer.add_argument("userid", type=int)
parserusersaveanswer.add_argument("username", type=str)

@nstrivia.route('/user/saveanswer')
class UserSaveAnswer(Resource):
  @api.expect(parserusersaveanswer)
  @api.response(200, 'Success')
  @api.response(400, 'Generic Error')
  def get(self):
    try:
      questionid = request.args.get("questionid")
      answerid = request.args.get("answerid")
      userid = request.args.get("userid")
      username = request.args.get("username")
      save_data = trivia.save_answer(questionid, answerid, userid, username)
      resp = Response(json.dumps(save_data), mimetype='application/json')
      resp.status_code = 200
      return resp
    except Exception as e:
      abort(400, str(e))




parserusersave = reqparse.RequestParser()
parserusersave.add_argument("userid", type=int)
parserusersave.add_argument("username", type=str)

@nstrivia.route('/user/saveuser')
class UserSave(Resource):
  @api.expect(parserusersave)
  @api.response(200, 'Success')
  @api.response(400, 'Generic Error')
  def get(self):
    try:
      userid = request.args.get("userid")
      username = request.args.get("username")
      save_data = trivia.save_user_commit(username, userid)
      resp = Response(json.dumps(save_data), mimetype='application/json')
      resp.status_code = 200
      return resp
    except Exception as e:
      abort(400, str(e))




parserusergetanswer = reqparse.RequestParser()
parserusergetanswer.add_argument("questionid", type=int)
parserusergetanswer.add_argument("userid", type=int)

@nstrivia.route('/user/getanswer')
class UserGetAnswer(Resource):
  @api.expect(parserusergetanswer)
  @api.response(200, 'Success')
  @api.response(400, 'Generic Error')
  def get(self):
    try:
      questionid = request.args.get("questionid")
      userid = request.args.get("userid")
      get_data = trivia.get_answer(questionid, userid)
      resp = Response(json.dumps(get_data), mimetype='application/json')
      resp.status_code = 200
      return resp
    except Exception as e:
      abort(400, str(e))


if __name__ == '__main__':
  app.run()
