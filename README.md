


⚠️ Important Disclaimer

This is an unofficial tool developed for personal use and is not affiliated with, endorsed, or supported by Blinkit.

Use at Your Own Risk: This script interacts directly with Blinkit's private APIs. Using it may be against their Terms of Service and could potentially lead to your account being flagged or suspended. The author is not responsible for any consequences that arise from the use of this software.

Handle with Care: This tool requires your sensitive, personal authentication tokens to function. You are responsible for keeping them secure.

Intended for Educational Purposes: This project was created to overcome a personal challenge and to explore API automation. Please use this tool responsibly and ethically.

Project Motivation

This script was born out of necessity. In a competitive environment where delivery slots were filled in seconds by users with 5G internet and high-performance phones, it became nearly impossible to book a slot manually. This toolkit was developed by intercepting the official Store Ops application's API calls to level the playing field, allowing for automated and programmatic interaction with the system.

🔑 Critical Prerequisite: Capturing Your Authentication Token

The entire toolkit depends on a valid AUTH_TOKEN to communicate with the Blinkit API. This token is only valid for 24 hours after you log in to the Store Ops app, so you will need to refresh it daily.

The most challenging step is capturing this token, as the application has measures to detect and block standard proxies.

How to Capture the Token:
You must intercept the HTTPS network traffic from your mobile device. This is a complex process that requires specialized tools and knowledge.

Required Tools: You will need a network sniffing application like Mitmproxy, Charles Proxy, or Proxyman.

Bypassing Security: You must figure out how to bypass the app's security measures (like certificate pinning or VPN detection) that prevent traffic interception. This often involves patching the app or using advanced rooting/jailbreaking techniques.

Find the Token: Once you are successfully intercepting the traffic, inspect the Request Headers of any API call made to storeops-api.blinkit.com. The Authorization header will contain your token in the format Bearer [YOUR_AUTH_TOKEN].

This step is for advanced users. Without a valid token, the scripts will not work.

⚙️ Configuration

All personal variables and authentication tokens must be stored in the .env file.

For your safety and convenience, it is highly recommended to use the provided settings manager to update your credentials.

code
Bash
download
content_copy
expand_less
python setting.py

This script provides a safe, interactive menu to change your tokens, IDs, and other variables without the risk of corrupting the .env file format.

🚀 Usage Guide
book.py - The Slot Booker

This is the primary tool for booking delivery slots. Simply run the script to access the main menu for automated and manual booking functionalities.

code
Bash
download
content_copy
expand_less
python book.py
mst.py - Task and Status Manager

This script is designed for managing your status during a shift. Its most powerful feature is the Ghost Mode, which allows you to take a "virtual break."

When activated, Ghost Mode will set your status to OFFLINE and then instantly back to ONLINE in a continuous loop. This action can push your position in the order queue, effectively giving you a break without losing your place entirely. The loop will run until you manually stop the script.

code
Bash
download
content_copy
expand_less
python mst.py
🛑 IMPORTANT USAGE WARNING

DO NOT BOOK SLOTS ON STORE ID 5296

This Store ID (also known as Site ID) may be included as a default example in the configuration files. This is my personal store, and I have shared this tool to help others, not to create more competition for myself.

Please find your own Store ID and update it immediately using setting.py. Failure to do so is a misuse of this tool.
