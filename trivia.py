import os
import requests
import sqlite3
import traceback
import html
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TMP_DIR = os.environ.get("TMP_DIR")
TRIVIA_API = os.environ.get("TRIVIA_API")

def create_quiz(author, author_id, amount, category, difficulty, typeq, guild_id):
  if not author:
    raise Exception("Author is mandatory")
  if author_id == 0 or not author_id:
    raise Exception("Author id is mandatory")
  if guild_id == 0 or not guild_id:
    raise Exception("Guild id is mandatory")
  if amount and amount is not None and amount != "" and int(amount) <= 10:
    url = TRIVIA_API + "?amount=" + amount
  elif not amount or amount is None or amount == "":
    url = TRIVIA_API + "?amount=5"
  else:
    raise Exception("Amount must be an integer")
  if category and category is not None and category != "":
    url = url + "&category=" + category
  if difficulty and difficulty is not None and difficulty != "":
    url = url + "&difficulty=" + difficulty
  if typeq and typeq is not None and typeq != "":
    url = url + "&typeq=" + typeq
  response = requests.get(url)
  return create_new_quiz(author, author_id, guild_id, response.json())

def check_temp_trivia_exists(): 
  fle = Path(TMP_DIR+'trivia.sqlite3')
  fle.touch(exist_ok=True)
  f = open(fle)
  f.close()

def create_empty_tables():
  check_temp_trivia_exists()
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_create_quiz_query = """ CREATE TABLE IF NOT EXISTS Quiz(
            id INTEGER PRIMARY KEY,
            author VARCHAR(255) NOT NULL,
            author_id INTEGER NOT NULL,
            is_running INTEGER NOT NULL,
            guild_id INTEGER NOT NULL
        ); """

    cursor.execute(sqlite_create_quiz_query)    
    
    
    sqlite_create_questions_query = """ CREATE TABLE IF NOT EXISTS Questions(
            id INTEGER PRIMARY KEY,
            number INTEGER NOT NULL,
            category VARCHAR(255) NOT NULL,
            type VARCHAR(255) NOT NULL,
            difficulty VARCHAR(255) NOT NULL,
            question INTEGER NOT NULL,
            is_last INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            FOREIGN KEY (quiz_id)
              REFERENCES Quiz (id) 
        ); """

    cursor.execute(sqlite_create_questions_query)


    sqlite_create_answers_query = """ CREATE TABLE IF NOT EXISTS Answers(
            id INTEGER PRIMARY KEY,
            answer VARCHAR(255) NOT NULL,
            is_correct INTEGER NOT NULL,
            questions_id INTEGER NOT NULL,
            FOREIGN KEY (questions_id)
              REFERENCES Questions (id) 
        ); """

    cursor.execute(sqlite_create_answers_query)

    sqlite_create_user_answers_query = """ CREATE TABLE IF NOT EXISTS Users(
            id INTEGER PRIMARY KEY,
            username VARCHAR(255) NOT NULL
        ); """

    cursor.execute(sqlite_create_user_answers_query)

    sqlite_create_user_answers_query = """ CREATE TABLE IF NOT EXISTS UserAnswers(
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            answer_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            FOREIGN KEY (user_id)
              REFERENCES Users (id),
            FOREIGN KEY (answer_id)
              REFERENCES Answers (id),
            FOREIGN KEY (question_id)
              REFERENCES Questions (question_id) 
        ); """

    cursor.execute(sqlite_create_user_answers_query)


  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  finally:
    if sqliteConnection:
        sqliteConnection.close()

