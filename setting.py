import os
import sys
from pathlib import Path
import json
from typing import Dict, Any, Optional

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


class BlinkitConfigManager:
    def __init__(self, env_file_path: str = ".env"):
        self.env_file_path = Path(env_file_path)
        self.config_data = {}
        self.load_config()

    def load_config(self) -> None:
        if not self.env_file_path.exists():
            print_warning(f".env file not found at {self.env_file_path}. Creating a new one...")
            self.create_default_config()
            return
        try:
            with open(self.env_file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self.config_data[key.strip()] = value.strip()
            print_success(f"Configuration loaded from {self.env_file_path}")
        except Exception as e:
            print_error(f"Error loading configuration: {e}")
            sys.exit(1)

    def save_config(self) -> None:
        try:
            with open(self.env_file_path, 'w', encoding='utf-8') as file:
                file.write("# Blinkit System Configuration\n")
                for key, value in self.config_data.items():
                    file.write(f"{key}={value}\n")
            print_success(f"Configuration saved to {self.env_file_path}")
        except Exception as e:
            print_error(f"Error saving configuration: {e}")

    def create_default_config(self) -> None:
        default_config = {
            "DEVICE_MANUFACTURER": "OPPO", "APP_VERSION_CODE": "154501", "VERSION_NAME": "15.45.1",
            "DEVICE_ID": "8f92524ac3ab0a43", "MODEL": "CPH1819",
            "EMPLOYEE_ID": "YOUR_EMPLOYEE_ID_HERE", "SITE_ID": "5296", "USER_ID": "YOUR_USER_ID_HERE",
            "PHONE_NUMBER": "YOUR_PHONE_NUMBER_HERE", "LATITUDE": "22.5747936", "LONGITUDE": "88.28344",
            "AUTH_TOKEN": "YOUR_AUTH_TOKEN_HERE", "HTTP_SESSION_TOKEN": "YOUR_HTTP_SESSION_TOKEN_HERE",
            "SESSION_TOKEN": "YOUR_SESSION_TOKEN_HERE", "TARGET_STORE_ID": "5296"
        }
        self.config_data = default_config
        self.save_config()

    def display_config(self, show_sensitive: bool = False) -> None:
        print(f"\n{Colors.BOLD}--- BLINKIT CONFIGURATION ---{Colors.RESET}")
        sensitive_keys = {"AUTH_TOKEN", "HTTP_SESSION_TOKEN", "SESSION_TOKEN", "PHONE_NUMBER"}
        for key, value in self.config_data.items():
            display_value = value
            if key in sensitive_keys and not show_sensitive:
                display_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "*" * len(value)
            print(f"  {Colors.GREY}{key:<25}:{Colors.RESET} {display_value}")

    def update_config(self, key: str, value: str) -> None:
        if not key: return print_error("Key cannot be empty.")
        self.config_data[key] = value
        print_success(f"Updated {key}.")

    def interactive_menu(self) -> None:
        while True:
            print(f"\n{Colors.BOLD}--- BLINKIT CONFIG MANAGER ---{Colors.RESET}")
            print(f"  {Colors.GREEN}1.{Colors.RESET} View Configuration")
            print(f"  {Colors.GREEN}2.{Colors.RESET} View Configuration (Show Sensitive)")
            print(f"  {Colors.GREEN}3.{Colors.RESET} Update a Value")
            print(f"  {Colors.GREEN}4.{Colors.RESET} Save Changes")
            print(f"  {Colors.GREEN}5.{Colors.RESET} Exit")
            choice = input(f"\n{Colors.GREEN}>> Select an option:{Colors.RESET} ").strip()

            if choice == "1":
                self.display_config(show_sensitive=False)
            elif choice == "2":
                if input(f"{Colors.YELLOW}This will show sensitive tokens. Continue? (y/N): {Colors.RESET}").lower() == 'y':
                    self.display_config(show_sensitive=True)
            elif choice == "3":
                key = input(f"{Colors.GREEN}Enter key to update:{Colors.RESET} ").strip()
                if key in self.config_data:
                    new_value = input(f"{Colors.GREEN}Enter new value for {key}:{Colors.RESET} ").strip()
                    self.update_config(key, new_value)
                else:
                    print_error(f"Key '{key}' not found.")
            elif choice == "4":
                self.save_config()
            elif choice == "5":
                print_info("Goodbye!")
                break
            else:
                print_error("Invalid choice.")

def main():
    print_info("Starting Blinkit Configuration Manager...")
    env_path = sys.argv[1] if len(sys.argv) > 1 else ".env"
    try:
        manager = BlinkitConfigManager(env_path)
        manager.interactive_menu()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()