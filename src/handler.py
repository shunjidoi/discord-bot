import json
import os
import boto3

import requests
from nacl.signing import VerifyKey

DISCORD_ENDPOINT = os.getenv('DISCORD_ENDPOINT')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
APPLICATION_ID = os.getenv('APPLICATION_ID')
APPLICATION_PUBLIC_KEY = os.getenv('APPLICATION_PUBLIC_KEY')
COMMAND_GUILD_ID = os.getenv('COMMAND_GUILD_ID')

verify_key = VerifyKey(bytes.fromhex(APPLICATION_PUBLIC_KEY))


def registerCommands():
    endpoint = f"{DISCORD_ENDPOINT}/applications/{APPLICATION_ID}/guilds/{COMMAND_GUILD_ID}/commands"
    print(f"registering commands: {endpoint}")

    commands = [
        {
            "name": "start",
            "description": "server will start",
            "options": []
        },
        {
            "name": "stop",
            "description": "server will stop",
            "options": []
        }
    ]

    headers = {
        "User-Agent": "discord-slash-commands-helloworld",
        "Content-Type": "application/json",
        "Authorization": f"Bot {DISCORD_TOKEN}"
    }

    for c in commands:
        requests.post(endpoint, headers=headers, json=c).raise_for_status()


def verify(signature: str, timestamp: str, body: str) -> bool:
    try:
        verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
    except Exception as e:
        print(f"failed to verify request: {e}")
        return False

    return True


def defer(interaction_id, interaction_token, text):
    # https://discord.com/developers/docs/interactions/receiving-and-responding#responding-to-an-interaction
    endpoint = f"{DISCORD_ENDPOINT}/interactions/{interaction_id}/{interaction_token}/callback"
    json = {
        "type": 4,  # 4=ChannelMessageWithSource / 5=DeferredChannelMessageWithSource 
        "data": {
            "content": text,
        }
    }
    r = requests.post(endpoint, json=json)
    print(r)


def start():
    try:
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance("i-0c358471181cfc055")
        instance.start()
        # instance.wait_until_running()
    except Exception as e:
        print(e)


def stop():
    try:
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance("i-0c358471181cfc055")
        instance.stop()
        # instance.wait_until_stopped()
    except Exception as e:
        print(e)


def callback(event: dict, context: dict):
    # API Gateway has weird case conversion, so we need to make them lowercase.
    # See https://github.com/aws/aws-sam-cli/issues/1860
    headers: dict = {k.lower(): v for k, v in event['headers'].items()}
    rawBody: str = event['body']

    # validate request
    signature = headers.get('x-signature-ed25519')
    timestamp = headers.get('x-signature-timestamp')
    if not verify(signature, timestamp, rawBody):
        return {
            "cookies": [],
            "isBase64Encoded": False,
            "statusCode": 401,
            "headers": {},
            "body": ""
        }

    req: dict = json.loads(rawBody)
    print(req)
    if req['type'] == 1:  # InteractionType.Ping
        registerCommands()
        return {
            "type": 1  # InteractionResponseType.Pong
        }
    elif req['type'] == 2:  # InteractionType.ApplicationCommand
        action = req['data']['name']
        print(f"action = {action}")
        
        interaction_id = req['id']
        interaction_token = req['token']

        if action == "start":
            text = '起こしたからちょい待ち'
            defer(interaction_id, interaction_token, text)
            start()
    
        if action == "stop":
            text = 'もう少ししたら止まるよ'
            defer(interaction_id, interaction_token, text)
            stop()

        print(text)
        return {
            "type": 4,  # 4=ChannelMessageWithSource / 5=DeferredChannelMessageWithSource 
            "data": {
                "content": text
            }
        }

