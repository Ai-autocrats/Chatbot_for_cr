from nltk.stem import WordNetLemmatizer
import nltk
import json
import numpy as np
import pickle
import random
from tensorflow.keras.models import load_model
import os

nltk.download('punkt')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

basedir = '.'
model = load_model(f'{basedir}/bot.h5')
intents = json.loads(open(f'{basedir}/intents.json').read())
words = pickle.load(open(f'{basedir}/words.pkl', 'rb'))
classes = pickle.load(open(f'{basedir}/classes.pkl', 'rb'))


def clean_up_sentence(sentence):
  sentence_words = nltk.word_tokenize(sentence)
  sentence_words = [
    lemmatizer.lemmatize(word.lower()) for word in sentence_words
  ]
  return sentence_words


def bow(sentence, words, show_details=True):
  # tokenize the pattern
  sentence_words = clean_up_sentence(sentence)
  # bag of words - matrix of N words, vocabulary matrix
  bag = [0] * len(words)
  #enumerate([3.1,2,9,4])=>[(0,3) ,(1,1) ,(2,2) , (3,9) ,(4,4)]

  for s in sentence_words:
    for i, w in enumerate(words):
      if w == s:
        # assign 1 if current word is in the vocabulary position
        bag[i] = 1

  return (np.array(bag))


def predict_class(sentence, model):
  # filter out predictions below a threshold
  p = bow(sentence, words, show_details=False)
  res = model.predict(np.array([p]))[0]
  ERROR_THRESHOLD = 0.6

  results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

  # sort by strength of probability
  results.sort(key=lambda x: x[1], reverse=True)
  # print(results)
  return_list = []
  #     for r in results:
  #         return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
  try:
    if results[0]:
      for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    else:
      return_list.append({"intent": 'noanswer', "probability": '1'})
  except:
    return_list.append({"intent": 'noanswer', "probability": '1'})
  # print(return_list)
  return return_list


def getResponse(ints, intents_json):
  result = 'sorry I could not understand'
  tag = ints[0]['intent']
  # print(tag)
  list_of_intents = intents_json['intents']
  for i in list_of_intents:
    if (i['tag'] == tag):
      result = random.choice(i['responses'])
      break
  return result, tag


def prediction(msg):
  ints = predict_class(
    msg, model
  )  # [{"intent": "PhyNotes" , probablity : 0.9} , {"intent": "PhyNotes" , probablity : 0.9}]
  res, tag = getResponse(ints, intents)
  result = {"response": res, "tag": tag}
  # if float(ints[0]['probability']):
  # result = {"response": res, "tag": tag}
  # else:
  #     result = {
  #         "response": "sorry I could not understand what you are saying",
  #         "tag": "couldnotunderstand"
  #     }
  return result


##### response #####
def ChatBot(query):

  try:
    Bot_Response = prediction(query)

  except Exception as e:
    Bot_Response = {'response': e, 'tag': "error"}
    # print(e)

  return Bot_Response


# os.system('clear')
# while True:
#     x = input('user : ')
#     if x.lower() in ['exit', 'quit', 'close']:
#         exit()
#     print('Bot : ' + str(ChatBot(x.lower())['response']))


def fliterSubject(string):
  sub = {"phy": ["physics", "phy", "phys"], "chem": ["chem", "chemistry"]}
  for key, vals in zip(sub.keys(), sub.values()):
    for val in vals:
      if string.find(val) != -1:
        return key
  return ""


def update(db, cname, name, field, value):
  if cname == "examdates":
    try:
      result = db.examdates.update_one({"name": name}, {"$set": {field: value}})
      return f"{field} updated tp {value} !!"
    except:
      return "Erorr"


def getDetails(db, cname, name, field):
  if cname == "examdates":
    value = dict(db.examdates.find_one({"name": name}))[field]
    return value
