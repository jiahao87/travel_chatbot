from flask import Flask, request
from travel_planner_chatbot import reply_message
import json
import requests
import urllib.request


app = Flask(__name__)

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = 'a8bf030ae95c83eaa9775d0dd7e7540f'# <paste your verify token here>
PAGE_ACCESS_TOKEN = 'EAAIee6jvZBsQBALtYWPYiC4EUnY8ZAOrLQwaHqVgqplN9XfOyitsy3DIaWZCF7zcZAAKs9cyrYs9BCwZC2AIeUwdcgMPjZBi2bjf9ZC6SPDknM9TL8HWmdDZCws8pJR5kGoWjZAZCNWwxZCfwHecZBWLG4hpaQQtCTLgRmWKU3CgAso7HV7PoXEndlQy8m1w9wYeNSMZD'# paste your page access token here>"


def get_name(sender):
    profile_link = "https://graph.facebook.com/{}?fields=first_name&access_token={}".format(sender, PAGE_ACCESS_TOKEN)
    with urllib.request.urlopen(profile_link) as url:
        name = json.loads(url.read().decode())
        name = name['first_name']
        return name


def get_bot_response(message):
    """This function returns a response to what the user said."""
    reply, type, state = reply_message(message)
    return reply, type, state


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"


def respond(sender, message):
    """Formulate a response to the user and
    pass it on to a function that sends it."""
    response, msg_type, state = get_bot_response(message)
    if state == 0:
        send_message(sender, "Hi {}!".format(get_name(sender)))
        send_message(sender, response)
        send_start(sender)
    else:
        if msg_type == "text":
            send_message(sender, response)
        elif msg_type == "url":
            send_url(sender, response)
        elif msg_type == "generic":
            send_generic_template(sender, response)
        elif msg_type == "quick":
            send_quick_replies(sender, response)


def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))


def is_user_postback(message):
    """Check if the message is a message from the user"""
    return (message.get('postback') and
            message['postback'].get('payload'))


@app.route("/webhook",methods=['GET','POST'])
def listen():
    """This is the main function flask uses to
    listen at the `/webhook` endpoint"""
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        payload = request.json
        event = payload['entry'][0]['messaging']
        for x in event:
            if is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']
                respond(sender_id, text)
            elif is_user_postback(x):
                text = x['postback']['payload']
                sender_id = x['sender']['id']
                respond(sender_id, text)
        return "ok"


def send_message(recipient_id, text):
    """Send a response to Facebook"""
    payload = {
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }

    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }

    response = requests.post(
        FB_API_URL,
        params=auth,
        json=payload
    )

    return response.json()


def send_url(recipient_id, url):

    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": url
                }
            }}
    })

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    headers = {
        "Content-Type": "application/json"
    }

    r = requests.post(FB_API_URL,
                      params=params,
                      headers=headers,
                      data=data)


def send_generic_template(recipient_id, elements):
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": elements
                }
            }}
    })

    params = {"access_token": PAGE_ACCESS_TOKEN}

    headers = {"Content-Type": "application/json"}

    r = requests.post(FB_API_URL,
                      params=params,
                      headers=headers,
                      data=data)


def send_start(recipient_id):
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                        "title": "Gardens by the Bay",
                        "image_url": "https://res.klook.com/images/fl_lossy.progressive,q_65/c_fill,w_1295,h_720,f_auto/w_80,x_15,y_15,g_south_west,l_klook_water/activities/b26c5529-Gardens-by-the-Bay/GardensbytheBayTicketSingapore.jpg",
                        "subtitle": "Gardens by the Bay is a showpiece of horticulture and garden artistry in the city",
                        "buttons": [
                            {
                                "type": "postback",
                                "title": "Tell me more",
                                "payload": "tell_me_more gardens by the bay"
                            }
                        ]
                        },
                        {
                            "title": "Universal Studios Singapore",
                            "image_url": "http://blog.raynatours.com/wp-content/uploads/2016/12/Universal-Studios-in-Singapore.jpg",
                            "subtitle": "Universal Studios is a theme park located within Resorts World Sentosa on Sentosa Island",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Tell me more",
                                    "payload": "tell_me_more universal studios"
                                }
                            ]
                        },
                        {
                            "title": "S.E.A. Aquarium",
                            "image_url": "https://media.karousell.com/media/photos/products/2018/07/19/sea_aquarium_tickets_1532015525_d6347f03.jpg",
                            "subtitle": "Large aquarium & resort featuring 800 species of marine life",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Tell me more",
                                    "payload": "tell_me_more aquarium"
                                }
                            ]
                        },
                        {
                            "title": "Jewel Changi Airport",
                            "image_url": "https://static.businessinsider.sg/2019/03/Jewel-Changi-Airport-image-1.jpg",
                            "subtitle": "Jewel is an airport mall with world's tallest indoor waterfall",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Tell me more",
                                    "payload": "tell_me_more jewel"
                                }
                            ]
                        },
                        {
                            "title": "Singapore Zoo",
                            "image_url": "http://ttgasia.2017.ttgasia.com/wp-content/uploads/sites/2/2018/04/Singapore-Zoo.jpg",
                            "subtitle": "Set in a rainforest environment, Singapore Zoo adopts an open concept",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Tell me more",
                                    "payload": "tell_me_more zoo"
                                }
                            ]
                        },
                    ]
                }
            }}
    })

    params = {"access_token": PAGE_ACCESS_TOKEN}

    headers = {"Content-Type": "application/json"}

    r = requests.post(FB_API_URL,
                      params=params,
                      headers=headers,
                      data=data)


def send_quick_replies(recipient_id, text):

    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {
            "text": text,
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "Indoor",
                    "payload": "find_activity indoor"
                },
                {
                    "content_type": "text",
                    "title": "Outdoor",
                    "payload": "find_activity outdoor"
                },
                {
                    "content_type": "text",
                    "title": "Shopping",
                    "payload": "find_activity shopping"
                },
                {
                    "content_type": "text",
                    "title": "Scenic",
                    "payload": "find_activity scenic"
                },
                {
                    "content_type": "text",
                    "title": "Nature",
                    "payload": "find_activity nature"
                },
                {
                    "content_type": "text",
                    "title": "Heritage",
                    "payload": "find_activity heritage"
                }
            ]
    }
    })

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    headers = {
        "Content-Type": "application/json"
    }

    r = requests.post(FB_API_URL,
                      params=params,
                      headers=headers,
                      data=data)

