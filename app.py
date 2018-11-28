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

import requests

from IPython.display import HTML

def processRequest(req):
    print ("started processing")
    if req.get("result").get("action") == "webSearch":
        baseurl = "https://api.cognitive.microsoft.com/bing/v7.0/search"
        wql_query = makeWqlQuery(req)
        print ("wql query created")
        if wql_query is None:
            print("wqlquery is empty")
            return {}
        headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
	params  = {"q": search_term, "textDecorations":True, "textFormat":"HTML"}
	response = requests.get(search_url, headers=headers, params=params)
	response.raise_for_status()
	search_results = response.json()
        print("yql result: ")
        print(result)
        data = json.loads(search_result)
        res = makeWebhookSearchResult(data)
    else:
        return {}
    return res

        

def makeWqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    webSearchParam = parameters.get("q")
    if webSearchParam is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookSearchResult(data):
    rows = "\n".join(["""<tr>
                           <td><a href=\"{0}\">{1}</a></td>
                           <td>{2}</td>
                         </tr>""".format(v["url"],v["name"],v["snippet"]) \
                      for v in search_results["webPages"]["value"]])
    HTML("<table>{0}</table>".format(rows))
    print("Response:")
    print(rows)

    return {
        "speech": rows,
	"displayText": rows,
	"source": "webhookdata"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port %d" % port)

app.run(debug=False, port=port, host='0.0.0.0')
