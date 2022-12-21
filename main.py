from flask import Flask, request
from response import ChatBot, fliterSubject
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)


@app.route('/bot', methods=['POST'])
def bot():
  incoming_msg = request.values.get('Body', '').lower()
  sub = fliterSubject(incoming_msg)
  print(sub)
  print(incoming_msg)
  resp = MessagingResponse()
  msg = resp.message()
  chatbot_resp = ChatBot(incoming_msg)
  print(chatbot_resp["tag"])
  msg.body(chatbot_resp["response"])
  return str(resp)


@app.route('/response', methods=['GET'])
def response():
  query = request.args.get("q")
  resp = ChatBot(query)
  return resp


app.run(host='0.0.0.0', port=81)