def create_new_quiz(author, author_id, guild_id, content): 
  quiz_id = 0 
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_insert_quiz_query = """INSERT INTO Quiz
                          (author, author_id, is_running, guild_id) 
                           VALUES 
                          (?, ?, ?, ?)"""

    data_quiz_tuple = (author,author_id,1,guild_id,)

    cursor.execute(sqlite_insert_quiz_query, data_quiz_tuple)

    quiz_id = cursor.lastrowid

    numbercounter = 1

    for result in content['results']:
      sqlite_insert_questions_query = """INSERT INTO Questions
                            (number, category, type, difficulty, question, is_last, quiz_id) 
                            VALUES 
                            (?, ?, ?, ?, ?, ?, ?)"""

      

      is_last = 0
      if numbercounter == len(content['results']):
        is_last = 1

      data_questions_tuple = (numbercounter, 
        html.unescape(result['category']), 
        html.unescape(result['type']), 
        html.unescape(result['difficulty']), 
        html.unescape(result['question']), 
        is_last,
        quiz_id)
      cursor.execute(sqlite_insert_questions_query, data_questions_tuple)

      question_id = cursor.lastrowid

      sqlite_insert_answers_query = """INSERT INTO Answers
                            (answer, is_correct, questions_id) 
                            VALUES 
                            (?, ?, ?)"""
      data_correct_answer_tuple = (html.unescape(result['correct_answer']), 1, question_id)
      cursor.execute(sqlite_insert_answers_query, data_correct_answer_tuple)

      for incorrect_answer in result['incorrect_answers']:
        data_incorrect_answer_tuple = (incorrect_answer, 0, question_id)
        cursor.execute(sqlite_insert_answers_query, data_incorrect_answer_tuple)

      numbercounter += 1

    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  finally:
    if sqliteConnection:
        sqliteConnection.close()  
  if quiz_id != 0:
    save_data_set = {
        "Quiz_id":           quiz_id
    }
    return save_data_set
  else:
    raise Exception("Error creating new quiz")

def get_quiz(quiz_id: int, guild_id: int):
  quiz_data_set = None
  try:

    author = None
    is_running = None
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
    cursor_quiz = sqliteConnection.cursor()

    sqlite_select_quiz_query = """SELECT author, is_running, guild_id from Quiz WHERE id = ? and guild_id = ? ORDER BY ID DESC"""
    cursor_quiz.execute(sqlite_select_quiz_query, (quiz_id,guild_id,))
    records_quiz = cursor_quiz.fetchall()
    for row in records_quiz:
      author = row[0]
      is_running = row[1]
      guild_id = row[2]

    
    cursor_quiz.close()

    if not author:      
      if sqliteConnection:
        sqliteConnection.close()
      raise Exception("Author not found")

    cursor_questions = sqliteConnection.cursor()

    sqlite_select_questions_query = """SELECT * from Questions WHERE quiz_id = ? ORDER BY ID DESC"""
    cursor_questions.execute(sqlite_select_questions_query, (quiz_id,))
    records_questions = cursor_questions.fetchall()

    json_question_list = []

    for row in records_questions:
      idquestion =   row[0]
      number =       row[1]
      category =     row[2]
      typeq =        row[3]
      difficulty =   row[4]
      question =     row[5]
      is_last =      row[6]

      cursor_answers = sqliteConnection.cursor()

      sqlite_select_answers_query = """SELECT * from Answers WHERE questions_id = ? ORDER BY ID DESC"""
      cursor_answers.execute(sqlite_select_answers_query, (idquestion,))
      records_answers = cursor_answers.fetchall()

      json_answers_list = []

      for row in records_answers:
        idanswer =     row[0]
        answer =       row[1]
        is_correct =   row[2]
        
        answers_data_set = {
          "id":           idanswer, 
          "answer":       answer, 
          "is_correct":   is_correct
        }

        json_answers_list.append(answers_data_set)



      question_data_set = {
        "id":           idquestion, 
        "number":       number, 
        "category":     category, 
        "type":         typeq, 
        "difficulty":   difficulty, 
        "question":     question,
        "is_last":      is_last,
        "answers":      json_answers_list
      }
      json_question_list.append(question_data_set)

      cursor_answers.close()

    cursor_questions.close()

    quiz_data_set = {
        "id":           quiz_id, 
        "is_running":   is_running, 
        "author":       author, 
        "guild_id":     guild_id,
        "questions":    json_question_list
    }

  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  finally:
    if sqliteConnection:
      sqliteConnection.close()

  if quiz_data_set is not None:
    return quiz_data_set
  else:
    raise Exception("Quiz id not found")


def get_quiz_results(quiz_id: int, guild_id: int):
  result = {}
  try:

    author = None
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
    cursor_quiz = sqliteConnection.cursor()

    sqlite_select_quiz_query = """SELECT author from Quiz WHERE id = ? ORDER BY ID DESC"""
    cursor_quiz.execute(sqlite_select_quiz_query, (quiz_id,))
    records_quiz = cursor_quiz.fetchall()
    for row in records_quiz:
      author = row[0]

    
    cursor_quiz.close()

    if not author:      
      if sqliteConnection:
        sqliteConnection.close()
      raise Exception("Author not found")

    cursor_questions = sqliteConnection.cursor()
    

    sqlite_select_questions_query = """SELECT us.username, is_correct
                                       FROM UserAnswers ua
                                                 JOIN Users us on us.id = ua.user_id
                                                 JOIN Answers an on an.id = ua.answer_id
                                                 JOIN Questions qs on qs.id = an.questions_id
                                       JOIN Quiz qz on qz.id = qs.quiz_id
                                                 WHERE qz.id = ? and qz.guild_id = ?
                                                 ORDER BY us.username"""

    cursor_questions.execute(sqlite_select_questions_query, (quiz_id,guild_id,))
    records_questions = cursor_questions.fetchall()

    for row in records_questions:
      username =      row[0]
      is_correct =       row[1]

      if username in result.keys():
        result[username] = result[username] + is_correct
      else:
        result[username] = is_correct

      cursor_questions.close()

  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  finally:
    if sqliteConnection:
      sqliteConnection.close()

  return dict(sorted(result.items(), key=lambda item: item[1]))




