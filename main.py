from curl_cffi import requests
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz
from pyfiglet import Figlet
import shutil

wib = pytz.timezone('Asia/Jakarta')

class NaorisProtocol:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "chrome-extension://cpikalnagknmlfhnilhfelifgbollmmp",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Storage-Access": "active",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://naorisprotocol.network"
        self.PING_API = "https://beat.naorisprotocol.network"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}
        self.refresh_tokens = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        figlet = Figlet(font='slant')  # Ganti font di sini
        banner = figlet.renderText("Naoris Bot")

        terminal_width = shutil.get_terminal_size().columns
        centered_banner = "\n".join(line.center(terminal_width) for line in banner.splitlines())

        print(Fore.CYAN + Style.BRIGHT + centered_banner)
        print(Fore.GREEN + Style.BRIGHT + "Auto Ping Naoris by Bg WIN".center(terminal_width))


    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                response = await asyncio.to_thread(requests.get, "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt")
                response.raise_for_status()
                content = response.text
                with open(filename, 'w') as f:
                    f.write(content)
                self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        mask_account = account[:6] + '*' * 6 + account[-6:]
        return mask_account
    
    def print_message(self, address, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    async def generate_token(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/sec-api/auth/gt-event"
        data = json.dumps({"wallet_address":address})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=60, impersonate="chrome110")
                if response.status_code == 404:
                    return self.print_message(self.mask_account(address), proxy, Fore.RED, f"Generate Token Failed: {Fore.YELLOW+Style.BRIGHT}Join Testnet & Complete Required Tasks First")
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(self.mask_account(address), proxy, Fore.RED, f"Generate Token Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def refresh_token(self, address: str, use_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/sec-api/auth/refresh"
        data = json.dumps({"refreshToken":self.refresh_tokens[address]})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=60, impersonate="chrome110")
                if response.status_code == 401:
                    await self.process_generate_token(address, use_proxy)
                    data = json.dumps({"refreshToken":self.refresh_tokens[address]})
                    continue
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(self.mask_account(address), proxy, Fore.RED, f"Refreshing Token Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            
    async def wallet_details(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/sec-api/api/wallet-details"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=60, impersonate="chrome110")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(self.mask_account(address), proxy, Fore.RED, f"GET Wallet Details Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def add_whitelist(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/sec-api/api/addWhitelist"
        data = json.dumps({"walletAddress":address, "url":"naorisprotocol.network"})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=60, impersonate="chrome110")
                if response.status_code == 409:
                    return self.print_message(self.mask_account(address), proxy, Fore.RED, f"Add to Whitelist Failed: {Fore.YELLOW+Style.BRIGHT}URL Already Exists In Whitelist")
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(self.mask_account(address), proxy, Fore.RED, f"Add to Whitelist Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def toggle_activation(self, address: str, device_hash: int, state: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/sec-api/api/switch"
        data = json.dumps({"walletAddress":address, "state":state, "deviceHash":device_hash})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=60, impersonate="chrome110")
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(self.mask_account(address), proxy, Fore.RED, f"Turn On Protection Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def initiate_msg_product(self, address: str, device_hash: int, proxy=None, retries=5):
        url = f"{self.PING_API}/sec-api/api/htb-event"
        data = json.dumps({"inputData":{"walletAddress":address, "deviceHash":device_hash}})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=60, impersonate="chrome110")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(self.mask_account(address), proxy, Fore.RED, f"Initiate Message Production Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def perform_ping(self, address: str, proxy=None, retries=5):
        url = f"{self.PING_API}/api/ping"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": "2",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, json={}, proxy=proxy, timeout=60, impersonate="chrome110")
                if response.status_code == 410:
                    return response.text
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(self.mask_account(address), proxy, Fore.RED, f"PING Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")

    async def process_generate_token(self, address: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        token = None
        while token is None:
            token = await self.generate_token(address, proxy)
            if not token:
                await asyncio.sleep(5)
                proxy = self.rotate_proxy_for_account(address) if use_proxy else None
                continue
            
            self.access_tokens[address] = token["token"]
            self.refresh_tokens[address] = token["refreshToken"]

            self.print_message(address, proxy, Fore.GREEN, "Generate Token Success.")

            return self.access_tokens[address], self.refresh_tokens[address]

    async def process_refresh_token(self, address: str, use_proxy: bool):
        while True:
            await asyncio.sleep(30 * 60)
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            token = None
            while token is None:
                token = await self.refresh_token(address, use_proxy, proxy)
                if not token:
                    await asyncio.sleep(5)
                    proxy = self.rotate_proxy_for_account(address) if use_proxy else None
                    continue
                
                self.access_tokens[address] = token["token"]
                self.refresh_tokens[address] = token["refreshToken"]

                self.print_message(address, proxy, Fore.GREEN, "Refreshing Token Success")

    async def process_add_whitelist(self, address: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        whitelist = await self.add_whitelist(address, proxy)
        if whitelist and whitelist.get("message") == "url saved successfully":
            self.print_message(address, proxy, Fore.GREEN, "Add to Whitelist Success.")

        return True

    async def process_get_wallet_details(self, address: str, use_proxy: bool):
        await self.process_add_whitelist(address, use_proxy)

        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            total_earning = "N/A"

            wallet = await self.wallet_details(address, proxy)
            if wallet:
                total_earning = wallet.get("message", {}).get("totalEarnings", 0)

            self.print_message(address, proxy, Fore.WHITE, f"Earning Total: {total_earning} PTS")

            await asyncio.sleep(15 * 60)
    
    async def process_send_ping(self, address: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            ping = await self.perform_ping(address, proxy)
            if ping and ping.strip() == "Ping Success!!":
                self.print_message(address, proxy, Fore.GREEN, "PING Success")

            await asyncio.sleep(10)
        
    async def process_initiate_msg_product(self, address: str, device_hash: int, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            initiate = await self.initiate_msg_product(address, device_hash, proxy)
            if initiate and initiate.get("message") == "Message production initiated":
                self.print_message(address, proxy, Fore.GREEN, "Message Production Initiated")

            await asyncio.sleep(10 * 60)
    
    async def process_activate_toggle(self, address, device_hash, use_proxy):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            deactivate = await self.toggle_activation(address, device_hash, "OFF", proxy)
            if deactivate and deactivate.strip() in ["Session ended and daily usage updated", "No action needed"]:
                activate = await self.toggle_activation(address, device_hash, "ON", proxy)
                if activate and activate.strip() == "Session started":
                    self.print_message(address, proxy, Fore.GREEN, "Turn On Protection Success")

                    tasks = [
                        asyncio.create_task(self.process_initiate_msg_product(address, device_hash, use_proxy)),
                        asyncio.create_task(self.process_send_ping(address, use_proxy))
                    ]
                    await asyncio.gather(*tasks)
                else:
                    continue
            else:
                continue
        
    async def process_accounts(self, address: str, device_hash: int, use_proxy: bool):
        self.access_tokens[address], self.refresh_tokens[address]= await self.process_generate_token(address, use_proxy)
        if self.access_tokens[address] and self.refresh_tokens[address]:
            tasks = [
                asyncio.create_task(self.process_refresh_token(address, use_proxy)),
                asyncio.create_task(self.process_get_wallet_details(address, use_proxy)),
                asyncio.create_task(self.process_activate_toggle(address, device_hash, use_proxy))
            ]
            await asyncio.gather(*tasks)

    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED}No Accounts Loaded.{Style.RESET_ALL}")
                return

            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*65)

            while True:
                tasks = []
                for account in accounts:
                    if account:
                        address = account["Address"].lower()
                        device_hash = int(account["deviceHash"])

                        if address and device_hash:
                            tasks.append(asyncio.create_task(self.process_accounts(address, device_hash, use_proxy)))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = NaorisProtocol()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Naoris Protocol Node - BOT{Style.RESET_ALL}                                       "                              
        )
