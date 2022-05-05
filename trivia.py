import os
import requests
import sqlite3
import traceback
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TMP_DIR = os.environ.get("TMP_DIR")
TRIVIA_API = os.environ.get("TRIVIA_API")

def create_quiz(author, author_id, amount, category, difficulty, typeq):
  if not author:
    raise Exception("Author is mandatory")
  if not author_id:
    raise Exception("Author id is mandatory")
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
  return create_new_quiz(author, author_id, response.json())

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
            author_id INTEGER NOT NULL
        ); """

    cursor.execute(sqlite_create_quiz_query)    
    
    
    sqlite_create_questions_query = """ CREATE TABLE IF NOT EXISTS Questions(
            id INTEGER PRIMARY KEY,
            number INTEGER NOT NULL,
            category VARCHAR(255) NOT NULL,
            type VARCHAR(255) NOT NULL,
            difficulty VARCHAR(255) NOT NULL,
            question INTEGER NOT NULL,
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

def create_new_quiz(author, author_id, content): 
  quiz_id = 0 
  try:
    sqliteConnection = sqlite3.connect(TMP_DIR+'trivia.sqlite3')
    cursor = sqliteConnection.cursor()

    sqlite_insert_quiz_query = """INSERT INTO Quiz
                          (author, author_id) 
                           VALUES 
                          (?, ?)"""

    data_quiz_tuple = (author,author_id,)

    cursor.execute(sqlite_insert_quiz_query, data_quiz_tuple)

    quiz_id = cursor.lastrowid

    numbercounter = 1

    for result in content['results']:
      sqlite_insert_questions_query = """INSERT INTO Questions
                            (number, category, type, difficulty, question, quiz_id) 
                            VALUES 
                            (?, ?, ?, ?, ?, ?)"""
      data_questions_tuple = (numbercounter, result['category'], result['type'], result['difficulty'], result['question'], quiz_id)
      cursor.execute(sqlite_insert_questions_query, data_questions_tuple)

      question_id = cursor.lastrowid

      sqlite_insert_answers_query = """INSERT INTO Answers
                            (answer, is_correct, questions_id) 
                            VALUES 
                            (?, ?, ?)"""
      data_correct_answer_tuple = (result['correct_answer'], 1, question_id)
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

def get_quiz(quiz_id):
  quiz_data_set = None
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
        "answers":      json_answers_list
      }
      json_question_list.append(question_data_set)

      cursor_answers.close()

    cursor_questions.close()

    quiz_data_set = {
        "id":           quiz_id, 
        "author":       author, 
        "questions":    json_question_list
    }

  except sqlite3.Error as error:
    print("SQLITE Error: ", error)
    raise Exception(str(error))
  finally:
    if sqliteConnection:
      sqliteConnection.close()

  return quiz_data_set
  if quiz_data_set is not None:
    return quiz_data_set
  else:
    raise Exception("Quiz id not found")


def save_answer(questionid: int, answerid: int, userid: int, username: str):
  

  answers_data_set = get_answer_internal(questionid, userid)

  if(answers_data_set is not None):
    save_data_set = {
        "UserAnswers_id": answers_data_set['id']
    }
    return save_data_set


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
  try:

    if question_id:
      sqlite_select_questions_query = """SELECT * from Questions WHERE id = ? ORDER BY ID DESC"""
      data = (question_id,)
    elif number:
      sqlite_select_questions_query = """SELECT * from Questions WHERE number = ? and quiz_id = ? ORDER BY ID DESC"""
      data = (number,quiz_id,)
    else:
      raise Exception("question_id or (number + quiz_id) are mandatory")

    
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