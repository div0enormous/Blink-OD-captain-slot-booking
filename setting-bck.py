
import os
import sys
from pathlib import Path
import json
from typing import Dict, Any, Optional

class BlinkitConfigManager:
    def __init__(self, env_file_path: str = ".env"):
        self.env_file_path = Path(env_file_path)
        self.config_data = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from .env file"""
        if not self.env_file_path.exists():
            print(f"âš ï¸  .env file not found at {self.env_file_path}")
            print("Creating a new configuration file...")
            self.create_default_config()
            return
        
        try:
            with open(self.env_file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.config_data[key.strip()] = value.strip()
            
            print(f"âœ… Configuration loaded from {self.env_file_path}")
        
        except Exception as e:
            print(f"âŒ Error loading configuration: {e}")
            sys.exit(1)
    
    def save_config(self) -> None:
        """Save configuration back to .env file"""
        try:
            # Create backup
            backup_path = Path(f"{self.env_file_path}.backup")
            if self.env_file_path.exists():
                import shutil
                shutil.copy2(self.env_file_path, backup_path)
                print(f"ðŸ“‹ Backup created: {backup_path}")
            
            # Write new configuration
            with open(self.env_file_path, 'w', encoding='utf-8') as file:
                file.write("# Blinkit Slot Checker Configuration\n")
                file.write("# Fill in your actual values below (DO NOT COMMIT THIS FILE TO VERSION CONTROL)\n\n")
                
                # Group configurations
                groups = {
                    "Device Information": [
                        "DEVICE_MANUFACTURER", "APP_VERSION_CODE", "VERSION_NAME", 
                        "DEVICE_ID", "VERSION_CODE", "CLIENT_NAME", "MODEL", 
                        "DEVICE_HARDWARE_TYPE", "APP_VERSION", "VERSION"
                    ],
                    "App Settings": [
                        "APP_THEME", "APP_APPEARANCE", "SYSTEM_APPEARANCE", 
                        "VOICE_OVER_ENABLED", "APP_LOCALE", "ROLE"
                    ],
                    "User Information (REQUIRED - Update these with your actual values)": [
                        "EMPLOYEE_ID", "SITE_ID", "USER_ID", "PHONE_NUMBER", 
                        "LATITUDE", "LONGITUDE"
                    ],
                    "Authentication Tokens (REQUIRED - Update these with your actual tokens)": [
                        "AUTH_TOKEN", "HTTP_SESSION_TOKEN", "SESSION_TOKEN"
                    ],
                    "Static Cookie (Keep this as-is)": [
                        "CFUVID_COOKIE"
                    ],
                    "User Agent String": [
                        "USER_AGENT"
                    ],
                    "Prefered slot id": [
                        "TARGET_STORE_ID"
                    ]
                }
                
                for group_name, keys in groups.items():
                    file.write(f"# {group_name}\n")
                    for key in keys:
                        if key in self.config_data:
                            file.write(f"{key}={self.config_data[key]}\n")
                    file.write("\n")
                
                # Add any remaining keys not in groups
                remaining_keys = set(self.config_data.keys()) - set().union(*groups.values())
                if remaining_keys:
                    file.write("# Additional Configuration\n")
                    for key in sorted(remaining_keys):
                        file.write(f"{key}={self.config_data[key]}\n")
                
                file.write("\n# Note: The following are dynamically generated and don't need to be set:\n")
                file.write("# - Request ID (generated per request)\n")
                file.write("# - __cf_bm cookie (generated per request)\n")
                file.write("# - __cfruid cookie (generated per request)\n")
            
            print(f"âœ… Configuration saved to {self.env_file_path}")
        
        except Exception as e:
            print(f"âŒ Error saving configuration: {e}")
    
    def create_default_config(self) -> None:
        """Create a default configuration template"""
        default_config = {
            "DEVICE_MANUFACTURER": "OPPO",
            "APP_VERSION_CODE": "154501",
            "VERSION_NAME": "15.45.1",
            "DEVICE_ID": "8f92524ac3ab0a43",
            "VERSION_CODE": "154501",
            "CLIENT_NAME": "storeops-app",
            "MODEL": "CPH1819",
            "DEVICE_HARDWARE_TYPE": "NON_HHD",
            "APP_VERSION": "15.46.0",
            "VERSION": "15.46.0",
            "APP_THEME": "default",
            "APP_APPEARANCE": "LIGHT",
            "SYSTEM_APPEARANCE": "UNSPECIFIED",
            "VOICE_OVER_ENABLED": "0",
            "APP_LOCALE": "en",
            "ROLE": "OD_CAPTAIN",
            "EMPLOYEE_ID": "YOUR_EMPLOYEE_ID_HERE",
            "SITE_ID": "5296",
            "USER_ID": "YOUR_USER_ID_HERE",
            "PHONE_NUMBER": "YOUR_PHONE_NUMBER_HERE",
            "LATITUDE": "22.5747936",
            "LONGITUDE": "88.28344",
            "AUTH_TOKEN": "YOUR_AUTH_TOKEN_HERE",
            "HTTP_SESSION_TOKEN": "YOUR_HTTP_SESSION_TOKEN_HERE",
            "SESSION_TOKEN": "YOUR_SESSION_TOKEN_HERE",
            "CFUVID_COOKIE": "5x422DTLm.r7_atNJrAj_oLraFONgPZx152h.zLrbEo-1756816602998-0.0.1.1-604800000",
            "USER_AGENT": "com.blinkitstoreops/154501 (Linux; U; Android 10; en; CPH1819; Build/QP1A.190711.020; Cronet/140.0.7289.0)",
            "TARGET_STORE_ID": "5296"
        }
        
        self.config_data = default_config
        self.save_config()
    
    def display_config(self, show_sensitive: bool = False) -> None:
        """Display current configuration"""
        print("\n" + "="*60)
        print("ðŸ“± BLINKIT CONFIGURATION MANAGER")
        print("="*60)
        
        sensitive_keys = {"AUTH_TOKEN", "HTTP_SESSION_TOKEN", "SESSION_TOKEN", "PHONE_NUMBER"}
        
        categories = {
            "ðŸ“± Device Information": [
                "DEVICE_MANUFACTURER", "MODEL", "APP_VERSION", "VERSION_NAME", "DEVICE_ID"
            ],
            "âš™ï¸  App Settings": [
                "APP_THEME", "APP_APPEARANCE", "APP_LOCALE", "ROLE"
            ],
            "ðŸ‘¤ User Information": [
                "EMPLOYEE_ID", "SITE_ID", "USER_ID", "PHONE_NUMBER"
            ],
            "ðŸ” Authentication": [
                "AUTH_TOKEN", "HTTP_SESSION_TOKEN", "SESSION_TOKEN"
            ],
            "ðŸ“ Location": [
                "LATITUDE", "LONGITUDE", "TARGET_STORE_ID"
            ]
        }
        
        for category, keys in categories.items():
            print(f"\n{category}:")
            print("-" * 40)
            for key in keys:
                if key in self.config_data:
                    value = self.config_data[key]
                    
                    # Mask sensitive data
                    if key in sensitive_keys and not show_sensitive:
                        if len(value) > 10:
                            value = value[:6] + "*" * (len(value) - 10) + value[-4:]
                        else:
                            value = "*" * len(value)
                    
                    print(f"  {key:<20}: {value}")
    
    def update_config(self, key: str, value: str) -> None:
        """Update a configuration value"""
        if not key:
            print("âŒ Key cannot be empty")
            return
        
        old_value = self.config_data.get(key, "NOT SET")
        self.config_data[key] = value
        
        print(f"âœ… Updated {key}")
        if key not in {"AUTH_TOKEN", "HTTP_SESSION_TOKEN", "SESSION_TOKEN", "PHONE_NUMBER"}:
            print(f"   Old: {old_value}")
            print(f"   New: {value}")
        else:
            print(f"   Value updated (sensitive data masked)")
    
    def get_config_value(self, key: str) -> Optional[str]:
        """Get a configuration value"""
        return self.config_data.get(key)
    
    def delete_config(self, key: str) -> None:
        """Delete a configuration key"""
        if key in self.config_data:
            del self.config_data[key]
            print(f"âœ… Deleted {key}")
        else:
            print(f"âŒ Key '{key}' not found")
    
    def interactive_menu(self) -> None:
        """Interactive menu for configuration management"""
        while True:
            print("\n" + "="*60)
            print("ðŸ”§ BLINKIT CONFIG MANAGER - MAIN MENU")
            print("="*60)
            print("1. ðŸ“‹ View Configuration")
            print("2. ðŸ“‹ View Configuration (Show Sensitive Data)")
            print("3. âœï¸  Update Configuration")
            print("4. âž• Add New Configuration")
            print("5. ðŸ—‘ï¸  Delete Configuration")
            print("6. ðŸ’¾ Save Changes")
            print("7. ðŸ”„ Reload from File")
            print("8. ðŸ“¤ Export to JSON")
            print("9. âŒ Exit")
            
            choice = input("\nðŸ”¹ Enter your choice (1-9): ").strip()
            
            if choice == "1":
                self.display_config(show_sensitive=False)
            
            elif choice == "2":
                confirm = input("âš ï¸  This will show sensitive tokens. Continue? (y/N): ")
                if confirm.lower() == 'y':
                    self.display_config(show_sensitive=True)
            
            elif choice == "3":
                self.update_menu()
            
            elif choice == "4":
                key = input("ðŸ“ Enter new configuration key: ").strip()
                value = input("ðŸ“ Enter value: ").strip()
                if key and value:
                    self.update_config(key, value)
                else:
                    print("âŒ Both key and value are required")
            
            elif choice == "5":
                key = input("ðŸ—‘ï¸  Enter key to delete: ").strip()
                if key:
                    self.delete_config(key)
                else:
                    print("âŒ Key is required")
            
            elif choice == "6":
                self.save_config()
            
            elif choice == "7":
                self.load_config()
            
            elif choice == "8":
                self.export_to_json()
            
            elif choice == "9":
                print("ðŸ‘‹ Goodbye!")
                break
            
            else:
                print("âŒ Invalid choice. Please select 1-9.")
    
    def update_menu(self) -> None:
        """Menu for updating configurations"""
        print("\nðŸ”§ Quick Update Options:")
        print("-" * 40)
        
        quick_options = {
            "1": ("EMPLOYEE_ID", "Employee ID"),
            "2": ("AUTH_TOKEN", "Auth Token"),
            "3": ("HTTP_SESSION_TOKEN", "HTTP Session Token"),
            "4": ("SESSION_TOKEN", "Session Token"),
            "5": ("PHONE_NUMBER", "Phone Number"),
            "6": ("USER_ID", "User ID"),
            "7": ("SITE_ID", "Site ID"),
            "8": ("APP_VERSION", "App Version"),
            "9": ("TARGET_STORE_ID", "Target Store ID"),
            "10": ("LATITUDE", "Latitude"),
            "11": ("LONGITUDE", "Longitude"),
        }
        
        for num, (key, desc) in quick_options.items():
            current_value = self.config_data.get(key, "NOT SET")
            if key in {"AUTH_TOKEN", "HTTP_SESSION_TOKEN", "SESSION_TOKEN", "PHONE_NUMBER"}:
                if current_value != "NOT SET":
                    current_value = current_value[:6] + "***" + current_value[-4:] if len(current_value) > 10 else "***"
            print(f"{num:2}. {desc:<20}: {current_value}")
        
        print("12. Custom key")
        print("0.  Back to main menu")
        
        choice = input("\nðŸ”¹ Select option: ").strip()
        
        if choice == "0":
            return
        elif choice == "12":
            key = input("ðŸ“ Enter custom key: ").strip()
            if not key:
                print("âŒ Key cannot be empty")
                return
        elif choice in quick_options:
            key = quick_options[choice][0]
        else:
            print("âŒ Invalid choice")
            return
        
        current_value = self.config_data.get(key, "NOT SET")
        print(f"\nðŸ“‹ Current value for {key}: {current_value}")
        
        new_value = input("ðŸ“ Enter new value (or press Enter to cancel): ").strip()
        if new_value:
            self.update_config(key, new_value)
        else:
            print("âŒ Update cancelled")
    
    def export_to_json(self) -> None:
        """Export configuration to JSON file"""
        try:
            export_file = f"blinkit_config_export_{int(import_time.time())}.json"
            
            # Create export data (mask sensitive info)
            export_data = {}
            sensitive_keys = {"AUTH_TOKEN", "HTTP_SESSION_TOKEN", "SESSION_TOKEN", "PHONE_NUMBER"}
            
            for key, value in self.config_data.items():
                if key in sensitive_keys:
                    export_data[key] = "***MASKED***"
                else:
                    export_data[key] = value
            
            with open(export_file, 'w', encoding='utf-8') as file:
                json.dump(export_data, file, indent=2)
            
            print(f"âœ… Configuration exported to {export_file}")
            print("âš ï¸  Sensitive data has been masked in the export")
        
        except Exception as e:
            print(f"âŒ Error exporting configuration: {e}")

def main():
    """Main function"""
    import time as import_time
    
    print("ðŸš€ Starting Blinkit Configuration Manager...")
    
    # Check if .env file path is provided as argument
    env_path = ".env"
    if len(sys.argv) > 1:
        env_path = sys.argv[1]
    
    try:
        manager = BlinkitConfigManager(env_path)
        manager.interactive_menu()
    except KeyboardInterrupt:
        print("\n\nðŸ‘‹ Goodbye!")
    except Exception as e:
        print(f"âŒ Unexpected error: {e}")

if __name__ == "__main__":
    main()
