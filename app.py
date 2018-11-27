#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    print ("started processing")
    if req.get("result").get("action") == "yahooWeatherForecast":
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        print ("yql query created")
        if yql_query is None:
            print("yqlquery is empty")
            return {}
        yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
        print(yql_url)
        result = urllib.urlopen(yql_url).read()
        print("yql result: ")
        print(result)
        data = json.loads(result)
        res = makeWebhookResult(data)
    elif req.get("result").get("action") == "getBodyPart":
	data = req
	res = makeWebhookResultForGetBodyPart(data)
    elif req.get("result").get("action") == "getBotName":
	data = req
	res = makeWebhookResultForGetBotName(data)
    elif req.get("result").get("action") == "getEventTime":
	data = req
	res = makeWebhookResultForGetEventTime(data)
    elif req.get("result").get("action") == "getFood":
	data = req
	res = makeWebhookResultForGetFood(data)
    elif req.get("result").get("action") == "getHowAreYou":
	data = req
	res = makeWebhookResultForGetHowAreYou(data)
    elif req.get("result").get("action") == "getNeedSpeaker":
	data = req
	res = makeWebhookResultForGetNeedSpeaker(data)
    elif req.get("result").get("action") == "getNeedTimeSpeaker":
	data = req
	res = makeWebhookResultForGetNeedTimeSpeaker(data)
    elif req.get("result").get("action") == "getQuit":
	data = req
	res = makeWebhookResultForGetQuit(data)
    elif req.get("result").get("action") == "getSchedule":
	data = req
	res = makeWebhookResultForGetSchedule(data)
    elif req.get("result").get("action") == "getSpeakerOrderIntent":
	data = req
	res = makeWebhookResultForGetSpeakerOrderIntent(data)
    elif req.get("result").get("action") == "getSpeakers":
	data = req
	res = makeWebhookResultForGetSpeakers(data)
    elif req.get("result").get("action") == "getUst":
	data = req
	res = makeWebhookResultForGetUst(data)
    elif req.get("result").get("action") == "getWifi":
	data = req
	res = makeWebhookResultForGetWifi(data)
    else:
        return {}
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    slack_message = {
        "text": speech,
        "attachments": [
            {
                "title": channel.get('title'),
                "title_link": channel.get('link'),
                "color": "#36a64f",

                "fields": [
                    {
                        "title": "Condition",
                        "value": "Temp " + condition.get('temp') +
                                 " " + units.get('temperature'),
                        "short": "false"
                    },
                    {
                        "title": "Wind",
                        "value": "Speed: " + channel.get('wind').get('speed') +
                                 ", direction: " + channel.get('wind').get('direction'),
                        "short": "true"
                    },
                    {
                        "title": "Atmosphere",
                        "value": "Humidity " + channel.get('atmosphere').get('humidity') +
                                 " pressure " + channel.get('atmosphere').get('pressure'),
                        "short": "true"
                    }
                ],

                "thumb_url": "http://l.yimg.com/a/i/us/we/52/" + condition.get('code') + ".gif"
            }
        ]
    }

    facebook_message = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": channel.get('title'),
                        "image_url": "http://l.yimg.com/a/i/us/we/52/" + condition.get('code') + ".gif",
                        "subtitle": speech,
                        "buttons": [
                            {
                                "type": "web_url",
                                "url": channel.get('link'),
                                "title": "View Details"
                            }
                        ]
                    }
                ]
            }
        }
    }

    print(json.dumps(slack_message))

    return {
        "speech": speech,
        "displayText": speech,
        "data": {"slack": slack_message, "facebook": facebook_message},
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

def makeWebhookResultForGetBodyPart(data):
    bodypart = data.get("result").get("parameters").get("body-part")
    outcome = 'Unknown'
    if bodypart == 'mouth':
        outcome = 'm'
    elif bodypart == 'ear':
        outcome = 'e'
    elif bodypart == 'skin':
        outcome = 's'
    elif bodypart == 'nose':
        outcome = 'n'
    elif bodypart == 'eye':
        outcome = 'e'
    speech = bodypart + 'is made of'

    return {
        "speech": speech,
	"displayText": speech,
	"source": "webhookdata"
    }

def makeWebhookResultForGetBotName(data):
    speech = 'I am Kitty Bot!'
    return {
	"speech": speech,
	"displayText": speech,
	"source": "webhookdata"
    }

def makeWebhookResultForGetEventTime(data):
    speech = 'The event goes on from 10 a.m. to 5 p.m.'
    return {
	"speech": speech,
	"displayText": speech,
	"source": "webhookdata"   
    }

def makeWebhookResultForGetFood(data):
    speech = 'The food is served downstairs at the cafe'
    return {
	"speech": speech,
	"displayText": speech,
	"source": "webhookdata"   
    }

def makeWebhookResultForGetHowAreYou(data):
    speech = 'Im here answering all your questions. What do you think?'
    return {
	"speech": speech,
	"displayText": speech,
	"source": "webhookdata"   
    }

def makeWebhookResultForGetNeedSpeaker(data):
    speakername = data.get("result").get("parameters").get("SpeakerName")
    outcome = 'Unknown'
    if speakername == 'vineet':
        outcome = 'Vineet Baburaj is presenting at 11 a.m.'
    elif speakername == 'ashok':
        outcome = 'Ashok Nair is presenting at 12 p.m.'
    elif speakername == 'simsar':
        outcome = 'Simsar is presenting at 12:30 p.m.'
    elif speakername == 'rafi':
        outcome = 'Rafi is presenting tomorrow at 12:30 p.m.'
    speech = outcome

    return {
        "speech": speech,
	"displayText": speech,
	"source": "webhookdata"
    }

def makeWebhookResultForGetNeedTimeSpeaker(data):
    speakertime = data.get("result").get("parameters").get("TIME_SPEAKER")
    eventday = data.get("result").get("parameters").get("eventDays")
    outcome = 'Unknown'
    if speakertime == 'eleven':
        outcome = 'Vineet Baburaj is presenting at 11 a.m.'
    elif speakertime == 'twelve':
        outcome = 'Ashok Nair is presenting at 12 p.m.'
    elif speakertime == 'twelve_thirty':
        outcome = 'Simsar is presenting at 12:30 p.m.'
    elif speakertime == 'twelve_thirty':
        outcome = 'Rafi is presenting tomorrow at 12:30 p.m.'
    speech = outcome

    return {
        "speech": speech,
	"displayText": speech,
	"source": "webhookdata"
    }

def makeWebhookResultForGetQuit(data):
    speech = 'Bye! It was nice talking to you!'
    return {
	"speech": speech,
	"displayText": speech,
	"source": "webhookdata"
    }

def makeWebhookResultForGetSchedule(data):
    speech = 'There will be a talk at 11 a.m. by Vineet Baburaj followed by a presentation by Mr. Ashok Nair at 12 p.m. and another presentation by Simsar at 12:30 p.m.'
    return {
	"speech": speech,
	"displayText": speech,
	"source": "webhookdata"
    }

def makeWebhookResultForGetSpeakerOderIntent(data):
    speakeroder = data.get("result").get("parameters").get("SpeakerOder")
    outcome = 'Unknown'
    if speakerorder == 'first':
        outcome = 'Vineet Baburaj is the fist speaker presenting at 11 a.m.'
    elif speakerorder == 'second':
        outcome = 'Ashok Nair is the second speaker presenting at 12 p.m.'
    elif speakerorder == 'third':
        outcome = 'Simsar is the third speaker presenting at 12:30 p.m.'
    speech = outcome
    return {
	"speech": speech,
	"displayText": speech,
	"source": "webhookdata"
    }
    
def makeWebhookResultForGetSpeakers(data):
    speech = 'The speakers presenting today are Vineet, Ashok and Simsar!'
    return {
	"speech": speech,
	"displayText": speech,
	"source": "webhookdata"
    }

def makeWebhookResultForGetUst(data):
    speech = 'I was bult in UST Global. It is an American multinational provider of Digital, IT services and solutions.'
    return {
	"speech": speech,
	"displayText": speech,
	"source": "webhookdata"
    }

def makeWebhookResultForGetWifi(data):
    speech = 'Please get help from an UST Global employee to connect to the wifi.'
    return {
	"speech": speech,
	"displayText": speech,
	"source": "webhookdata"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port %d" % port)

app.run(debug=False, port=port, host='0.0.0.0')
