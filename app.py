import os
import ssl
import certifi
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request
from functions import draft_email

# Set the SSL_CERT_FILE environment variable to use certifi's certificate
os.environ['SSL_CERT_FILE'] = certifi.where()

# Create an SSL context using certifi
ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Set Slack API credentials
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_USER_ID = os.environ["SLACK_BOT_USER_ID"]

app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

# Initialize the Flask app
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

def get_bot_user_id():
    try:
        slack_client = WebClient(token=SLACK_BOT_TOKEN, ssl=ssl_context)
        response = slack_client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        print(f"Error: {e}")

def my_function(text):
    response = text.upper()
    return response

@app.event("app_mention")
def handle_mentions(body, say):
    text = body["event"]["text"]

    mention = f"<@{SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()

    say("Sure, I'll get right on that!")
    response = draft_email(text)
    say(response)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run()