def save_answer(questionid: int, answerid: int, userid: int, username: str):
  

  answers_data_set = get_answer_internal(questionid, userid)

  if(answers_data_set is not None):
    raise Exception("The user already answered the question!")


  save_id = 0
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')

    save_user_no_commit(username, userid, sqliteConnection)

    cursor = sqliteConnection.cursor()

    sqlite_save_query = """INSERT INTO UserAnswers
                          (user_id, answer_id, question_id) 
                          VALUES 
                          (?,?,?)"""

    data = (userid,answerid,questionid,)
    cursor.execute(sqlite_save_query, data)

    save_id = cursor.lastrowid

    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  
  if save_id != 0:
    save_data_set = {
        "UserAnswers_id":           save_id
    }
    return save_data_set
  else:
    raise Exception("Error saving the user answer")

def save_user_commit(username: str, user_id: int):
  save_id = 0
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
    cursor_old = sqliteConnection.cursor()

    old_user_id = None

    sqlite_select_user_query = """SELECT * from Users WHERE id = ?"""
    data_select = (user_id,)
    cursor_old.execute(sqlite_select_user_query, data_select)
    records_users = cursor_old.fetchall()

    
    for row in records_users:
      save_id = row[0]


    if save_id == 0:
      cursor_old.close()

      cursor = sqliteConnection.cursor()
      sqlite_save_query = """INSERT INTO Users
                            (id, username) 
                            VALUES 
                            (?, ?) """

      data = (user_id,username,)
      cursor.execute(sqlite_save_query, data)

      save_id = cursor.lastrowid
      cursor.close()
      sqliteConnection.commit()

  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  if save_id != 0:
    save_data_set = {
        "Users_id":           save_id
    }
    return save_data_set
  else: 
    raise Exception("Error saving the user")

def save_user_no_commit(username: str, user_id: int, sqliteConnection):
  save_id = 0
  try:
    cursor_old = sqliteConnection.cursor()

    old_user_id = None

    sqlite_select_user_query = """SELECT * from Users WHERE id = ?"""
    data_select = (user_id,)
    cursor_old.execute(sqlite_select_user_query, data_select)
    records_users = cursor_old.fetchall()

    
    for row in records_users:
      cursor_old.close()      
      return

    cursor_old.close()

    cursor = sqliteConnection.cursor()
    sqlite_save_query = """INSERT INTO Users
                          (id, username) 
                          VALUES 
                          (?, ?) """

    data = (user_id,username,)
    cursor.execute(sqlite_save_query, data)

    save_id = cursor.lastrowid
    cursor.close()

  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  if save_id != 0:
    return "User saved"
  else: 
    raise Exception("Error saving the user")


def get_answer_internal(questionid: int, userid: int):
  answers_data_set = None
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_select_answers_query = """SELECT * from UserAnswers WHERE question_id = ? and user_id = ? ORDER BY ID DESC"""

    data = (questionid,userid,)
    cursor.execute(sqlite_select_answers_query, data)

    
    records_user_answers = cursor.fetchall()

    
    for row in records_user_answers:
      answer_id   =   row[3]
    
      cursor_answers = sqliteConnection.cursor()

      sqlite_select_answers_query = """SELECT * from Answers WHERE id = ? ORDER BY ID DESC"""
      cursor_answers.execute(sqlite_select_answers_query, (answer_id,))
      records_answers = cursor_answers.fetchall()


      for row in records_answers:
        idanswer =     row[0]
        answer =       row[1]
        is_correct =   row[2]
        
        answers_data_set = {
          "id":           idanswer, 
          "answer":       answer, 
          "is_correct":   is_correct
        }

        cursor_answers.close()

    cursor.close()

  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  
  if answers_data_set:
    return answers_data_set


