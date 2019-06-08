import re
import random
import urllib.request
import json
import numpy as np
from datetime import date
import joblib
import sqlite3


today = date.today()

intent_model = joblib.load('intent_classification.pkl')
count_vect = joblib.load('count_vect.pkl')
tf_transformer = joblib.load('tf_transformer.pkl')
labels = ['find_activity_type', 'tell_me_more']


def fetch_weather_forecast(today_date):
    weather_api = "https://api.data.gov.sg/v1/environment/24-hour-weather-forecast?date={}".format(today_date)
    with urllib.request.urlopen(weather_api) as url:
        weather = json.loads(url.read().decode())
        forecast = weather['items'][0]['periods'][0]['regions']
        return forecast


#weather_forecast = fetch_weather_forecast(today)


def reply_message(message):
    if match_intent(message) == 'greet':
        reply = respond(message)
        type = 'text'
        state = 0
    elif match_intent(message):
        reply = respond(message)
        type = 'text'
        state = 3
    elif message.lower() in activity_type.keys():
        activity = find_activity_type(message.lower())
        reply = combine_elements(activity)
        type = 'generic'
        state = 1
    elif message[:12] == "tell_me_more":
        reply = tell_me_more(message)
        type = "text"
        state = 1
    elif intent_classification([message]) == 'find_activity_type':
        if find_activity_type(message) is not None:
            activity = find_activity_type(message)
            reply = combine_elements(activity)
            type = 'generic'
            state = 1
        else:
            reply = "Sorry, I do not quite understand what activities you are finding. \n\n" \
                    "Could you choose one area below instead?"
            type = 'quick'
            state = 1
    else:
        reply = "Sorry, I do not quite understand what you are asking. \n\n" \
                "Would you like to choose an area below to get started?"
        type = 'quick'
        state = 1
    return reply, type, state


keywords = {'greet': ['hello', 'hi', 'hey', 'yo', 'greeting','whats up', 'gd morning', 'good morning', 'gd afternoon',
                      'good afternoon', 'gd evening', 'good evening', 'hi there'],
            'goodbye': ['bye', 'farewell', 'goodbye', 'see you', 'see ya'],
            'thanks': ['thank', 'thx', 'thks']
            }

responses = {'greet': ["I'm Zapedo, your travel planner for day trip in Singapore. "
                       "Here are 5 suggestions for you. Feel free to also ask me for other suggestions, e.g., shopping"],
             'goodbye': ['Have a good trip :)', 'Goodbye!', 'Enjoy your trip :)'],
             'thanks': ['You are welcome', 'Thank you too']
             }

# Define a dictionary of patterns
patterns = {}

# Iterate over the keywords dictionary
for intent, keys in keywords.items():
    # Create regular expressions and compile them into pattern objects
    patterns[intent] = re.compile('|'.join(keys))


# Define a function to find the intent of a message
def match_intent(message):
    matched_intent = None
    for intent, pattern in patterns.items():
        # Check if the pattern occurs in the message
        if re.search(pattern, message):
            matched_intent = intent
    return matched_intent


# Define a respond function
def respond(message):
    # Call the match_intent function
    intent = match_intent(message)
    # Fall back to the default response
    key = "default"
    if intent in responses:
        key = intent
    return random.choice(responses[key])


# Use svm model to classify intent
def intent_classification(message):
    p_count = count_vect.transform(message)
    p_tfidf = tf_transformer.transform(p_count)
    prob = intent_model.predict_proba(p_tfidf)
    if np.max(prob) > 0.7:
        intention = labels[int(np.argmax(prob))]
    else:
        intention = 'others'
    return intention


activity_type = {'indoor': ['indoor'],
                 'outdoor': ['outdoor'],
                 'shopping': ['shopping', 'shop', 'buy', 'souvenir', 'gift'],
                 'heritage': ['culture', 'museum'],
                 'scenic': ['scenic', 'view', 'scenery'],
                 'nature': ['nature', 'greenery']
            }

# Define a dictionary of patterns
activity_keywords = {}

# Iterate over the keywords dictionary
for act_type, keys in activity_type.items():
    # Create regular expressions and compile them into pattern objects
    activity_keywords[act_type] = re.compile('|'.join(keys))


# if intention is to find suggestions for activity type, then find out activity type
def find_activity_type(message):
    activity = None
    for act_type, pattern in activity_keywords.items():
        # Check if the pattern occurs in the message
        if re.search(pattern, message):
            activity = act_type
    return activity


def query_criteria(activity):
    criteria = {}
    if activity == 'indoor':
        criteria['indoor'] = 1
    elif activity == 'outdoor':
        criteria['outdoor'] = 1
    elif activity == 'shopping':
        criteria['shopping'] = 1
    elif activity == 'heritage':
        criteria['heritage'] = 1
    elif activity == 'scenic':
        criteria['scenic'] = 1
    elif activity == 'nature':
        criteria['nature'] = 1
    return criteria


# Define find_hotels()
def find_places(criteria):
    # Create the base query
    query = 'SELECT * FROM places'
    # Add filter clauses for each of the parameters
    if len(criteria) > 0:
        filters = ["{}=?".format(k) for k in criteria]
        query += " WHERE " + " AND ".join(filters)
    # Create the tuple of values
    t = tuple(criteria.values())

    # Open connection to DB
    conn = sqlite3.connect("travel_places.db")
    # Create a cursor
    c = conn.cursor()
    # Execute the query
    c.execute(query, t)
    # Return the results
    return c.fetchall()


def combine_elements(activity):
    criteria = query_criteria(activity)
    results = find_places(criteria)
    elements = []
    for result in results[:5]:
        element = {}
        element['title'] = result[1]
        element['image_url'] = result[2]
        element['subtitle'] = result[3]
        element['buttons'] = [{"type": "postback", "title": "Tell me more", "payload": result[4]}]
        elements.append(element)
    return elements


def tell_me_more(message):
    criteria = {'payload': message}
    results = find_places(criteria)
    description = results[0][5]
    return description

