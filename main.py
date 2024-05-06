import json
import re
import requests
import time
from discord_webhook import DiscordWebhook
from dotenv import load_dotenv
import os
from datetime import datetime
from urllib.parse import urlparse
import whois

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
last_whois = {}

# Load or create log.json file
log = {}
try:
    with open('log.json', 'r') as f:
        file_contents = f.read()
        if file_contents:
            log = json.loads(file_contents)
except (FileNotFoundError, json.decoder.JSONDecodeError):
    pass


def format_whois_output(whois_info):
    relevant_keys = ['registrar', 'updated_date', 'creation_date', 'expiration_date', 'name_servers', 'status', 'emails']
    formatted_output = ''
    for key in relevant_keys:
        value = whois_info.get(key)
        formatted_key = key.replace('_', ' ').capitalize()
        if value is None:
            formatted_value = 'None'
        elif isinstance(value, list):
            formatted_value = ', '.join(map(str, value))
        else:
            formatted_value = str(value)
        formatted_output += f"**{formatted_key}:** {formatted_value}\n"
    return formatted_output


while True:
    for domain in domains:
        try:
            # Ping the domain using HTTP HEAD request
            start_time = time.time()
            end_time = None
            for scheme in ['https', 'http']:
                parsed_url = urlparse(f'{scheme}://{domain}', scheme)
                url = parsed_url.geturl()
                try:
                    response = requests.head(url, timeout=10)
                    end_time = time.time()
                    break
                except requests.exceptions.RequestException as e:
                    print(f'Error connecting to {url}: {e}')
                    continue

            if end_time is None:
                # Handle case when both HTTP and HTTPS failed
                status = 'Offline'
                ping_status = 'Failed'
                ping_time = -1
            else:
                # Calculate ping time in milliseconds
                ping_time = int((end_time - start_time) * 1000)

                # Determine ping status
                ping_status = 'Successful'

                # Determine the site status based on the ping status and ping time
                status = 'Online' if ping_status == 'Successful' and ping_time < 1000 else 'Offline'

            # Update log if there's a change in status or WHOIS information
            if (status, ping_status, ping_time) != last_check.get(domain, None) or domain not in last_whois:
                # Update last_check dictionary
                last_check[domain] = (status, ping_status, ping_time)

                # Perform WHOIS scan
                try:
                    whois_info = whois.whois(domain)
                    whois_output = format_whois_output(whois_info)
                except Exception as e:
                    whois_output = str(e)

                # Update log with the WHOIS output
                if domain not in log:
                    log[domain] = []
                log_entry = {"date_ms": [f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {ping_time} ms"],
                             "whois": [whois_output]}
                log[domain].append(log_entry)

                # Parse WHOIS information into a dictionary
                current_whois_dict = {}
                for item in whois_output.strip().split('\n'):
                    if ':' in item:
                        key, value = item.split(':', 1)
                        current_whois_dict[key.strip()] = value.strip()

                # Check if any field has changed
                if domain in last_whois:
                    last_stored_whois_dict = last_whois[domain]
                    whois_change_detected = current_whois_dict != last_stored_whois_dict
                else:
                    last_whois[domain] = current_whois_dict
                    whois_change_detected = False  # Set to False for the first check

                whois_message = "Detected changes!" if whois_change_detected else "No changes detected"

                # Update last_whois dictionary
                last_whois[domain] = current_whois_dict

                # Send a formatted message to the Discord channel
                webhook = DiscordWebhook(url=webhook_url)
                history = '\n'.join(entry["date_ms"][0] for entry in log[domain][-10:]) if domain in log else ''

                embed = {
                    'description': f"{':green_circle:' if status == 'Online' else ':red_circle:'} **{domain.upper()} IS {status.upper()}**\n\n"
                                   f"**Status**\n{status}\n\n"
                                   f"**Ping Status**\n{ping_status}\n\n"
                                   f"**Response Time**\n{ping_time} ms\n\n"
                                   f"**WHOIS Scan -** {whois_message}\n\n{whois_output}\n\n"  # Include WHOIS output
                                   f"**History**\n{history}\n\n",
                    'color': 0x00ff00 if status == 'Online' else 0xff0000,
                    'thumbnail': {'url': 'https://i.imgur.com/GwZXlYq.png'},  # Embed thumbnail
                    'footer': {'text': 'The Task Force Monitor'}
                }
                webhook.add_embed(embed)
                response = webhook.execute()

                # Log the check details
                print(f'Domain: {domain}, Status: {status}, Ping Status: {ping_status}, Ping Time: {ping_time} ms, WHOIS Change: {whois_change_detected}')

        except Exception as e:
            # Handle errors
            status = 'Offline'
            ping_status = 'Failed'
            ping_time = -1  # Indicate failure
            log_entry = {
                "date_ms": [f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {ping_status}"],
                "whois": []  # Initialize empty WHOIS logs
            }
            if domain not in log:
                log[domain] = []
            log[domain].append(log_entry)  # Keep all entries

            # Send a formatted message to the Discord channel
            webhook = DiscordWebhook(url=webhook_url)
            history = '\n'.join(entry["date_ms"][0] for entry in log[domain][-10:]) if domain in log else ''
            embed = {
                'description': f"{':red_circle:'} **{domain.Upper()} IS {status.Upper()}**\n\n"
                               f"**Status**\n{status}\n\n"
                               f"**Ping Status**\n{ping_status}\n\n"
                               f"**Response Time**\n{ping_time} ms\n\n"
                               f"**WHOIS Scan -** No changes detected\n\n"
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
