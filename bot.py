import os
import sys
import time
import random
import threading
import requests
from datetime import datetime
import pytz
from colorama import Fore, Style, init
from solders.keypair import Keypair
import warnings

warnings.filterwarnings('ignore')
if not sys.warnoptions:
    os.environ["PYTHONWARNINGS"] = "ignore"

init(autoreset=True)

class BotTemplate:
    def __init__(self):
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBvdXRob2JtcXZmYm5ueXlhbWt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUxOTU4ODcsImV4cCI6MjA5MDc3MTg4N30.MyqPl2IKQjDw3Tjf8m9T-0-NbD0GcGjRmSjWFLPyC30"
        self.headers_default = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "apikey": self.api_key,
            "content-type": "application/json",
            "origin": "https://axiomoracle.xyz",
            "referer": "https://axiomoracle.xyz/",
            "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
        }
        self.headers_checkin = self.headers_default.copy()
        self.headers_checkin.update({
            "authorization": f"Bearer {self.api_key}",
            "content-profile": "public",
            "x-client-info": "supabase-js-web/2.103.3"
        })
        self.log_lock = threading.Lock()

    def get_wib_time(self):
        try:
            wib = pytz.timezone('Asia/Jakarta')
            return datetime.now(wib).strftime('%H:%M:%S')
        except Exception:
            return datetime.now().strftime('%H:%M:%S')

    def log(self, message, level="INFO"):
        try:
            time_str = self.get_wib_time()
            
            if level == "INFO":
                color = Fore.CYAN
                symbol = "[INFO]"
            elif level == "SUCCESS":
                color = Fore.GREEN
                symbol = "[SUCCESS]"
            elif level == "ERROR":
                color = Fore.RED
                symbol = "[ERROR]"
            elif level == "WARNING":
                color = Fore.YELLOW
                symbol = "[WARNING]"
            elif level == "CYCLE":
                color = Fore.MAGENTA
                symbol = "[CYCLE]"
            else:
                color = Fore.WHITE
                symbol = "[LOG]"
            
            with self.log_lock:
                print(f"[{time_str}] {color}{symbol} {message}{Style.RESET_ALL}")
        except Exception:
            pass

    def read_file(self, filename, optional=False):
        try:
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            if not optional:
                self.log(f"File {filename} not found!", "ERROR")
            return []
        except Exception as e:
            self.log(f"Error reading file {filename}: {e}", "ERROR")
            return []

    def get_wallet_from_private_key(self, private_key_str):
        try:
            keypair = Keypair.from_base58_string(private_key_str)
            return str(keypair.pubkey())
        except Exception as e:
            self.log(f"Failed to process private key: {e}", "ERROR")
            return None

    def get_rank(self, wallet, proxy_dict):
        url = "https://pouthobmqvfbnnyyamkt.supabase.co/functions/v1/node-api/leaderboard"
        try:
            res = requests.get(url, headers=self.headers_default, proxies=proxy_dict, timeout=60)
            if res.status_code in [200, 201]:
                data = res.json()
                for item in data.get('leaderboard', []):
                    if item.get('wallet') == wallet:
                        return item.get('rank')
        except Exception:
            pass
        return "Unranked"

    def get_status(self, wallet, proxy_dict):
        url = f"https://pouthobmqvfbnnyyamkt.supabase.co/functions/v1/node-api/status?wallet={wallet}"
        try:
            res = requests.get(url, headers=self.headers_default, proxies=proxy_dict, timeout=60)
            if res.status_code in [200, 201]:
                return res.json()
        except Exception:
            pass
        return {}

    def get_dashboard_summary(self, wallet, proxy_dict):
        url = "https://pouthobmqvfbnnyyamkt.supabase.co/rest/v1/rpc/get_dashboard_summary_cached"
        payload = {"_wallet": wallet}
        try:
            res = requests.post(url, json=payload, headers=self.headers_checkin, proxies=proxy_dict, timeout=60)
            if res.status_code in [200, 201]:
                return res.json()
        except Exception:
            pass
        return {}

    def register(self, wallet, proxy_dict):
        url = "https://pouthobmqvfbnnyyamkt.supabase.co/functions/v1/node-api/register"
        payload = {"wallet_address": wallet}
        try:
            res = requests.post(url, json=payload, headers=self.headers_default, proxies=proxy_dict, timeout=60)
            if res.status_code in [200, 201]:
                self.log("Register Success", "SUCCESS")
                return True
            else:
                self.log(f"Register Failed | Status: {res.status_code}", "ERROR")
        except Exception as e:
            self.log(f"Register Error: {e}", "ERROR")
        return False

    def daily_checkin(self, wallet, proxy_dict):
        url = "https://pouthobmqvfbnnyyamkt.supabase.co/rest/v1/rpc/daily_checkin"
        payload = {"_wallet": wallet}
        try:
            res = requests.post(url, json=payload, headers=self.headers_checkin, proxies=proxy_dict, timeout=60)
            if res.status_code in [200, 201, 204]:
                self.log("Daily Check-in Success", "SUCCESS")
            else:
                self.log(f"Daily Check-in Failed | Status: {res.status_code}", "ERROR")
        except Exception as e:
            self.log(f"Daily Check-in Error: {e}", "ERROR")

    def send_heartbeat(self, wallet, proxy_dict):
        url = "https://pouthobmqvfbnnyyamkt.supabase.co/functions/v1/node-api/heartbeat"
        payload = {
            "wallet_address": wallet
        }
        try:
            res = requests.post(url, json=payload, headers=self.headers_default, proxies=proxy_dict, timeout=60)
            if res.status_code in [200, 201]:
                data = res.json()
                if data.get("success"):
                    return True, data.get("throttled", False), data
                else:
                    self.log(f"Heartbeat returned false: {data}", "WARNING")
            else:
                self.log(f"Heartbeat Failed | Status: {res.status_code}", "ERROR")
        except Exception as e:
            self.log(f"Heartbeat Error: {e}", "ERROR")
        return False, False, {}

    def get_activity(self, wallet, proxy_dict):
        url = f"https://pouthobmqvfbnnyyamkt.supabase.co/functions/v1/node-api/activity?wallet={wallet}"
        try:
            res = requests.get(url, headers=self.headers_default, proxies=proxy_dict, timeout=60)
            if res.status_code in [200, 201]:
                data = res.json()
                streak = data.get("streak", 0)
                days = data.get("days", [])
                validations = 0
                hours = 0
                if len(days) > 0:
                    validations = days[0].get("validations", 0)
                    hours = days[0].get("hours", 0)
                return streak, validations, hours
        except Exception as e:
            self.log(f"Activity Error: {e}", "ERROR")
        return 0, 0, 0

    def print_banner(self):
        try:
            banner = f"""
{Fore.CYAN}AXIOM BOT{Style.RESET_ALL}
{Fore.WHITE}By: FEBRIYAN{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
"""
            print(banner)
        except Exception:
            pass

    def show_menu(self):
        try:
            print(f"{Fore.CYAN}Select Mode:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}1. Run with proxy")
            print(f"2. Run without proxy{Style.RESET_ALL}")
            print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
            
            while True:
                try:
                    choice = input(f"{Fore.GREEN}Enter your choice (1/2): {Style.RESET_ALL}").strip()
                    if choice in ['1', '2']:
                        return choice
                    else:
                        print(f"{Fore.RED}Invalid choice! Please enter 1 or 2.{Style.RESET_ALL}")
                except KeyboardInterrupt:
                    print(f"\n{Fore.RED}Program terminated by user.{Style.RESET_ALL}")
                    sys.exit(0)
                except Exception:
                    return '2'
        except Exception:
            return '2'

    def countdown(self, seconds):
        try:
            for i in range(seconds, 0, -1):
                hours = i // 3600
                minutes = (i % 3600) // 60
                secs = i % 60
                print(f"\r[COUNTDOWN] Next cycle in: {hours:02d}:{minutes:02d}:{secs:02d} ", end="", flush=True)
                time.sleep(1)
            print("\r" + " " * 60 + "\r", end="", flush=True)
        except Exception:
            pass

    def run(self):
        try:
            os.system('clear' if os.name == 'posix' else 'cls')
            self.print_banner()

            private_keys = self.read_file('accounts.txt')

            if not private_keys:
                self.log("No private keys in accounts.txt. Bot stopped.", "ERROR")
                return

            choice = self.show_menu()
            use_proxy = choice == '1'
            
            proxies = []
            if use_proxy:
                proxies = self.read_file('proxy.txt', optional=True)
                self.log("Running with proxy", "INFO")
            else:
                self.log("Running without proxy", "INFO")

            total_accounts = len(private_keys)
            self.log(f"Loaded {total_accounts} accounts successfully", "SUCCESS")
            
            print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}\n")

            accounts_state = []
            for i, pk in enumerate(private_keys):
                try:
                    wallet = self.get_wallet_from_private_key(pk)
                    if not wallet:
                        continue
                    
                    proxy_dict = None
                    if use_proxy and proxies:
                        proxy_url = proxies[i % len(proxies)]
                        proxy_dict = {"http": proxy_url, "https": proxy_url}

                    self.log(f"Initializing Account {i+1}", "INFO")
                    self.log(f"Wallet       : {wallet[:6]}...{wallet[-4:]}", "INFO")
                    self.register(wallet, proxy_dict)
                    
                    status_data = self.get_status(wallet, proxy_dict)
                    uptime = status_data.get('lifetime_uptime', 0)
                    
                    self.log(f"Initial Uptime: {uptime}", "INFO")
                    rank = self.get_rank(wallet, proxy_dict)
                    self.log(f"Current Rank : {rank}", "INFO")
                    
                    accounts_state.append({
                        "wallet": wallet,
                        "proxy": proxy_dict,
                        "uptime": uptime,
                        "last_checkin": 0,
                        "index": i + 1
                    })
                except Exception as e:
                    self.log(f"Error initializing account {i+1}: {e}", "ERROR")

            print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}\n")

            cycle = 1
            while True:
                try:
                    self.log(f"Cycle {cycle} Started", "CYCLE")
                    print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
                    
                    success_count = 0
                    
                    for acc in accounts_state:
                        try:
                            wallet = acc['wallet']
                            proxy_dict = acc['proxy']
                            now = time.time()
                            
                            self.log(f"Starting Account {acc['index']}/{len(accounts_state)}", "INFO")
                            self.log(f"Wallet       : {wallet[:6]}...{wallet[-4:]}", "INFO")
                            
                            if now - acc['last_checkin'] >= 86400:
                                self.daily_checkin(wallet, proxy_dict)
                                acc['last_checkin'] = time.time()
                            
                            self.log("Sending Heartbeat...", "INFO")
                            is_success, is_throttled, hb_data = self.send_heartbeat(wallet, proxy_dict)
                            
                            if is_success:
                                if is_throttled:
                                    self.log("Heartbeat Throttled (Too Fast)", "WARNING")
                                    success_count += 1
                                else:
                                    self.log("Heartbeat Success", "SUCCESS")
                                    
                                    dash_data = self.get_dashboard_summary(wallet, proxy_dict)
                                    status_data = self.get_status(wallet, proxy_dict)
                                    
                                    node_active = status_data.get("node_active", True)
                                    boost = dash_data.get("boost", hb_data.get("referral_multiplier", 1))
                                    accuracy = dash_data.get("node_accuracy", hb_data.get("consensus_accuracy", 100))
                                    uptime = status_data.get("lifetime_uptime", hb_data.get("lifetime_uptime", acc['uptime']))
                                    
                                    acc['uptime'] = uptime
                                    
                                    self.log(f"Node Active  : {node_active}", "INFO")
                                    self.log(f"Accuracy     : {accuracy}%", "INFO")
                                    self.log(f"Boost        : {boost}x", "INFO")
                                    self.log(f"Uptime       : {uptime}", "INFO")
                                    
                                    rank = self.get_rank(wallet, proxy_dict)
                                    self.log(f"Rank         : {rank}", "INFO")
                                    
                                    streak, validations, hours = self.get_activity(wallet, proxy_dict)
                                    self.log(f"Streak       : {streak} Days", "INFO")
                                    self.log(f"Validations  : {validations}", "INFO")
                                    self.log(f"Hours Active : {hours} Hrs", "INFO")
                                    
                                    success_count += 1
                            
                            if acc['index'] < len(accounts_state):
                                print(f"{Fore.WHITE}............................................................{Style.RESET_ALL}")
                                time.sleep(3)
                        except Exception as e:
                            self.log(f"Error processing account {acc['index']}: {e}", "ERROR")
                            time.sleep(3)
                    
                    print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
                    self.log(f"Cycle {cycle} Complete | Success: {success_count}/{len(accounts_state)}", "CYCLE")
                    print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
                    
                    cycle += 1
                    self.countdown(59)
                except Exception as e:
                    self.log(f"Cycle error: {e}", "ERROR")
                    time.sleep(5)
        except Exception as e:
            self.log(f"Critical error in run: {e}", "ERROR")

if __name__ == "__main__":
    try:
        bot = BotTemplate()
        bot.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Bot stopped by user (Ctrl+C).{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)
