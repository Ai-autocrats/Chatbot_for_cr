from flask import Flask, request, current_app, g
from response import ChatBot, fliterSubject, update, getDetails
from twilio.twiml.messaging_response import MessagingResponse
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo


def get_db():
  """
    Configuration method to return db instance
    """
  db = getattr(g, "_database", None)

  if db is None:

    db = g._database = PyMongo(current_app).db

  return db


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)

app = Flask(__name__)
CODE = "code123"


@app.route('/bot', methods=['POST'])
def bot():
  incoming_msg = request.values.get('Body', '').lower()
  sub = fliterSubject(incoming_msg)
  print(sub)
  print(incoming_msg)
  resp = MessagingResponse()
  msg = resp.message()
  if incoming_msg.startswith("update"):
    cmd, cname, name, field, value, code = incoming_msg.split("-")
    if code != CODE:
      msg.body("Invalid Code!")
      return str(resp)
    msg.body(update(db, cname, name, field, value))
    return str(resp)

  chatbot_resp = ChatBot(incoming_msg)
  print(chatbot_resp["tag"])

  if chatbot_resp["tag"] == "exams":
    date = getDetails(db, "examdates", "mse1", "date")
    msg.body(chatbot_resp["response"] + "\n your mse date is " + date)
    return str(resp)

  msg.body(chatbot_resp["response"])
  return str(resp)


@app.route('/response', methods=['GET'])
def response():
  '''
  update mse1 date "12/10/22 to 15/10/22" CODE123
  update sem1 date "12/10/22 to 15/10/22" CODE123
  '''
  string = 'update-exams-mse1-date-12/10/22 to 15/10/22-code123'

  cmd, cname, name, field, value, code = string.split("-")

  # result = db.exams.update_one({"name": "mse1"}, )
  # notes = db.notes.find()
  # date = db.dates.find_one({"key": "mse"})
  #print(date)
  # for note in notes:
  #   # print(dict(note)["phy"])
  #   # query = request.args.get("q")
  #   # resp = ChatBot(query)

  return "hello"  #dict(date)["date"]


app.config['DEBUG'] = True
app.config['MONGO_URI'] =""
app.run(host='0.0.0.0', port=81)
