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
parserquizcreate.add_argument("guild_id", type=int)

nsquiz = api.namespace('quiz', 'Quiz APIs')
@nsquiz.route('/create')
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
      guild_id = request.args.get("guild_id")
      quiz_data = trivia.create_quiz(author, author_id, amount, category, difficulty, typeq, guild_id)
      resp = Response(json.dumps(quiz_data), mimetype='application/json')
      resp.status_code = 200
      return resp
    except Exception as e:
      abort(400, str(e))
      
parserquizinsert = reqparse.RequestParser()
parserquizinsert.add_argument("quiz_id", type=int)
parserquizinsert.add_argument("guild_id", type=int)

@nsquiz.route('/get')
class QuizInsert(Resource):
  @api.expect(parserquizinsert)
  @api.response(200, 'Success')
  @api.response(400, 'Generic Error')
  def get(self):
    try:
      quiz_id = request.args.get("quiz_id")
      guild_id = request.args.get("guild_id")
      quiz_data = trivia.get_quiz(quiz_id, guild_id)
      resp = Response(json.dumps(quiz_data), mimetype='application/json')
      resp.status_code = 200
      return resp
    except Exception as e:
      abort(400, str(e))


parserquizend = reqparse.RequestParser()
parserquizend.add_argument("quiz_id", type=int)
parserquizend.add_argument("guild_id", type=int)

@nsquiz.route('/end')
class QuizEnd(Resource):
  @api.expect(parserquizend)
  @api.response(200, 'Success')
  @api.response(400, 'Generic Error')
  def get(self):
    try:
      quiz_id = request.args.get("quiz_id")
      guild_id = request.args.get("guild_id")
      quiz_data = trivia.end_quiz(quiz_id, guild_id)
      resp = Response(json.dumps(quiz_data), mimetype='application/json')
      resp.status_code = 200
      return resp
    except Exception as e:
      abort(400, str(e))

parserquizendall = reqparse.RequestParser()
parserquizendall.add_argument("guild_id", type=int)

@nsquiz.route('/endall')
class QuizEndAll(Resource):
  @api.expect(parserquizendall)
  @api.response(200, 'Success')
  @api.response(400, 'Generic Error')
  def get(self):
    try:
      guild_id = request.args.get("guild_id")
      quiz_data = trivia.end_all_quiz(guild_id)
      resp = Response(json.dumps(quiz_data), mimetype='application/json')
      resp.status_code = 200
      return resp
    except Exception as e:
      abort(400, str(e))


parserquizrunning = reqparse.RequestParser()
parserquizrunning.add_argument("is_running", type=int)
parserquizrunning.add_argument("guild_id", type=int)

@nsquiz.route('/running')
class QuizByRunning(Resource):
  @api.expect(parserquizrunning)
  @api.response(200, 'Success')
  @api.response(400, 'Generic Error')
  def get(self):
    try:
      is_running = request.args.get("is_running")
      guild_id = request.args.get("guild_id")
      quiz_data = trivia.quiz_by_running(is_running,guild_id)
      resp = Response(json.dumps(quiz_data), mimetype='application/json')
      resp.status_code = 200
      return resp
    except Exception as e:
      abort(400, str(e))


      
parserquizgetresults = reqparse.RequestParser()
parserquizgetresults.add_argument("quiz_id", type=int)
parserquizgetresults.add_argument("guild_id", type=int)

@nsquiz.route('/getresults')
class QuizGetResults(Resource):
  @api.expect(parserquizgetresults)
  @api.response(200, 'Success')
  @api.response(400, 'Generic Error')
  def get(self):
    try:
      quiz_id = request.args.get("quiz_id")
      guild_id = request.args.get("guild_id")
      quiz_data = trivia.get_quiz_results(quiz_id,guild_id)
      resp = Response(json.dumps(quiz_data), mimetype='application/json')
      resp.status_code = 200
      return resp
    except Exception as e:
      abort(400, str(e))




nsquestions = api.namespace('questions', 'Questions APIs')
      
parserquestionsget = reqparse.RequestParser()
parserquestionsget.add_argument("question_id", type=int)
parserquestionsget.add_argument("number", type=int)
parserquestionsget.add_argument("quiz_id", type=int)

@nsquestions.route('/get')
class QuestionsGet(Resource):
  @api.expect(parserquestionsget)
  @api.response(200, 'Success')
  @api.response(400, 'Generic Error')
  def get(self):
    try:
      question_id = request.args.get("question_id")
      number = request.args.get("number")
      quiz_id = request.args.get("quiz_id")
      questions_data = trivia.get_question(question_id, number, quiz_id)
      resp = Response(json.dumps(questions_data), mimetype='application/json')
      resp.status_code = 200
      return resp
    except Exception as e:
      abort(400, str(e))



nsanswers = api.namespace('answers', 'Answers APIs')

      
parseranswersget = reqparse.RequestParser()
parseranswersget.add_argument("answer_id", type=int)

@nsanswers.route('/get')
class AnswersGet(Resource):
  @api.expect(parseranswersget)
  @api.response(200, 'Success')
  @api.response(400, 'Generic Error')
  def get(self):
    try:
      answer_id = request.args.get("answer_id")
      answers_data = trivia.get_answers(answer_id)
      resp = Response(json.dumps(answers_data), mimetype='application/json')
      resp.status_code = 200
      return resp
    except Exception as e:
      abort(400, str(e))


nsuser = api.namespace('user', 'User APIs')
parserusersaveanswer = reqparse.RequestParser()
parserusersaveanswer.add_argument("questionid", type=int)
parserusersaveanswer.add_argument("answerid", type=int)
parserusersaveanswer.add_argument("userid", type=int)
parserusersaveanswer.add_argument("username", type=str)

@nsuser.route('/saveanswer')
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

@nsuser.route('/saveuser')
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

@nsuser.route('/getanswer')
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