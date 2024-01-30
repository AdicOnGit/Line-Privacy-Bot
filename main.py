import json
import logging
from fastapi import FastAPI, Request, Response, status
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage,
    ReplyMessageRequest
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    JoinEvent,
    LeaveEvent
)
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Setup logging
logger = logging.getLogger("uvicorn.error")
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

configuration = Configuration(access_token=os.environ.get("ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))

GROUP_ID_FILE = "group_id.txt"
AUTHENTICATED_USERS_FILE = "authenticated_users.json"
PASSWORD = os.environ.get("PASSWORD")

# Function to add a new group ID to the file


def add_group_id(group_id):
    with open(GROUP_ID_FILE, "a") as file:
        file.write(group_id + "\n")

# Function to remove a group ID from the file


def remove_group_id(group_id):
    with open(GROUP_ID_FILE, "r") as file:
        lines = file.readlines()
    with open(GROUP_ID_FILE, "w") as file:
        for line in lines:
            if line.strip("\n") != group_id:
                file.write(line)

# Function to get all group IDs from the file


def get_group_ids():
    with open(GROUP_ID_FILE, "r") as file:
        return [line.strip() for line in file.readlines()]

# Function to authenticate a user


def authenticate_user(user_id, password):
    if password == PASSWORD:
        with open(AUTHENTICATED_USERS_FILE, "r+") as file:
            try:
                users = json.load(file)
            except json.JSONDecodeError:
                users = {}
            users[user_id] = True
            file.seek(0)
            json.dump(users, file)
            return True
    return False

# Function to check if a user is authenticated


def is_user_authenticated(user_id):
    try:
        with open(AUTHENTICATED_USERS_FILE, "r") as file:
            users = json.load(file)
            return users.get(user_id, False)
    except (FileNotFoundError, json.JSONDecodeError):
        return False


@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get('X-Line-Signature')
    body = await request.body()

    try:
        handler.handle(body.decode('utf-8'), signature)
    except InvalidSignatureError as e:
        logger.info(f"Invalid Signature Error: {e}")
        return Response(content='Invalid signature.', status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.info(f"Exception: {e}")
        return Response(content='Error processing the request.', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(content='OK', status_code=status.HTTP_200_OK)


@handler.add(JoinEvent)
def handle_join(event):
    if hasattr(event.source, 'type') and event.source.type == 'group':
        group_id = event.source.group_id
        add_group_id(group_id)


@handler.add(LeaveEvent)
def handle_leave(event):
    if hasattr(event.source, 'type') and event.source.type == 'group':
        group_id = event.source.group_id
        remove_group_id(group_id)


# Temporary storage for users in the authentication process
authentication_pending_users = {}


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text

    # Check if the user is already authenticated
    if is_user_authenticated(user_id):
        # Process the message from the authenticated user
        process_authenticated_user_message(text, event)
    elif user_id in authentication_pending_users:
        # The user is in the process of authentication
        handle_authentication_attempt(user_id, text, event)
    elif text == "knock knock open the door":
        # Start the authentication process for a new user
        initiate_authentication(user_id, event)
    # If the user is not authenticated and not in the process, do not respond


def process_authenticated_user_message(text, event):
    if hasattr(event.source, 'type') and event.source.type == 'user':
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            gid_already_sent = []
            for gid in get_group_ids():
                if gid not in gid_already_sent:  # Avoid sending back to the same group
                    try:
                        line_bot_api.push_message(
                            PushMessageRequest(
                                to=gid,
                                messages=[TextMessage(text=text)]
                            )
                        )
                        gid_already_sent.append(gid)
                    except Exception as e:
                        logger.info(f"Exception in message forwarding: {e}")


def handle_authentication_attempt(user_id, text, event):
    authenticated = authenticate_user(user_id, text)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if authenticated:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="You are now authenticated. Welcome!")]
                )
            )
        else:
            # Notify of incorrect password and keep user in pending state
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="Incorrect password!!!")]
                )
            )
        del authentication_pending_users[user_id]


def initiate_authentication(user_id, event):
    # Mark user as pending authentication and ask for the password
    authentication_pending_users[user_id] = True
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="Please enter the password.")]
            )
        )
