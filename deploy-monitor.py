import os
import shutil
import json
import subprocess
import datetime
import logging
import re
import psutil
import sys
import threading
from urllib.parse import urlparse


# Set up logging
logging.basicConfig(filename='deployer.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def create_monitor():
    # Get domain and webhook from user
    domain_url = input("Enter the domain: ")
    webhook_url = input("Enter the webhook URL: ")

    # Extract the domain name from the URL
    parsed_url = urlparse(domain_url)
    domain = parsed_url.netloc

    # Create the new folder inside the monitors directory
    monitors_dir = os.path.join(os.getcwd(), "monitors")
    if not os.path.exists(monitors_dir):
        os.makedirs(monitors_dir)

    new_monitor_dir = os.path.join(monitors_dir, domain)
    os.makedirs(new_monitor_dir, exist_ok=True)

    # Copy and modify the required files
    model_dir = os.path.join(os.getcwd(), "model")
    shutil.copy(os.path.join(model_dir, "monitor.py"), new_monitor_dir)
    os.rename(os.path.join(new_monitor_dir, "monitor.py"), os.path.join(new_monitor_dir, f"{domain}.py"))

    with open(os.path.join(new_monitor_dir, "domain.json"), "w") as f:
        json.dump({"domain": domain_url}, f)
        logging.info(f"Created domain.json for monitor {domain}")

    with open(os.path.join(new_monitor_dir, "webhook.json"), "w") as f:
        json.dump({"webhook_url": webhook_url}, f)
        logging.info(f"Created webhook.json for monitor {domain}")

    with open(os.path.join(new_monitor_dir, "log.json"), "w") as f:
        json.dump({}, f)
        logging.info(f"Created log.json for monitor {domain}")

    logging.info(f"Created new monitor for {domain_url}")

    # Ask if the user wants to start the monitor
    start_monitor = input(f"Do you want to start the monitor for {domain_url} now? (y/n) ").lower()
    if start_monitor == "y":
        start_monitor_process(new_monitor_dir, domain)


def start_monitor_process(monitor_dir, domain):
    monitor_script = os.path.join(monitor_dir, f"{domain}.py")
    if os.path.exists(monitor_script):
        os.chdir(monitor_dir)  # Change working directory to monitor directory
        command = f'"{sys.executable}" "{monitor_script}"'
        try:
            subprocess.run(command, shell=True, check=True)
            logging.info(f"Started monitor for {domain} at {datetime.datetime.now()}")
        except subprocess.CalledProcessError as e:
            print(f"Error starting monitor for {domain}: {e}")
            logging.error(f"Error starting monitor for {domain}: {e}")
        finally:
            os.chdir(os.path.dirname(os.getcwd()))  # Change working directory back to previous directory
    else:
        print(f"Monitor script '{monitor_script}' not found.")


def stop_monitor_process(monitor_dir, domain):
    for proc in psutil.process_iter(['cmdline']):
        try:
            if domain in proc.cmdline()[-1]:
                proc.terminate()
                logging.info(f"Stopped monitor for {domain} at {datetime.datetime.now()}")
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, IndexError):
            pass
    else:
        logging.info(f"No running monitor found for {domain}")


def start_monitors():
    monitors_dir = os.path.join(os.getcwd(), "monitors")
    if not os.path.exists(monitors_dir):
        print("No monitors found.")
        return

    print("Available monitors:")
    monitor_dirs = [d for d in os.listdir(monitors_dir) if os.path.isdir(os.path.join(monitors_dir, d))]
    for i, monitor_dir in enumerate(monitor_dirs, start=1):
        print(f"{i}. {monitor_dir}")

    choice = input("Enter the number of the monitor to start, or 'all' to start all monitors: ")
    if choice == "all":
        for monitor_dir in monitor_dirs:
            start_monitor_process(os.path.join(monitors_dir, monitor_dir), monitor_dir)
    else:
        try:
            index = int(choice) - 1
            if index >= 0 and index < len(monitor_dirs):
                monitor_dir = monitor_dirs[index]
                start_monitor_process(os.path.join(monitors_dir, monitor_dir), monitor_dir)
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid choice.")


def stop_monitors():
    monitors_dir = os.path.join(os.getcwd(), "monitors")
    if not os.path.exists(monitors_dir):
        print("No monitors found.")
        return

    print("Available monitors:")
    monitor_dirs = [d for d in os.listdir(monitors_dir) if os.path.isdir(os.path.join(monitors_dir, d))]
    for i, monitor_dir in enumerate(monitor_dirs, start=1):
        print(f"{i}. {monitor_dir}")

    choice = input("Enter the number of the monitor to stop, or 'all' to stop all monitors: ")
    if choice == "all":
        for monitor_dir in monitor_dirs:
            stop_monitor_process(os.path.join(monitors_dir, monitor_dir), monitor_dir)
    else:
        try:
            index = int(choice) - 1
            if index >= 0 and index < len(monitor_dirs):
                monitor_dir = monitor_dirs[index]
                stop_monitor_process(os.path.join(monitors_dir, monitor_dir), monitor_dir)
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid choice.")


def main():
    while True:
        print("\nWhat would you like to do?")
        print("1. Create a new monitor")
        print("2. Start existing monitor(s)")
        print("3. Stop existing monitor(s)")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            create_monitor()
        elif choice == "2":
            start_monitors()
        elif choice == "3":
            stop_monitors()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
