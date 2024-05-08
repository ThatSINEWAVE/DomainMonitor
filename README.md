<div align="center">

# DomainMonitor

DomainMonitor is a Python-based monitoring tool designed to track changes in specified domains and notify users via Discord webhooks. It facilitates monitoring various aspects of a domain, including ping time, WHOIS information, and IP details, and sends notifications when changes are detected.

</div>

## Features

- **Domain Monitoring**: Keep track of the status and details of specified domains.
- **Ping Time Monitoring**: Measure the response time (ping) of monitored domains.
- **WHOIS Information**: Retrieve and monitor WHOIS information for domains.
- **IP Details**: Obtain and monitor IP details associated with domains.
- **Change Detection**: Detect changes in domain information and notify users via Discord webhooks.
- **Customization**: Easily deploy and configure new monitors using provided scripts.
- **Continuous Monitoring**: Run monitoring processes continuously to ensure timely detection of changes.
- **Logging**: Log deployment activities and monitoring data for reference and analysis.

<div align="center">

## ☕ [Support my work on Ko-Fi](https://ko-fi.com/thatsinewave)

</div>

## Project Structure

The project structure includes the following files and directories:

- **`monitors/`**: Directory containing template monitor configurations.
- **`model/domain.json`**: Configuration template for the monitored domain.
- **`model/webhook.json`**: Configuration template for webhook URL.
- **`model/log.json`**: Template for log data for the monitored domain.
- **`model/monitor.py`**: Python script for monitoring domains.
- **`deploy-monitor.py`**: Script for deploying new monitors.
- **`deployer.log`**: Log file for deployment activities.

## Requirements

DomainMonitor relies on the following Python libraries:

- `whois`: For retrieving WHOIS information.
- `requests`: For making HTTP requests.
- `discord_webhook`: For sending notifications via Discord webhooks.
- `difflib`: For generating difference reports.
- `psutil`: For managing processes.

## Installation

To install DomainMonitor and its dependencies, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/DomainMonitor.git
   ```

2. Navigate to the project directory:

   ```bash
   cd DomainMonitor
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

<div align="center">

## [Join my discord server](https://discord.gg/2nHHHBWNDw)

</div>

## Example Monitors

### Monitor for `https://example.com`

This monitor checks the status of `https://example.com` and sends notifications via Discord webhook if any changes are detected.

### Monitor for `https://github.com`

Similar to the previous monitor, this one monitors `https://github.com` and notifies about changes via Discord webhook.

## Deployment

To deploy a new monitor:

1. Run the `deploy-monitor.py` script.
2. Enter the domain URL and Discord webhook URL when prompted.
3. Optionally, start the monitor immediately or start it later using the provided options.

## Usage

Once monitors are set up, the monitoring process runs continuously in the background, checking for changes at regular intervals. You can customize the monitoring frequency and behavior according to your requirements.

## Log File

The `deployer.log` file contains logs generated by the deployment process, providing insights into monitor creation and management activities.

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
