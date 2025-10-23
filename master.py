#!/usr/bin/env python3

import os
import json
import time
import uuid
import random
import hashlib
import requests
import threading
import sys
from datetime import datetime
from dotenv import load_dotenv, find_dotenv, set_key
import base64

# --- Hacker Style Theme ---
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    WHITE = '\033[97m'
    GREY = '\033[90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}[+]{Colors.RESET} {message}")

def print_error(message):
    print(f"{Colors.RED}[-]{Colors.RESET} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[!]{Colors.RESET} {message}")

def print_info(message):
    print(f"{Colors.GREY}[*]{Colors.RESET} {message}")

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

class BlinkitTaskMaster:
    def __init__(self, debug=False):
        load_dotenv()
        self.pending_tasks_url = "https://storeops-api.blinkit.com/v1/worker/pending_tasks"
        self.notifications_url = f"https://notification-api.blinkit.com/receiver/{os.getenv('EMPLOYEE_ID')}/parcels?status=PENDING"
        self.worker_state_url = "https://storeops-api.blinkit.com/v1/worker/state"
        self.session = requests.Session()
        self.debug = debug
        self.stop_fetching = False

    def generate_request_id(self) -> str:
        return str(uuid.uuid4())

    def generate_cf_bm_cookie(self) -> str:
        timestamp = int(time.time())
        random_part1 = hashlib.sha256(str(random.random()).encode()).hexdigest()
        random_part2 = hashlib.sha256(str(random.random()).encode()).hexdigest()
        return f"{random_part1[:40]}-{timestamp}-1.0.1.1-{random_part2[:50]}"

    def generate_cfruid_cookie(self) -> str:
        timestamp = int(time.time())
        random_hash = hashlib.sha256(str(random.random()).encode()).hexdigest()
        return f"{random_hash[:40]}-{timestamp}"

    def get_headers(self, host: str, auth_token: str = None) -> dict:
        request_id, cf_bm, cfruid = self.generate_request_id(), self.generate_cf_bm_cookie(), self.generate_cfruid_cookie()
        final_auth_token = auth_token or os.getenv('AUTH_TOKEN')
        headers = {
            'Host': host,
            'x-device-id': os.getenv('DEVICE_ID', '17564ebcddad5a0c'),
            'authorization': f"Bearer {final_auth_token}",
            'user-agent': os.getenv('USER_AGENT', 'com.blinkitstoreops/155406 (Linux; U; Android 10; en; CPH1819; Build/QP1A.190711.020; Cronet/141.0.7340.3)'),
            'accept': 'application/json', 'content-type': 'application/json',
            'employeeid': os.getenv('EMPLOYEE_ID'), 'site-id': os.getenv('SITE_ID'),
            'requestid': request_id,
            'cookie': f"__cf_bm={cf_bm}; __cfruid={cfruid}; _cfuvid={os.getenv('CFUVID_COOKIE')}"
        }
        if "notification-api" in host:
            headers['x-tenant-id'] = 'STOREOPS'
        return headers

    def fetch_api(self, url: str, headers: dict):
        try:
            response = self.session.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                return response.json()
            return {"error": f"HTTP {response.status_code}", "response": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": f"Network Error: {e}"}

    def fetch_orders_loop(self):
        """Continuously fetch from both APIs and display raw, non-repeating output."""
        try:
            interval = float(input(f"{Colors.GREEN}Enter refresh interval in seconds (e.g., 5):{Colors.RESET} ").strip())
        except ValueError:
            print_error("Invalid number. Defaulting to 5 seconds.")
            interval = 5.0

        self.stop_fetching = False
        print_info(f"Starting to fetch orders every {interval} seconds. Press Ctrl+C to stop.")
        time.sleep(2)

        while not self.stop_fetching:
            try:
                clear_screen()
                print(f"{Colors.BOLD}--- BLINKIT TASK MASTER - LIVE FEED ---{Colors.RESET}")
                print(f"{Colors.GREY}Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Interval: {interval}s{Colors.RESET}\n")

                # Fetch and display Pending Tasks
                print(f"{Colors.YELLOW}[*] Pending Tasks API Output:{Colors.RESET}")
                task_headers = self.get_headers(host="storeops-api.blinkit.com")
                task_data = self.fetch_api(self.pending_tasks_url, task_headers)
                print(f"{Colors.GREY}{json.dumps(task_data, indent=2)}{Colors.RESET}")

                print(f"\n{Colors.GREY}{'='*50}{Colors.RESET}\n")

                # Fetch and display Notifications
                print(f"{Colors.YELLOW}[*] Notifications API Output:{Colors.RESET}")
                notification_headers = self.get_headers(host="notification-api.blinkit.com")
                notification_data = self.fetch_api(self.notifications_url, notification_headers)
                print(f"{Colors.GREY}{json.dumps(notification_data, indent=2)}{Colors.RESET}")

                time.sleep(interval)
            except KeyboardInterrupt:
                self.stop_fetching = True
                clear_screen()
                print_info("\nStopping fetch loop.")
                break

    def ghost_mode(self):
        """Continuously cycle worker status between OFFLINE and ONLINE."""
        print(f"\n{Colors.BOLD}--- GHOST MODE (STATUS CYCLER) ---{Colors.RESET}")
        print_warning("This mode will repeatedly set your status to OFFLINE, then ONLINE.")
        
        auth_token = input(f"{Colors.YELLOW}Enter fresh Auth Token (Bearer): {Colors.RESET}").strip()
        if not auth_token:
            print_error("Auth token is required.")
            return

        try:
            interval = float(input(f"{Colors.GREEN}Enter interval between status changes (e.g., 5 seconds):{Colors.RESET} ").strip())
        except ValueError:
            print_error("Invalid number. Defaulting to 5 seconds.")
            interval = 5.0
            
        headers = self.get_headers(host="storeops-api.blinkit.com", auth_token=auth_token)
        payload_offline = {"status": "OFFLINE"}
        payload_online = {"active_role_name": "PICKER", "status": "ONLINE"}

        print_info(f"Starting Ghost Mode loop. Press Ctrl+C to stop.")
        time.sleep(2)

        try:
            while True:
                # Go OFFLINE
                print_info(f"[{datetime.now().strftime('%H:%M:%S')}] Setting status to OFFLINE...")
                try:
                    response_offline = self.session.post(self.worker_state_url, headers=headers, json=payload_offline, timeout=20)
                    if response_offline.status_code == 200:
                        print_success("Status set to OFFLINE.")
                    else:
                        print_error(f"Failed to go OFFLINE. Status: {response_offline.status_code}")
                        if self.debug: print(f"Response: {response_offline.text}")
                except requests.exceptions.RequestException as e:
                    print_error(f"Network error on OFFLINE call: {e}")

                time.sleep(interval)

                # Go ONLINE
                print_info(f"[{datetime.now().strftime('%H:%M:%S')}] Setting status to ONLINE...")
                try:
                    response_online = self.session.post(self.worker_state_url, headers=headers, json=payload_online, timeout=20)
                    if response_online.status_code == 200:
                        print_success("Status set to ONLINE.")
                    else:
                        print_error(f"Failed to go ONLINE. Status: {response_online.status_code}")
                        if self.debug: print(f"Response: {response_online.text}")
                except requests.exceptions.RequestException as e:
                    print_error(f"Network error on ONLINE call: {e}")
                
                print(f"{Colors.GREY}{'-'*40}{Colors.RESET}")
                time.sleep(interval)

        except KeyboardInterrupt:
            print_info("\nGhost Mode stopped.")

    def analyze_jwt(self):
        """Analyzes a JWT token."""
        print(f"\n{Colors.BOLD}--- JWT TOKEN ANALYZER ---{Colors.RESET}")
        print_warning("This feature CANNOT generate a valid token.")
        token = input(f"{Colors.YELLOW}Enter your full Bearer token to analyze: {Colors.RESET}").strip()
        if token.lower().startswith("bearer "): token = token[7:]
        try:
            header = json.loads(base64.urlsafe_b64decode(token.split('.')[0] + '==').decode())
            payload = json.loads(base64.urlsafe_b64decode(token.split('.')[1] + '==').decode())
            print(f"\n{Colors.GREEN}[+] TOKEN HEADER:{Colors.RESET}\n{json.dumps(header, indent=2)}")
            print(f"\n{Colors.GREEN}[+] TOKEN PAYLOAD:{Colors.RESET}\n{json.dumps(payload, indent=2)}")
            if 'exp' in payload:
                expiry_time = datetime.fromtimestamp(payload['exp'])
                print(f"\n{Colors.GREY}[*] Token expires at: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
        except Exception as e:
            print_error(f"Could not decode token. Error: {e}")

    def show_menu(self):
        print(f"\n\n{Colors.BOLD}--- BLINKIT TASK MASTER ---{Colors.RESET}")
        print(f"{Colors.GREY}Author: Dibyendu Dey{Colors.RESET}")
        print(f"{Colors.GREY}{'='*40}{Colors.RESET}")
        print(f"  {Colors.GREEN}1.{Colors.RESET} Fetch More Orders (Live Feed)")
        print(f"  {Colors.GREEN}2.{Colors.RESET} Ghost Mode (Status Cycler)")
        print(f"  {Colors.GREEN}3.{Colors.RESET} Analyze Bearer Token")
        print(f"  {Colors.GREEN}4.{Colors.RESET} Exit")
        return input(f"\n{Colors.GREEN}>> Select an option:{Colors.RESET} ").strip()

    def run(self):
        while True:
            choice = self.show_menu()
            if choice == '1': self.fetch_orders_loop()
            elif choice == '2': self.ghost_mode()
            elif choice == '3': self.analyze_jwt()
            elif choice == '4':
                print_info("Goodbye!")
                break
            else:
                print_error("Invalid option.")
            input(f"\n{Colors.GREY}Press Enter to return to the menu...{Colors.RESET}")

if __name__ == "__main__":
    try:
        import requests
        from dotenv import load_dotenv, find_dotenv, set_key
    except ImportError:
        print_error("Missing required packages. Run: pip install requests python-dotenv")
        sys.exit(1)

    if not os.path.exists('.env'):
        with open('.env', 'w') as f: f.write("# See book.py for .env template\n")
        print_warning("Created .env file. Please populate it with your credentials.")

    master = BlinkitTaskMaster()
    master.run()