from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import text2emotion as te
import pickle
import string

app = Flask(__name__)

try:
    import cPickle as pickle
except ImportError: 
    import pickle
import re
with open('Emoji_Dict.p', 'rb') as fp:
    Emoji_Dict = pickle.load(fp)
Emoji_Dict = {v: k for k, v in Emoji_Dict.items()}


def convert_emojis_to_word(text):
    for emot in Emoji_Dict:
        text = re.sub(r'('+emot+')', "_".join(Emoji_Dict[emot].replace(","," ").replace(":"," ").split()), text)
    return text
 

@app.route("/")
def hello():
    return "Bot Started"

@app.route("/sms", methods=['POST'])

def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    tfidf = pickle.load(open('vectorizer.pkl','rb'))
    model = pickle.load(open('model.pkl','rb'))
    msg = request.form.get('Body')
    transformed_sms = convert_emojis_to_word(msg)
    transformed_sms = transformed_sms.replace("_", " ")
    vector_input = tfidf.transform([transformed_sms])
    result = model.predict(vector_input)[0]

    sentiment_dict = te.get_emotion(transformed_sms)
    sentiment = max(zip(sentiment_dict.values(), sentiment_dict.keys()))[1]
    # Create reply
    resp = MessagingResponse()
    if result == 1:
        spamRes = "Spam"
        print(transformed_sms)
        resp.message("Message is "+spamRes+". And, the sentiment is: "+sentiment)
    else:
        spamRes = "Not Spam"
        print(transformed_sms)
        resp.message("Message is: "+spamRes+" And, the sentiment is: "+sentiment)
    

    return str(resp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)