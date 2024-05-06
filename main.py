import json
import re
import requests
import subprocess
import time
from discord_webhook import DiscordWebhook
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Load domains from JSON file
try:
    with open('domains.json', 'r') as f:
        domains = json.load(f)
except FileNotFoundError:
    domains = []

# Get the Discord webhook URL from the environment variable
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

# Initialize last_check dictionary
last_check = {}

# Load or create log.json file
log = {}
try:
    with open('log.json', 'r') as f:
        file_contents = f.read()
        if file_contents:
            log = json.loads(file_contents)
except (FileNotFoundError, json.decoder.JSONDecodeError):
    pass

while True:
    for domain in domains:
        try:
            # Ping the domain using HTTP HEAD request
            start_time = time.time()
            response = requests.head(domain)
            end_time = time.time()

            # Calculate ping time in milliseconds
            ping_time = int((end_time - start_time) * 1000)

            # Determine ping status
            ping_status = 'Successful'

            # Determine the site status based on the ping status and ping time
            status = 'Online' if ping_status == 'Successful' and ping_time < 1000 else 'Offline'

            # Update log
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"{current_time} - {ping_time} ms"
            if domain not in log:
                log[domain] = []
            log[domain].append(log_entry)  # Keep all entries

            # Check if the status has changed since the last check
            if (status, ping_status, ping_time) != last_check.get(domain, None):
                # Send a formatted message to the Discord channel
                webhook = DiscordWebhook(url=webhook_url)
                history = '\n'.join(log[domain][-10:])  # Show only the last 10 entries in the embed
                embed = {
                    'description': f"{':green_circle:' if status == 'Online' else ':red_circle:'} **{domain.replace('https://', '').replace('http://', '').upper()} IS {status.upper()}**\n\n"
                                   f"**Status**\n{status}\n\n"
                                   f"**Ping Status**\n{ping_status}\n\n"
                                   f"**Response Time**\n{ping_time} ms\n\n"
                                   f"**History**\n{history}\n\n",
                    'color': 0x00ff00 if status == 'Online' else 0xff0000,
                    'thumbnail': {'url': 'https://i.imgur.com/GwZXlYq.png'},  # Embed thumbnail
                    'footer': {'text': 'The Task Force Monitor'}
                }
                webhook.add_embed(embed)
                response = webhook.execute()

                # Update last_check dictionary
                last_check[domain] = (status, ping_status, ping_time)

            # Log the check details
            print(f'Domain: {domain}, Status: {status}, Ping Status: {ping_status}, Ping Time: {ping_time} ms')

        except Exception as e:
            # Handle errors
            status = 'Offline'
            ping_status = 'Failed'
            ping_time = -1  # Indicate failure
            log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {ping_status}"
            if domain not in log:
                log[domain] = []
            log[domain].append(log_entry)  # Keep all entries

            # Send a formatted message to the Discord channel
            webhook = DiscordWebhook(url=webhook_url)
            history = '\n'.join(log[domain][-10:])  # Show only the last 10 entries in the embed
            embed = {
                'description': f"{':red_circle:'} **{domain.replace('https://', '').replace('http://', '').upper()} IS {status.upper()}**\n\n"
                               f"**Status**\n{status}\n\n"
                               f"**Ping Status**\n{ping_status}\n\n"
                               f"**Response Time**\n{ping_time} ms\n\n"
                               f"**History**\n{history}\n\n",
                'color': 0xff0000,
                'thumbnail': {'url': 'https://i.imgur.com/GwZXlYq.png'},  # Embed thumbnail
                'footer': {'text': 'The Task Force Monitor'}
            }
            webhook.add_embed(embed)
            response = webhook.execute()

            # Update last_check dictionary
            last_check[domain] = (status, ping_status, ping_time)

            print(f'Error checking {domain}: {e}')

    # Save the log to log.json
    with open('log.json', 'w') as f:
        json.dump(log, f, indent=4)

    # Wait for a specified time before checking again
    time.sleep(60)  # Timer

# Console commands
while True:
    command = input('Enter a command (add/remove/exit): ')
    if command == 'add':
        domain = input('Enter the domain to add: ')
        domains.append(domain)
        last_check[domain] = None
        with open('domains.json', 'w') as f:
            json.dump(domains, f)
        print(f'Added {domain} to the list of domains.')
    elif command == 'remove':
        domain = input('Enter the domain to remove: ')
        if domain in domains:
            domains.remove(domain)
            del last_check[domain]
            del log[domain]
            with open('domains.json', 'w') as f:
                json.dump(domains, f)
            print(f'Removed {domain} from the list of domains.')
        else:
            print(f'{domain} is not in the list of domains.')
    elif command == 'exit':
        break
    else:
        print('Invalid command.')
