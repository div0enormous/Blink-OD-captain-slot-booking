#!/usr/bin/env python3

import os
import json
import time
import uuid
import random
import hashlib
import requests
import threading
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import gzip
from typing import Dict, List, Optional
import sys
import concurrent.futures

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

class BlinkitSlotBooker:
    def __init__(self, debug=False):
        load_dotenv()
        self.list_slots_url = "https://storeops-api.blinkit.com/v1/slots/list_slots_by_site"
        self.book_slots_url = "https://storeops-api.blinkit.com/v1/slots/book"
        self.cancel_slots_url = "https://storeops-api.blinkit.com/v1/slots/cancel"
        self.session = requests.Session()
        self.debug = debug
        self.auto_booking_running = False
        self.stop_auto_booking = False
        self.spinner_running = False

    def generate_request_id(self) -> str:
        """Generate a unique request ID"""
        return str(uuid.uuid4())

    def generate_cf_bm_cookie(self) -> str:
        """Generate a CloudFlare __cf_bm cookie"""
        timestamp = int(time.time())
        random_hash = hashlib.md5(str(random.random()).encode()).hexdigest()[:32]
        return f"{random_hash}-{timestamp}-1.0.1.1-{hashlib.md5(str(random.random()).encode()).hexdigest()[:64]}"

    def generate_cfruid_cookie(self) -> str:
        """Generate a CloudFlare __cfruid cookie"""
        timestamp = int(time.time())
        random_hash = hashlib.sha256(str(random.random()).encode()).hexdigest()[:32]
        return f"{random_hash}-{timestamp}"

    def get_headers(self) -> Dict[str, str]:
        """Build request headers with dynamic values"""
        request_id = self.generate_request_id()
        cf_bm = self.generate_cf_bm_cookie()
        cfruid = self.generate_cfruid_cookie()

        headers = {
            'Host': 'storeops-api.blinkit.com',
            'x-device-manufacturer': os.getenv('DEVICE_MANUFACTURER', 'OPPO'),
            'x-app-version-code': os.getenv('APP_VERSION_CODE', '154501'),
            'version_name': os.getenv('VERSION_NAME', '15.45.1'),
            'x-device-id': os.getenv('DEVICE_ID', '8f92524ac3ab0a43'),
            'version_code': os.getenv('VERSION_CODE', '154501'),
            'x-client-name': os.getenv('CLIENT_NAME', 'storeops-app'),
            'model': os.getenv('MODEL', 'CPH1819'),
            'x-device-hardware-type': os.getenv('DEVICE_HARDWARE_TYPE', 'NON_HHD'),
            'x-app-version': os.getenv('APP_VERSION', '15.45.1'),
            'version': os.getenv('VERSION', '15.45.1'),
            'content-type': 'application/json',
            'x-app-theme': os.getenv('APP_THEME', 'default'),
            'x-app-appearance': os.getenv('APP_APPEARANCE', 'LIGHT'),
            'x-system-appearance': os.getenv('SYSTEM_APPEARANCE', 'UNSPECIFIED'),
            'x-accessibility-voice-over-enabled': os.getenv('VOICE_OVER_ENABLED', '0'),
            'accept': 'application/json',
            'http_session_token': os.getenv('HTTP_SESSION_TOKEN'),
            'role': os.getenv('ROLE', 'OD_CAPTAIN'),
            'session-token': os.getenv('SESSION_TOKEN'),
            'x-lat': os.getenv('LATITUDE', '22.5747936'),
            'employeeid': os.getenv('EMPLOYEE_ID'),
            'site-id': os.getenv('SITE_ID'),
            'userid': os.getenv('USER_ID'),
            'authorization': f"Bearer {os.getenv('AUTH_TOKEN')}",
            'phonenumber': os.getenv('PHONE_NUMBER'),
            'x-app-locale': os.getenv('APP_LOCALE', 'en'),
            'requestid': request_id,
            'site_id': os.getenv('SITE_ID'),
            'x-long': os.getenv('LONGITUDE', '88.28344'),
            'siteid': os.getenv('SITE_ID'),
            'lat': os.getenv('LATITUDE', '22.5747936'),
            'long': os.getenv('LONGITUDE', '88.28344'),
            'user-agent': os.getenv('USER_AGENT', 'com.blinkitstoreops/154501 (Linux; U; Android 10; en; CPH1819; Build/QP1A.190711.020; Cronet/140.0.7289.0)'),
            'accept-encoding': 'gzip, deflate',
            'priority': 'u=1, i'
        }

        # Build cookies
        cfuvid = os.getenv('CFUVID_COOKIE', '5x422DTLm.r7_atNJrAj_oLraFONgPZx152h.zLrbEo-1756816602998-0.0.1.1-604800000')
        cookies = f"__cf_bm={cf_bm}; __cfruid={cfruid}; _cfuvid={cfuvid}"
        headers['cookie'] = cookies

        return headers

    def show_spinner(self, message: str = "Processing"):
        """Show a spinner animation with a hacker-style theme"""
        spinner_chars = ['|', '/', '-', '\\']
        self.spinner_running = True

        def animate():
            i = 0
            while self.spinner_running:
                sys.stdout.write(f"\r{Colors.GREEN}[{spinner_chars[i % len(spinner_chars)]}]{Colors.RESET} {message}...")
                sys.stdout.flush()
                time.sleep(0.1)
                i += 1

        spinner_thread = threading.Thread(target=animate, daemon=True)
        spinner_thread.start()
        return spinner_thread

    def stop_spinner(self):
        """Stop the spinner"""
        self.spinner_running = False
        time.sleep(0.2)
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

    def format_iso_time(self, iso_time: str) -> str:
        """Convert ISO time to IST and readable format"""
        try:
            dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
            ist_offset = timedelta(hours=5, minutes=30)
            ist_time = dt + ist_offset
            return ist_time.strftime('%H:%M')
        except Exception as e:
            if self.debug:
                print_error(f"Time conversion error: {e}")
            return iso_time

    def get_date_input(self, prompt: str) -> str:
        """Get date input from user and format it properly"""
        while True:
            date_input = input(f"{Colors.GREEN}{prompt}:{Colors.RESET} ").strip()
            try:
                date_obj = datetime.strptime(date_input, '%Y-%m-%d')
                end_date = date_obj.replace(hour=18, minute=30, second=0, microsecond=0, tzinfo=timezone.utc)
                start_date = end_date - timedelta(days=1)
                return start_date.isoformat(), end_date.isoformat()
            except ValueError:
                print_error("Invalid date format. Use YYYY-MM-DD (e.g., 2025-09-07)")
                continue

    def get_multiple_dates_input(self, max_dates: int = 5) -> List[tuple]:
        """Get up to max_dates from user"""
        dates = []
        print_info(f"Enter up to {max_dates} target dates (leave empty to finish):")

        for i in range(max_dates):
            date_input = input(f"{Colors.GREEN}Date {i+1} (YYYY-MM-DD):{Colors.RESET} ").strip()
            if not date_input:
                break
            try:
                date_obj = datetime.strptime(date_input, '%Y-%m-%d')
                end_date = date_obj.replace(hour=18, minute=30, second=0, microsecond=0, tzinfo=timezone.utc)
                start_date = end_date - timedelta(days=1)
                dates.append((start_date.isoformat(), end_date.isoformat()))
                print_success(f"Added target: {date_input}")
            except ValueError:
                print_error(f"Invalid date format. Please use YYYY-MM-DD.")
                i -= 1
        return dates

    def get_retry_time(self) -> float:
        """Get retry time from user"""
        while True:
            try:
                retry_input = input(f"{Colors.GREEN}Enter retry interval (default: 5s, min: 0.2s):{Colors.RESET} ").strip()
                if not retry_input:
                    return 5.0
                retry_time = float(retry_input)
                if retry_time < 0.2:
                    print_error("Interval too low. Minimum is 0.2 seconds.")
                    continue
                return retry_time
            except ValueError:
                print_error("Invalid number format.")
                continue

    def get_preferred_timings(self) -> List[tuple]:
        """Display a menu and get user's preferred time slots."""
        time_options = {
            "1": ("08:00-10:00", (datetime.strptime("08:00", "%H:%M").time(), datetime.strptime("10:00", "%H:%M").time())),
            "2": ("10:00-12:00", (datetime.strptime("10:00", "%H:%M").time(), datetime.strptime("12:00", "%H:%M").time())),
            "3": ("12:00-14:00", (datetime.strptime("12:00", "%H:%M").time(), datetime.strptime("14:00", "%H:%M").time())),
            "4": ("14:00-16:00", (datetime.strptime("14:00", "%H:%M").time(), datetime.strptime("16:00", "%H:%M").time())),
            "5": ("16:00-18:00", (datetime.strptime("16:00", "%H:%M").time(), datetime.strptime("18:00", "%H:%M").time())),
            "6": ("18:00-20:00", (datetime.strptime("18:00", "%H:%M").time(), datetime.strptime("20:00", "%H:%M").time())),
            "7": ("20:00-22:00", (datetime.strptime("20:00", "%H:%M").time(), datetime.strptime("22:00", "%H:%M").time())),
            "8": ("22:00-23:59", (datetime.strptime("22:00", "%H:%M").time(), datetime.strptime("23:59", "%H:%M").time())),
        }

        print_info("\nSelect preferred time slots to scan for:")
        for key, (text, _) in time_options.items():
            print(f"{Colors.GREY}{key}:{Colors.RESET} {text}")
        print(f"{Colors.GREY}9:{Colors.RESET} All of the above")

        while True:
            choice_input = input(f"{Colors.GREEN}Enter choices (e.g., 1,3,6), or 9 for all:{Colors.RESET} ").strip()
            if not choice_input:
                print_error("Selection cannot be empty.")
                continue

            if '9' in choice_input:
                print_success("Scanning for all preferred time slots.")
                return [v[1] for v in time_options.values()]

            selected_windows = []
            choices = [c.strip() for c in choice_input.split(',')]
            valid = True
            for choice in choices:
                if choice in time_options:
                    selected_windows.append(time_options[choice][1])
                else:
                    print_error(f"Invalid choice: {choice}")
                    valid = False
                    break
            if valid:
                selected_text = ', '.join([time_options[c][0] for c in choices])
                print_success(f"Scanning for slots in: {selected_text}")
                return selected_windows

    def fetch_slots_by_date(self, start_date: str, end_date: str) -> Optional[Dict]:
        """Fetch slots for a specific date range"""
        try:
            headers = self.get_headers()
            payload = {
                "start_date": start_date,
                "end_date": end_date,
                "status": "All",
                "location_info": {
                    "latitude": float(os.getenv('LATITUDE', '22.5747936')),
                    "longitude": float(os.getenv('LONGITUDE', '88.28344')),
                    "place_id": "",
                    "place_name": ""
                }
            }
            if self.debug:
                print_info(f"Request URL: {self.list_slots_url}")
                print_info(f"Request Payload: {json.dumps(payload, indent=2)}")

            response = self.session.post(self.list_slots_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                if self.debug:
                    print_error(f"HTTP {response.status_code}")
                    print(f"Response: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            if self.debug:
                print_error(f"Network Error: {e}")
            return None
        except Exception as e:
            if self.debug:
                print_error(f"Unexpected Error: {e}")
            return None

    def book_single_slot(self, slot_id: str) -> bool:
        """Book a single slot by slot ID"""
        try:
            headers = self.get_headers()
            payload = {"slot_ids": [slot_id]}
            if self.debug:
                print_info(f"Booking URL: {self.book_slots_url}")
                print_info(f"Booking Payload: {json.dumps(payload, indent=2)}")

            response = self.session.post(self.book_slots_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200 and response.json().get('success'):
                return True
            if self.debug:
                print_error(f"Booking failed for slot {slot_id}: HTTP {response.status_code}")
                print(f"Response: {response.text}")
            return False
        except Exception as e:
            if self.debug:
                print_error(f"Booking Error for slot {slot_id}: {e}")
            return False

    def cancel_slots(self, slot_ids: List[str]) -> bool:
        """Cancel slots by slot IDs"""
        try:
            headers = self.get_headers()
            payload = {"slot_ids": slot_ids}
            if self.debug:
                print_info(f"Cancel URL: {self.cancel_slots_url}")
                print_info(f"Cancel Payload: {json.dumps(payload, indent=2)}")

            response = self.session.post(self.cancel_slots_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200 and response.json().get('success'):
                return True
            if self.debug:
                print_error(f"Cancellation failed: HTTP {response.status_code}")
                print(f"Response: {response.text}")
            return False
        except Exception as e:
            if self.debug:
                print_error(f"Cancellation Error: {e}")
            return False

    def book_slots(self, slot_ids: List[str]) -> bool:
        """Book slots individually (one by one)"""
        if not slot_ids: return False
        successful_bookings, failed_bookings = [], []
        print_info(f"Booking {len(slot_ids)} slot(s) individually...")
        for i, slot_id in enumerate(slot_ids, 1):
            if self.book_single_slot(slot_id):
                successful_bookings.append(slot_id)
                print_success(f"Slot {slot_id} booked successfully")
            else:
                failed_bookings.append(slot_id)
                print_error(f"Slot {slot_id} booking failed")
            time.sleep(0.1) # Small delay
        if successful_bookings:
            print_success(f"Successfully booked {len(successful_bookings)} slot(s): {', '.join(successful_bookings)}")
        if failed_bookings:
            print_warning(f"Failed to book {len(failed_bookings)} slot(s): {', '.join(failed_bookings)}")
        return len(successful_bookings) > 0

    def book_all_slots_at_once(self, slot_ids: List[str]) -> bool:
        """Book all given slots in a single payload."""
        if not slot_ids: return False
        try:
            headers = self.get_headers()
            payload = {"slot_ids": slot_ids}
            if self.debug:
                print_info(f"Booking URL: {self.book_slots_url}")
                print_info(f"Booking Payload (Combined): {json.dumps(payload, indent=2)}")

            response = self.session.post(self.book_slots_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200 and response.json().get('success'):
                print_success(f"Combined booking successful for {len(slot_ids)} slots!")
                return True
            print_error(f"Combined booking failed: HTTP {response.status_code}")
            if self.debug: print(f"Response: {response.text}")
            return False
        except Exception as e:
            if self.debug: print_error(f"Combined Booking Error: {e}")
            return False

    def is_in_selected_windows(self, start_time_iso: str, selected_windows: List[tuple]) -> bool:
        """Check if a slot's start time is within user-selected IST windows."""
        try:
            slot_start_time = datetime.strptime(self.format_iso_time(start_time_iso), "%H:%M").time()
            for start, end in selected_windows:
                if start <= slot_start_time < end:
                    return True
        except (ValueError, TypeError):
            return False
        return False

    def filter_slots_by_store_and_time(self, data: Dict, target_store_id: str, selected_windows: List[tuple]) -> List[Dict]:
        """Filter slots by store, availability, and selected time windows."""
        eligible_slots = []
        if not data or not (stores := data.get('data', {}).get('stores')): return []
        for store in stores:
            if store.get('id') != target_store_id: continue
            for slot in store.get('slots', []):
                is_available = not slot.get('is_booked') and slot.get('booking_eligibility', {}).get('allowed')
                if is_available and (start_time := slot.get('start_time')) and self.is_in_selected_windows(start_time, selected_windows):
                    eligible_slots.append(slot)
        return eligible_slots

    def display_formatted_slots(self, data: Dict):
        """Display slots in a clean, hacker-style format"""
        if not data or not (stores := data.get('data', {}).get('stores')):
            print_error("No valid slot data received")
            return
        for store in stores:
            store_name = store.get('name', 'Unknown')
            print(f"\n{Colors.BOLD}STORE:{Colors.RESET} {store_name} ({store.get('address', 'N/A')})")
            print(f"{Colors.GREY}{'='*40}{Colors.RESET}")
            if not (slots := store.get('slots')):
                print_warning("No slots available for this store.")
                continue
            for slot in slots:
                start_time = self.format_iso_time(slot.get('start_time', ''))
                end_time = self.format_iso_time(slot.get('end_time', ''))
                slot_id = slot.get('id', 'N/A')
                payout = f"₹{slot.get('min_payout', 0)}–₹{slot.get('max_payout', 0)}"
                status_color = Colors.GREEN if not slot.get('is_booked') else Colors.RED
                status_text = "Available" if not slot.get('is_booked') else "Booked"
                print(f"  {Colors.GREEN}{start_time} - {end_time}{Colors.RESET} | ID: {Colors.WHITE}{slot_id}{Colors.RESET} | Payout: {Colors.YELLOW}{payout}{Colors.RESET}")
                print(f"  Status: {status_color}{status_text}{Colors.RESET} | Cancellable: {'Yes' if slot.get('is_cancellable') else 'No'}")
                print(f"{Colors.GREY}{'-'*40}{Colors.RESET}")

    def beast_mode_booking(self, date_ranges: List[tuple], target_store_id: str, retry_time: float, selected_windows: List[tuple]):
        """Beast mode - check multiple dates, filter by time, and book automatically."""
        date_list = [end.split('T')[0] for _, end in date_ranges]
        print_info(f"Beast Mode engaged for dates: {', '.join(date_list)}")
        spinner = self.show_spinner("Scanning for preferred slots")
        while not self.stop_auto_booking:
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(date_ranges)) as executor:
                    future_to_date = {executor.submit(self.fetch_slots_by_date, s, e): (s, e) for s, e in date_ranges}
                    all_preferred_slots = []
                    for future in concurrent.futures.as_completed(future_to_date):
                        try:
                            if data := future.result():
                                all_preferred_slots.extend(self.filter_slots_by_store_and_time(data, target_store_id, selected_windows))
                        except Exception as e:
                            if self.debug: print_error(f"Error processing future: {e}")
                    if all_preferred_slots:
                        self.stop_spinner()
                        slots_to_book_ids = [str(s.get('id')) for s in all_preferred_slots]
                        print_warning(f"Found {len(slots_to_book_ids)} matching slots. Engaging booking protocol...")
                        self.book_slots(slots_to_book_ids)
                        spinner = self.show_spinner("Resuming scan for preferred slots")
            except Exception as e:
                if self.debug: print_error(f"Error during beast mode: {e}")
            if not self.stop_auto_booking: time.sleep(retry_time)
        self.stop_spinner()
        print_info("Beast Mode disengaged.")
        self.auto_booking_running = False

    def auto_booking(self):
        """Auto booking functionality"""
        print(f"\n{Colors.BOLD}--- AUTO BOOKING ---{Colors.RESET}")
        print("1. Beast Mode (Single Store, Time-based)")
        print("2. Multi-Store Beast Mode (2 Stores)")
        mode = input(f"{Colors.GREEN}Select mode (1-2):{Colors.RESET} ").strip()

        booking_thread = None
        if mode == '1':
            date_ranges = self.get_multiple_dates_input(max_dates=10)
            if not date_ranges: return print_error("No dates provided.")
            selected_windows = self.get_preferred_timings()
            if not selected_windows: return
            retry_time = self.get_retry_time()
            target_store_id = input(f"{Colors.GREEN}Enter Target Store ID (default: 5296):{Colors.RESET} ").strip() or os.getenv('TARGET_STORE_ID', '5296')
            print_info(f"Starting Beast Mode for Store ID: {target_store_id}")
            booking_thread = threading.Thread(target=self.beast_mode_booking, args=(date_ranges, target_store_id, retry_time, selected_windows), daemon=True)
        elif mode == '2':
            # Simplified for brevity - you can add multi-store logic here if needed
            print_error("Multi-store mode is not implemented in this version.")
            return
        else:
            return print_error("Invalid selection.")

        if self.auto_booking_running: return print_warning("Auto booking is already running.")
        if booking_thread:
            self.auto_booking_running = True
            self.stop_auto_booking = False
            print_info("Press Ctrl+C or type 'stop' to halt.")
            booking_thread.start()
            try:
                while self.auto_booking_running:
                    if input("\nType 'stop' to halt: ").strip().lower() == 'stop':
                        self.stop_auto_booking = True
                        break
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping auto booking...")
                self.stop_auto_booking = True

    def manual_booking(self):
        """Manual booking functionality"""
        print(f"\n{Colors.BOLD}--- MANUAL BOOKING ---{Colors.RESET}")
        slot_ids_input = input(f"{Colors.GREEN}Enter slot IDs (comma-separated):{Colors.RESET} ").strip()
        if not slot_ids_input: return print_error("No slot IDs provided.")
        slot_ids = [sid.strip() for sid in slot_ids_input.split(',') if sid.strip()]
        if not slot_ids: return print_error("No valid slot IDs provided.")
        print_info(f"Attempting to book {len(slot_ids)} slot(s)...")
        spinner = self.show_spinner("Booking slots")
        if self.book_slots(slot_ids):
            self.stop_spinner()
            print_success("Booking complete. Check app for confirmation.")
        else:
            self.stop_spinner()
            print_error("Failed to book any slots.")

    def cancel_slots_menu(self):
        """Cancel slots functionality"""
        print(f"\n{Colors.BOLD}--- CANCEL SLOTS ---{Colors.RESET}")
        slot_ids_input = input(f"{Colors.GREEN}Enter slot IDs to cancel (comma-separated):{Colors.RESET} ").strip()
        if not slot_ids_input: return print_error("No slot IDs provided.")
        slot_ids = [sid.strip() for sid in slot_ids_input.split(',') if sid.strip()]
        if not slot_ids: return print_error("No valid slot IDs provided.")
        print_info(f"Attempting to cancel {len(slot_ids)} slot(s)...")
        spinner = self.show_spinner("Cancelling slots")
        if self.cancel_slots(slot_ids):
            self.stop_spinner()
            print_success("Slots cancelled successfully.")
        else:
            self.stop_spinner()
            print_error("Failed to cancel slots.")

    def view_list_of_slots(self):
        """View list of slots for a specific date"""
        print(f"\n{Colors.BOLD}--- VIEW SLOTS ---{Colors.RESET}")
        start_date, end_date = self.get_date_input("Enter date to view slots (YYYY-MM-DD)")
        spinner = self.show_spinner("Fetching slots")
        data = self.fetch_slots_by_date(start_date, end_date)
        self.stop_spinner()
        if not data: return print_error("Failed to fetch slot data.")
        self.display_formatted_slots(data)

    def show_settings(self):
        """Display and manage settings"""
        print(f"\n{Colors.BOLD}--- SETTINGS ---{Colors.RESET}")
        settings = {
            'DEVICE_ID': 'Device ID', 'EMPLOYEE_ID': 'Employee ID', 'SITE_ID': 'Site ID',
            'USER_ID': 'User ID', 'PHONE_NUMBER': 'Phone Number', 'TARGET_STORE_ID': 'Default Target Store ID'
        }
        for env_var, desc in settings.items():
            value = os.getenv(env_var, 'Not Set')
            display_value = value[:10] + "..." if len(value) > 10 and 'TOKEN' in env_var else value
            print(f"  {Colors.GREY}{desc:<25}:{Colors.RESET} {display_value}")
        print_info("\nTo modify settings, edit the .env file directly.")

    def show_menu(self):
        """Display main menu"""
        status_text = f"{Colors.YELLOW}(Running){Colors.RESET}" if self.auto_booking_running else ""
        print(f"\n{Colors.BOLD}--- BLINKIT SLOT BOOKING SYSTEM ---{Colors.RESET} {status_text}")
        print(f"{Colors.GREY}{'='*40}{Colors.RESET}")
        print(f"  {Colors.GREEN}1.{Colors.RESET} Auto Booking")
        print(f"  {Colors.GREEN}2.{Colors.RESET} Manual Booking")
        print(f"  {Colors.GREEN}3.{Colors.RESET} View List of Slots")
        print(f"  {Colors.GREEN}4.{Colors.RESET} Settings")
        print(f"  {Colors.GREEN}5.{Colors.RESET} Exit")
        return input(f"\n{Colors.GREEN}>> Select an option:{Colors.RESET} ").strip()

    def run(self):
        """Main application loop"""
        print(f"\n{Colors.BOLD}Blinkit Slot Booking System{Colors.RESET}")
        print(f"{Colors.GREY}Author: Dibyendu Dey{Colors.RESET}")
        while True:
            try:
                choice = self.show_menu()
                if choice == '1': self.auto_booking()
                elif choice == '2': self.manual_booking()
                elif choice == '3': self.view_list_of_slots()
                elif choice == '4': self.show_settings()
                elif choice == '5':
                    if self.auto_booking_running:
                        print_info("Stopping background process...")
                        self.stop_auto_booking = True
                        time.sleep(2)
                    print_info("Exiting...")
                    break
                else: print_error("Invalid option.")
                if choice != '1': input(f"\n{Colors.GREY}Press Enter to continue...{Colors.RESET}")
            except KeyboardInterrupt:
                print("\n\nExiting...")
                if self.auto_booking_running: self.stop_auto_booking = True
                break
            except Exception as e:
                print_error(f"An unexpected error occurred: {e}")
                if self.debug: import traceback; traceback.print_exc()
                input(f"{Colors.GREY}Press Enter to continue...{Colors.RESET}")

def create_env_template():
    """Create a template .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        template = """# Blinkit System Configuration
# Fill in your values below
DEVICE_MANUFACTURER=OPPO
APP_VERSION_CODE=154501
VERSION_NAME=15.45.1
DEVICE_ID=8f92524ac3ab0a43
MODEL=CPH1819
EMPLOYEE_ID=YOUR_EMPLOYEE_ID
SITE_ID=YOUR_SITE_ID
USER_ID=YOUR_USER_ID
PHONE_NUMBER=YOUR_PHONE_NUMBER
LATITUDE=22.5747936
LONGITUDE=88.28344
TARGET_STORE_ID=5296
AUTH_TOKEN=YOUR_AUTH_TOKEN_HERE
HTTP_SESSION_TOKEN=YOUR_SESSION_TOKEN_HERE
SESSION_TOKEN=YOUR_SESSION_TOKEN_HERE
"""
        with open('.env', 'w') as f: f.write(template)
        print_success("Created .env template file. Please update it with your values.")
        return False
    return True

if __name__ == "__main__":
    try:
        import requests
        from dotenv import load_dotenv
    except ImportError:
        print_error("Missing required packages. Run: pip install requests python-dotenv")
        exit(1)
    if create_env_template():
        booker = BlinkitSlotBooker(debug=False)
        booker.run()