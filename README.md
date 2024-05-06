<div align="center">

# Webhook-Watcher

Webhook-Watcher is a Python script designed to monitor the status of specified domains and report changes to a Discord channel using webhooks. It periodically checks the status of each domain, logs the results, and sends notifications for any status changes.

</div>

## Features

- **Domain Monitoring**: Webhook-Watcher monitors the status of specified domains by sending HTTP HEAD requests and checking for successful responses.
- **Discord Notifications**: It sends notifications to a Discord channel via webhooks for any status changes of the monitored domains.
- **Logging**: Webhook-Watcher maintains a log of the monitoring results for each domain, keeping track of response times and status changes.
- **Customization**: Easily add or remove domains to monitor by modifying the `domains.json` file.

<div align="center">

## ☕ [Support my work on Ko-Fi](https://ko-fi.com/thatsinewave)

</div>

## Prerequisites

- Python 3.x
- Required Python packages (`requests`, `discord-webhook`, `python-dotenv`), which can be installed via pip:
  ```bash
  pip install -r requirements.txt
  ```

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/your_username/Webhook-Watcher.git
   ```

2. Navigate to the cloned directory:
   ```bash
   cd Webhook-Watcher
   ```

3. Create a `.env` file and provide your Discord webhook URL:
   ```bash
   cp .env.example .env
   ```
   Replace `YOUR_WEBHOOK_URL_HERE` with your actual Discord webhook URL.

4. Modify the `domains.json` file to include the domains you want to monitor.

5. Run the `main.py` script:
   ```bash
   python main.py
   ```

6. To add or remove domains during runtime, follow the prompts provided in the console interface.

<div align="center">

## [Join my discord server](https://discord.gg/2nHHHBWNDw)

</div>

## File Structure

- **main.py**: The main Python script responsible for monitoring domains and sending notifications.
- **.env.example**: Example environment file containing placeholders for environment variables.
- **domains.json**: JSON file containing the list of domains to monitor.
- **log.json**: JSON file containing the log of monitoring results for each domain.

## Contributing

Contributions are welcome! Feel free to open issues or pull requests for any improvements or additional features.

## License

This project is licensed under the [MIT License](LICENSE).
