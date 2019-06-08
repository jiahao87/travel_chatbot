# travel_chatbot
Travel chatbot for day trips in Singapore

The purpose of this chatbot is to help travellers plan their day trips in Singapore.

![chatbot screenshot](https://raw.githubusercontent.com/jiahao87/travel_chatbot/master/images/chatbot_screenshot.PNG)

The chatbot uses messenger as platform and has the following functions:<br />

1. Provide travel suggestions (up to 5 places) based on natural language query
2. Fetch weather forecast to auto-suggest indoor places instead (work-in-progress)
3. Q&A on selected travel suggestion (work-in-progress)
<br />
To start chatbot,<br /> 
1. Input the page access token and verify token in server.py
<br />
2. Run the server.py files by keying in command prompt "set FLASK_APP=server.py flask run"
<br />
<br />
References:<br />
1. https://medium.com/@manoveg/multi-class-text-classification-with-probability-prediction-for-each-class-using-linearsvc-in-289189fbb100
<br />
2. https://www.datacamp.com/community/tutorials/facebook-chatbot-python-deploy
<br />
3. https://developers.facebook.com/docs/messenger-platform/send-messages
