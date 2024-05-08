import json
import time
import whois
import requests
from datetime import datetime
from discord_webhook import DiscordWebhook
from difflib import unified_diff

# Load configurations
print("Loading configurations...")
with open("domain.json", "r") as f:
    domain_config = json.load(f)

try:
    with open("log.json", "r") as f:
        log_data = json.load(f)
except FileNotFoundError:
    # If log.json doesn't exist, initialize log_data with an empty dictionary
    log_data = {}

if "logs" not in log_data:
    # Initialize logs if it doesn't exist
    log_data["logs"] = []

with open("webhook.json", "r") as f:
    webhook_config = json.load(f)


# Function to get ping time
def get_ping_time(url):
    try:
        response = requests.head(url)
        ping_time = response.elapsed.total_seconds() * 1000
        return ping_time
    except requests.ConnectionError:
        return "Failed to connect"


# Monitor whois details
def monitor_whois():
    domain = whois.whois(domain_config["domain"])
    filtered_domain = {k: v for k, v in domain.items() if k not in ['dnssec', 'name', 'org', 'address', 'city', 'state', 'zipcode', 'country']}
    return filtered_domain


# Monitor IP details
def monitor_ip():
    ip_query = domain_config["domain"].split("//")[1]
    ip_api_url = f"http://ip-api.com/json/{ip_query}?fields=status,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
    response = requests.get(ip_api_url)
    return response.json()


# Function to send Discord webhook with a formatted embed message
def send_discord_webhook(ping_time, whois_data, ip_data, changes):
    webhook = DiscordWebhook(url=webhook_config["webhook_url"])

    # Create the embed object
    embed = {
        "title": f"🔍 MONITORING {domain_config['domain']}",
        "color": 0x00ff00,  # Green color
        "fields": [
            {
                "name": "Time",
                "value": f"```{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}```",
                "inline": True
            },
            {
                "name": "Ping",
                "value": f"```{ping_time} ms```" if isinstance(ping_time, (int, float)) else f"```{ping_time}```",
                "inline": True
            },
            {
                "name": "Whois Info",
                "value": r"```" + f"\n".join([fr"{key}: {value}" for key, value in whois_data.items()]) + r"```",
                "inline": False
            },
            {
                "name": "IP Details",
                "value": r"```" + f"\n".join([fr"{key}: {value}" for key, value in ip_data.items()]) + r"```",
                "inline": False
            },
            {
                "name": "Changes",
                "value": "No changes detected" if not changes else "Detected changes\n```diff\n" + "\n".join(changes) + "\n```",
                "inline": False
            }
        ]
    }

    # Add the embed to the webhook
    webhook.add_embed(embed)

    response = webhook.execute()


# Function to save logs
def save_logs(data, changes):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": current_time,
        "data": data,
        "changes": {
            "message": "Detected changes" if changes else "No changes detected",
            "diff": "\n".join(changes) if changes else ""
        }
    }
    log_data["logs"].append(log_entry)

    with open("log.json", "w") as f:
        json.dump(log_data, f, indent=4, default=str)


# Monitor function
def monitor():
    print("Starting monitoring loop...")
    previous_whois_data = None
    while True:
        ping_time = get_ping_time(domain_config["domain"])
        whois_data = monitor_whois()
        ip_data = monitor_ip()

        # Calculate changes
        changes = []
        if previous_whois_data:
            if whois_data != previous_whois_data:
                changes.extend(unified_diff(
                    json.dumps(previous_whois_data, sort_keys=True, indent=4).splitlines(),
                    json.dumps(whois_data, sort_keys=True, indent=4).splitlines(),
                    fromfile="Previous Whois",
                    tofile="Current Whois",
                    lineterm=""
                ))

        # Send the formatted embed message
        send_discord_webhook(ping_time, whois_data, ip_data, changes)

        # Save logs
        save_logs({"ping_time": ping_time, "whois": whois_data, "ip": ip_data}, changes)

        previous_whois_data = whois_data

        print("Waiting for 1 minute before next check...")
        # Wait for 1 minute before checking again
        time.sleep(60)


# Run monitoring
monitor()