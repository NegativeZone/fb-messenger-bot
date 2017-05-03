import os
import sys
import json

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    set_response(sender_id, recipient_id, message_text)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

def set_response(sender_id, recipient_id, message_text):
    words = message_text.split()
    for word in words:
        if word.lower() == "hi" or word.lower() == "hello":
            send_message(recipient_id, "Hello there! I am Woofer, the core of Amplyf.ai's conversation engine.")
        if word.lower() == "woofer":
            send_message(recipient_id, "It seems you already know who I am! Welcome back!")
    for word in words:
        if word.lower() == "tell":
            for word_2 in words:
                if word_2.lower() == "about":
                    for word_3 in words:
                        if word_3.lower() == "you":
                            send_message(recipient_id, "I am Woofer, an artificial intelligence designed to have human-like conversations about whatever you can imagine!")
                            send_message(recipient_id, "For now, I am programmed to showcase my skills and abilities.")
                            send_message(recipient_id, "I hope you think I'm cool! I think I'm cool!")
                        if word_3.lower() == "amplyf.ai" or word_3.lower() == "amplyfai":
                            send_message(recipient_id, "Amplyf.ai is an Artificial Intelligence startup by Anuroop Bisaria, my creator and an all-around cool dude.")
                            send_message(recipient_id, "We make customized artificial intelligences that hold conversations that suit your needs, all with Woofer at their core.")
                            send_message(recipient_id, "Hey wait, that's me!")
                elif word_2.lower() == "joke":
                    send_message(recipient_id, "What do you call an underwater chatbot? A sub-woofer!")

def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