def get_answer(questionid, userid):
  answers_data_set = get_answer_internal(questionid, userid)
  if answers_data_set:
    return answers_data_set
  else:
    raise Exception("Error getting the user answer")

  
def get_question(question_id: int, number: int, quiz_id: int):
  question_data_set = None


  if question_id:
    sqlite_select_questions_query = """SELECT * from Questions WHERE id = ? ORDER BY ID DESC"""
    data = (question_id,)
  elif number and quiz_id:
    sqlite_select_questions_query = """SELECT * from Questions WHERE number = ? and quiz_id = ? ORDER BY ID DESC"""
    data = (number,quiz_id,)
  else:
    raise Exception("question_id or (number + quiz_id) are mandatory")

  try:

    
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
    cursor_questions = sqliteConnection.cursor()
    

    cursor_questions.execute(sqlite_select_questions_query, data)

    records_questions = cursor_questions.fetchall()

    json_question_list = []

    for row in records_questions:
      idquestion =   row[0]
      number =       row[1]
      category =     row[2]
      typeq =        row[3]
      difficulty =   row[4]
      question =     row[5]
      is_last =      row[6]

      cursor_answers = sqliteConnection.cursor()

      sqlite_select_answers_query = """SELECT * from Answers WHERE questions_id = ? ORDER BY ID DESC"""
      cursor_answers.execute(sqlite_select_answers_query, (idquestion,))
      records_answers = cursor_answers.fetchall()

      json_answers_list = []

      for row in records_answers:
        idanswer =     row[0]
        answer =       row[1]
        is_correct =   row[2]
        
        answers_data_set = {
          "id":           idanswer, 
          "answer":       answer, 
          "is_correct":   is_correct
        }

        json_answers_list.append(answers_data_set)



      question_data_set = {
        "id":           idquestion, 
        "number":       number, 
        "category":     category, 
        "type":         typeq, 
        "difficulty":   difficulty, 
        "question":     question,
        "is_last":      is_last, 
        "answers":      json_answers_list
      }

      cursor_answers.close()

    cursor_questions.close()

  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  if question_data_set is not None:
    return question_data_set
  else:
    raise Exception("Question id not found")



def get_answers(answers_id: int):
  json_answers_list = None
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3') 
    cursor_answers = sqliteConnection.cursor() 

    sqlite_select_answers_query = """SELECT * from Answers WHERE id = ? ORDER BY ID DESC"""

    cursor_answers.execute(sqlite_select_answers_query, (answers_id,))
    records_answers = cursor_answers.fetchall() 
    json_answers_list = [] 
    for row in records_answers:
      idanswer =     row[0]
      answer =       row[1]
      is_correct =   row[2]
      
      answers_data_set = {
        "id":           idanswer, 
        "answer":       answer, 
        "is_correct":   is_correct
      } 
      json_answers_list.append(answers_data_set)

    cursor_answers.close()

  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  if json_answers_list is not None:
    return json_answers_list
  else:
    raise Exception("Answer id not found")


def end_quiz(quiz_id: int, guild_id: int):
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_query = """UPDATE QUIZ SET is_running = 0 WHERE id = ? and guild_id = ?"""

    data = (quiz_id,guild_id,)
    cursor.execute(sqlite_query, data)

    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  finally:
    if sqliteConnection:
      sqliteConnection.close()
  return get_quiz_results(quiz_id, guild_id)

def end_all_quiz(guild_id: int):
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_query = """UPDATE QUIZ SET is_running = 0 WHERE guild_id = ?"""

    data = (guild_id, )
    cursor.execute(sqlite_query, data)

    sqliteConnection.commit()
    cursor.close()

  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  finally:
    if sqliteConnection:
      sqliteConnection.close()

  message = {
    "message": "all quiz ended"
  } 
  return message

def quiz_by_running(is_running: int, guild_id: int):
  json_data = []
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
    cursor_quiz = sqliteConnection.cursor()

    sqlite_select_quiz_query = """SELECT * from Quiz WHERE is_running = ? and guild_id = ? ORDER BY ID DESC"""
    cursor_quiz.execute(sqlite_select_quiz_query, (is_running,guild_id,))
    records_quiz = cursor_quiz.fetchall()
    for row in records_quiz:

      quiz_data_set = {
        "id":           row[0],
        "author":       row[1],
        "author_id":    row[2],
        "is_running":   row[3],
        "guild_id":    row[4]
      }

      json_data.append(quiz_data_set)

    
    cursor_quiz.close()
  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  finally:
    if sqliteConnection:
      sqliteConnection.close()

  return json_data