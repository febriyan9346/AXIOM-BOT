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
            "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
        }
        self.headers_checkin = self.headers_default.copy()
        self.headers_checkin.update({
            "authorization": f"Bearer {self.api_key}",
            "content-profile": "public",
            "x-client-info": "supabase-js-web/2.102.1"
        })
        self.log_lock = threading.Lock()
        self.feeds = self.fetch_okx_tickers()

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

    def fetch_okx_tickers(self):
        self.log("Fetching ticker data from OKX...", "INFO")
        try:
            res = requests.get("https://www.okx.com/api/v5/market/tickers?instType=SPOT", timeout=10)
            data = res.json()
            feeds = []
            for item in data.get('data', []):
                feed = item['instId'].replace('-', '/')
                feeds.append(feed)
            self.log(f"Successfully fetched {len(feeds)} tickers from OKX.", "SUCCESS")
            return feeds
        except Exception as e:
            self.log(f"Failed to fetch OKX tickers, using fallback list.", "WARNING")
            return ["HNT/USD", "BTC/USDT", "ETH/USDT", "SOL/USDT", "SUI/USDT"]

    def get_rank(self, wallet, proxy_dict):
        url = "https://pouthobmqvfbnnyyamkt.supabase.co/functions/v1/node-api/leaderboard"
        try:
            res = requests.get(url, headers=self.headers_default, proxies=proxy_dict, timeout=15)
            if res.status_code in [200, 201]:
                data = res.json()
                for item in data.get('leaderboard', []):
                    if item.get('wallet') == wallet:
                        return item.get('rank')
        except Exception:
            pass
        return "Unranked"

    def register(self, wallet, proxy_dict):
        url = "https://pouthobmqvfbnnyyamkt.supabase.co/functions/v1/node-api/register"
        payload = {"wallet_address": wallet}
        try:
            res = requests.post(url, json=payload, headers=self.headers_default, proxies=proxy_dict, timeout=15)
            if res.status_code in [200, 201]:
                data = res.json()
                self.log("Register Success", "SUCCESS")
                return data.get('stats', {}).get('total_points', 0)
            else:
                self.log(f"Register Failed | Status: {res.status_code}", "ERROR")
        except Exception as e:
            self.log(f"Register Error: {e}", "ERROR")
        return 0

    def daily_checkin(self, wallet, proxy_dict):
        url = "https://pouthobmqvfbnnyyamkt.supabase.co/rest/v1/rpc/daily_checkin"
        payload = {"_wallet": wallet}
        try:
            res = requests.post(url, json=payload, headers=self.headers_checkin, proxies=proxy_dict, timeout=15)
            if res.status_code in [200, 201, 204]:
                self.log("Daily Check-in Success", "SUCCESS")
            else:
                self.log(f"Daily Check-in Failed | Status: {res.status_code}", "ERROR")
        except Exception as e:
            self.log(f"Daily Check-in Error: {e}", "ERROR")

    def submit_points(self, wallet, feed, proxy_dict):
        url = "https://pouthobmqvfbnnyyamkt.supabase.co/functions/v1/node-api/submit"
        payload = {
            "wallet_address": wallet,
            "points": 5,
            "feed": feed,
            "accepted": True,
            "accuracy": 100
        }
        try:
            res = requests.post(url, json=payload, headers=self.headers_default, proxies=proxy_dict, timeout=15)
            if res.status_code in [200, 201]:
                data = res.json()
                if data.get("success"):
                    return data.get('points_added', 5)
            else:
                self.log(f"Submit Points Failed | Status: {res.status_code}", "ERROR")
        except Exception as e:
            self.log(f"Submit Points Error: {e}", "ERROR")
        return 0

    def ping_uptime(self, wallet, proxy_dict):
        url = "https://pouthobmqvfbnnyyamkt.supabase.co/functions/v1/node-api/uptime"
        payload = {
            "wallet_address": wallet,
            "seconds": 60
        }
        try:
            res = requests.post(url, json=payload, headers=self.headers_default, proxies=proxy_dict, timeout=15)
            if res.status_code in [200, 201]:
                self.log("Ping Uptime 60s Success", "SUCCESS")
            else:
                self.log(f"Ping Uptime Failed | Status: {res.status_code}", "ERROR")
        except Exception as e:
            self.log(f"Ping Uptime Error: {e}", "ERROR")

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
                    total_points = self.register(wallet, proxy_dict)
                    self.log(f"Initial Pts  : {total_points}", "INFO")
                    rank = self.get_rank(wallet, proxy_dict)
                    self.log(f"Current Rank : {rank}", "INFO")
                    
                    accounts_state.append({
                        "wallet": wallet,
                        "proxy": proxy_dict,
                        "total_points": total_points,
                        "last_checkin": 0,
                        "last_uptime": 0,
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
                            
                            if now - acc['last_uptime'] >= 60:
                                self.ping_uptime(wallet, proxy_dict)
                                acc['last_uptime'] = time.time()

                            feed = random.choice(self.feeds) if self.feeds else "HNT/USD"
                            added_points = self.submit_points(wallet, feed, proxy_dict)
                            
                            if added_points > 0:
                                acc['total_points'] += added_points
                                self.log(f"Farming Success", "SUCCESS")
                                self.log(f"Reward       : +{added_points} Pts", "INFO")
                                self.log(f"Feed         : {feed}", "INFO")
                                self.log(f"Total Points : {acc['total_points']}", "INFO")
                                rank = self.get_rank(wallet, proxy_dict)
                                self.log(f"Rank         : {rank}", "INFO")
                                success_count += 1
                            
                            if acc['index'] < len(accounts_state):
                                print(f"{Fore.WHITE}............................................................{Style.RESET_ALL}")
                                time.sleep(random.randint(1, 3))
                        except Exception as e:
                            self.log(f"Error processing account {acc['index']}: {e}", "ERROR")
                            time.sleep(2)
                    
                    print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
                    self.log(f"Cycle {cycle} Complete | Success: {success_count}/{len(accounts_state)}", "CYCLE")
                    print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
                    
                    cycle += 1
                    self.countdown(30)
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
