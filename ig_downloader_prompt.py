import logging
import os
import sys
import json
import time
import requests
from datetime import datetime
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

class InstagramDownloader:
    """Enhanced Instagram Downloader with visual browser and additional features"""
    
    def __init__(self):
        self.setup_logging()
        self.download_history = []
        self.session_stats = {
            'stories_downloaded': 0,
            'reels_downloaded': 0,
            'total_links': 0,
            'session_start': datetime.now()
        }
    
    def setup_logging(self):
        """Setup enhanced logging with colors"""
        class ColoredFormatter(logging.Formatter):
            COLORS = {
                'DEBUG': Fore.CYAN,
                'INFO': Fore.GREEN,
                'WARNING': Fore.YELLOW,
                'ERROR': Fore.RED,
                'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
            }

            def format(self, record):
                log_color = self.COLORS.get(record.levelname, '')
                record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
                return super().format(record)

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO,
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        
        self.logger = logging.getLogger(__name__)
        for handler in self.logger.handlers:
            handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))

    def print_banner(self):
        """Display enhanced application banner"""
        banner = f"""
{Fore.CYAN + Style.BRIGHT}
╔══════════════════════════════════════════════════════════════════════╗
║                       INSTAGRAM DOWNLOADER PRO                       ║
║                        Visual Browser Edition                        ║
║                                                                      ║
║  📸 Download Instagram Stories & Reels with Advanced Features        ║
║  🎯 Visual Browser Mode • Link Validation • Download History        ║
║  📊 Session Statistics • Enhanced Error Handling                    ║
╚══════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
        """
        print(banner)

    def print_menu(self):
        """Display enhanced main menu"""
        menu = f"""
{Fore.YELLOW + Style.BRIGHT}
┌─────────────────────────────────────────────────────────────────────┐
│                            MAIN MENU                                │
├─────────────────────────────────────────────────────────────────────┤
│  1. {Fore.GREEN}📖 Download Instagram Stories{Fore.YELLOW}                          │
│  2. {Fore.BLUE}🎥 Download Instagram Reel{Fore.YELLOW}                             │
│  3. {Fore.MAGENTA}📊 View Session Statistics{Fore.YELLOW}                           │
│  4. {Fore.CYAN}📋 View Download History{Fore.YELLOW}                               │
│  5. {Fore.WHITE}💾 Save Results to File{Fore.YELLOW}                               │
│  6. {Fore.RED}❌ Exit{Fore.YELLOW}                                                  │
└─────────────────────────────────────────────────────────────────────┘
{Style.RESET_ALL}
        """
        print(menu)

    def get_user_choice(self):
        """Get and validate user menu choice"""
        while True:
            try:
                choice = input(f"{Fore.CYAN}Enter your choice (1-6): {Style.RESET_ALL}").strip()
                if choice in ['1', '2', '3', '4', '5', '6']:
                    return int(choice)
                else:
                    print(f"{Fore.RED}❌ Invalid choice. Please enter 1-6.{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                sys.exit(0)
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {e}. Please try again.{Style.RESET_ALL}")

    def get_username_input(self):
        """Get and validate Instagram username with enhanced validation"""
        while True:
            try:
                print(f"\n{Fore.CYAN}📝 Instagram Username Input{Style.RESET_ALL}")
                print(f"{Fore.WHITE}• Don't include the @ symbol")
                print(f"• Use only letters, numbers, dots, and underscores")
                print(f"• Examples: john_doe, user.name, user123{Style.RESET_ALL}")
                
                username = input(f"\n{Fore.CYAN}Enter Instagram username: {Style.RESET_ALL}").strip()
                
                if username:
                    # Remove @ symbol if user included it
                    username = username.lstrip('@')
                    
                    # Enhanced validation
                    if len(username) < 1:
                        print(f"{Fore.RED}❌ Username too short.{Style.RESET_ALL}")
                        continue
                    elif len(username) > 30:
                        print(f"{Fore.RED}❌ Username too long (max 30 characters).{Style.RESET_ALL}")
                        continue
                    elif not username.replace('.', '').replace('_', '').isalnum():
                        print(f"{Fore.RED}❌ Invalid characters. Use only letters, numbers, dots, and underscores.{Style.RESET_ALL}")
                        continue
                    elif username.startswith('.') or username.endswith('.'):
                        print(f"{Fore.RED}❌ Username cannot start or end with a dot.{Style.RESET_ALL}")
                        continue
                    else:
                        print(f"{Fore.GREEN}✅ Valid username: @{username}{Style.RESET_ALL}")
                        return username
                else:
                    print(f"{Fore.RED}❌ Username cannot be empty.{Style.RESET_ALL}")
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Returning to main menu...{Style.RESET_ALL}")
                return None
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {e}. Please try again.{Style.RESET_ALL}")

    def get_reel_url_input(self):
        """Get and validate Instagram reel URL with enhanced validation"""
        while True:
            try:
                print(f"\n{Fore.CYAN}🔗 Instagram Reel URL Input{Style.RESET_ALL}")
                print(f"{Fore.WHITE}• Paste the complete Instagram URL")
                print(f"• Supported formats:")
                print(f"  - https://www.instagram.com/reel/ABC123/")
                print(f"  - https://www.instagram.com/p/ABC123/")
                print(f"  - https://instagram.com/reel/ABC123/{Style.RESET_ALL}")
                
                url = input(f"\n{Fore.CYAN}Enter Instagram reel URL: {Style.RESET_ALL}").strip()
                
                if url:
                    # Enhanced URL validation
                    try:
                        parsed = urlparse(url)
                        
                        if not parsed.scheme:
                            url = 'https://' + url
                            parsed = urlparse(url)
                        
                        if 'instagram.com' not in parsed.netloc.lower():
                            print(f"{Fore.RED}❌ URL must be from Instagram (instagram.com).{Style.RESET_ALL}")
                            continue
                        
                        if not ('reel' in url.lower() or '/p/' in url):
                            print(f"{Fore.RED}❌ URL must be a reel or post (/reel/ or /p/).{Style.RESET_ALL}")
                            continue
                        
                        print(f"{Fore.GREEN}✅ Valid Instagram URL detected{Style.RESET_ALL}")
                        return url
                        
                    except Exception as e:
                        print(f"{Fore.RED}❌ Invalid URL format: {e}{Style.RESET_ALL}")
                        continue
                else:
                    print(f"{Fore.RED}❌ URL cannot be empty.{Style.RESET_ALL}")
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Returning to main menu...{Style.RESET_ALL}")
                return None
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {e}. Please try again.{Style.RESET_ALL}")

    def setup_visual_driver(self):
        """Setup Chrome WebDriver in visual mode with enhanced options"""
        options = webdriver.ChromeOptions()
        
        # Enhanced Chrome options for better visual experience
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add user agent to appear more like a real browser
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Try different Chrome/Chromium binary locations
        possible_binaries = [
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser',
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',    # Windows
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'  # Windows 32-bit
        ]
        
        for binary in possible_binaries:
            if os.path.exists(binary):
                options.binary_location = binary
                self.logger.info(f"Using Chrome binary: {binary}")
                break
        
        return options

    def create_driver(self):
        """Create WebDriver with multiple fallback strategies"""
        options = self.setup_visual_driver()
        
        # Try multiple strategies to create driver
        strategies = [
            lambda: webdriver.Chrome(service=webdriver.ChromeService(executable_path='/usr/bin/chromedriver'), options=options),
            lambda: webdriver.Chrome(service=webdriver.ChromeService(), options=options),
            lambda: webdriver.Chrome(options=options),
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                driver = strategy()
                self.logger.info(f"WebDriver created successfully using strategy {i+1}")
                return driver
            except Exception as e:
                self.logger.warning(f"Strategy {i+1} failed: {e}")
        
        raise Exception("Failed to create WebDriver with all strategies")

    def handle_page_interactions(self, driver):
        """Handle common page interactions (cookies, ads, etc.)"""
        # Handle cookies consent
        try:
            print(f"{Fore.YELLOW}🍪 Handling cookies consent...{Style.RESET_ALL}")
            cookies_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Consent']"))
            )
            cookies_button.click()
            print(f"{Fore.GREEN}✅ Cookies consent handled{Style.RESET_ALL}")
            time.sleep(1)
        except Exception as e:
            self.logger.info(f"No cookies button found: {e}")
            print(f"{Fore.YELLOW}⚠️ No cookies dialog found{Style.RESET_ALL}")

        # Remove popup ads
        try:
            print(f"{Fore.YELLOW}🚫 Checking for popup ads...{Style.RESET_ALL}")
            popup_element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ads-modal"))
            )
            driver.execute_script("arguments[0].remove();", popup_element)
            print(f"{Fore.GREEN}✅ Popup ad removed{Style.RESET_ALL}")
        except Exception:
            print(f"{Fore.GREEN}✅ No popup ads detected{Style.RESET_ALL}")

    def validate_download_link(self, url, timeout=10):
        """Validate download link with enhanced checking"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
            
            if 200 <= response.status_code < 300:
                # Try to get content info
                content_length = response.headers.get('content-length')
                content_type = response.headers.get('content-type', '')
                
                size_info = ""
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    size_info = f" ({size_mb:.1f} MB)"
                
                return True, f"Valid{size_info} - {content_type}"
            else:
                return False, f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)[:30]}"

    def get_instagram_story_links(self, username):
        """Enhanced story links fetcher with better error handling"""
        print(f"{Fore.GREEN}🔍 Starting to fetch stories for username: @{username}{Style.RESET_ALL}")
        self.logger.info(f"Starting to fetch stories for username: {username}")
        
        driver = None
        download_links = []
        
        try:
            print(f"{Fore.BLUE}🌐 Initializing Chrome WebDriver (Visual Mode)...{Style.RESET_ALL}")
            driver = self.create_driver()
            driver.maximize_window()
            print(f"{Fore.GREEN}✅ Browser opened successfully!{Style.RESET_ALL}")

            print(f"{Fore.BLUE}🌐 Navigating to fastdl.app...{Style.RESET_ALL}")
            driver.get("https://fastdl.app/")
            time.sleep(2)

            self.handle_page_interactions(driver)

            # Username input with enhanced interaction
            print(f"{Fore.BLUE}⌨️ Entering username: @{username}...{Style.RESET_ALL}")
            url_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='search-form-input']"))
            )
            url_input.clear()
            time.sleep(0.5)
            url_input.send_keys(username)
            time.sleep(1)

            # Submit search
            print(f"{Fore.BLUE}🔍 Submitting search...{Style.RESET_ALL}")
            download_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='search-form__button']"))
            )
            download_button.click()
            time.sleep(3)

            # Click Stories tab
            try:
                print(f"{Fore.BLUE}📖 Accessing Stories section...{Style.RESET_ALL}")
                stories_tab = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//li[@class='tabs-component__item']/button[contains(text(), 'stories')]"))
                )
                stories_tab.click()
                time.sleep(2)
                print(f"{Fore.GREEN}✅ Stories tab selected{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ Error accessing Stories section: {e}{Style.RESET_ALL}")
                return []

            # Load all stories with progress tracking
            print(f"{Fore.BLUE}🔄 Loading all available stories...{Style.RESET_ALL}")
            see_more_count = 0
            max_attempts = 10  # Prevent infinite loops
            
            while see_more_count < max_attempts:
                try:
                    see_more_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@class='button button--see-more profile-media-list__button--see-more']"))
                    )
                    see_more_button.click()
                    see_more_count += 1
                    print(f"{Fore.CYAN}📄 Loaded batch {see_more_count}...{Style.RESET_ALL}")
                    time.sleep(2)
                except Exception:
                    break
            
            print(f"{Fore.GREEN}✅ All stories loaded ({see_more_count} batches){Style.RESET_ALL}")

            # Get download buttons
            print(f"{Fore.BLUE}🔍 Collecting download links...{Style.RESET_ALL}")
            download_buttons = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.button--filled"))
            )
            print(f"{Fore.GREEN}✅ Found {len(download_buttons)} stories{Style.RESET_ALL}")

            # Process download links with validation
            for index, download_button in enumerate(download_buttons):
                download_url = download_button.get_attribute("href")
                print(f"{Fore.CYAN}🔄 Validating link {index + 1}/{len(download_buttons)}...{Style.RESET_ALL}")
                
                is_valid, status = self.validate_download_link(download_url)
                if is_valid:
                    download_links.append({
                        'url': download_url,
                        'type': 'story',
                        'username': username,
                        'index': index + 1,
                        'status': status,
                        'timestamp': datetime.now().isoformat()
                    })
                    print(f"{Fore.GREEN}✅ Valid link {index + 1}: {status}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️ Invalid link {index + 1}: {status}{Style.RESET_ALL}")

        except Exception as e:
            self.logger.error(f"Error fetching stories: {e}", exc_info=True)
            print(f"{Fore.RED}❌ Error occurred: {e}{Style.RESET_ALL}")
        
        finally:
            if driver:
                print(f"{Fore.YELLOW}🔄 Keeping browser open for review...{Style.RESET_ALL}")
                time.sleep(5)
                driver.quit()
                print(f"{Fore.GREEN}✅ Browser closed{Style.RESET_ALL}")
        
        # Update session stats
        self.session_stats['stories_downloaded'] += 1
        self.session_stats['total_links'] += len(download_links)
        
        # Add to download history
        self.download_history.append({
            'type': 'stories',
            'target': username,
            'links_found': len(download_links),
            'timestamp': datetime.now().isoformat(),
            'links': download_links
        })
        
        result_msg = f"Found {len(download_links)} valid download links for @{username}"
        self.logger.info(result_msg)
        print(f"{Fore.GREEN + Style.BRIGHT}🎉 {result_msg}{Style.RESET_ALL}")
        return download_links

    def get_instagram_reel_links(self, reel_url):
        """Enhanced reel links fetcher with better error handling"""
        print(f"{Fore.GREEN}🔍 Starting to fetch reel from URL{Style.RESET_ALL}")
        self.logger.info(f"Starting to fetch reel from URL: {reel_url}")
        
        driver = None
        download_links = []
        
        try:
            print(f"{Fore.BLUE}🌐 Initializing Chrome WebDriver (Visual Mode)...{Style.RESET_ALL}")
            driver = self.create_driver()
            driver.maximize_window()
            print(f"{Fore.GREEN}✅ Browser opened successfully!{Style.RESET_ALL}")

            print(f"{Fore.BLUE}🌐 Navigating to fastdl.app...{Style.RESET_ALL}")
            driver.get("https://fastdl.app/")
            time.sleep(2)

            self.handle_page_interactions(driver)

            # URL input
            print(f"{Fore.BLUE}⌨️ Entering reel URL...{Style.RESET_ALL}")
            url_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='search-form-input']"))
            )
            url_input.clear()
            time.sleep(0.5)
            url_input.send_keys(reel_url)
            time.sleep(1)

            # Submit search
            print(f"{Fore.BLUE}🔍 Submitting search...{Style.RESET_ALL}")
            download_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='search-form__button']"))
            )
            download_button.click()
            time.sleep(5)

            # Get download buttons
            print(f"{Fore.BLUE}🔍 Collecting download links...{Style.RESET_ALL}")
            download_buttons = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.button--filled"))
            )
            print(f"{Fore.GREEN}✅ Found {len(download_buttons)} download options{Style.RESET_ALL}")

            # Process download links
            for index, download_button in enumerate(download_buttons):
                download_url = download_button.get_attribute("href")
                print(f"{Fore.CYAN}🔄 Validating link {index + 1}/{len(download_buttons)}...{Style.RESET_ALL}")
                
                is_valid, status = self.validate_download_link(download_url)
                if is_valid:
                    download_links.append({
                        'url': download_url,
                        'type': 'reel',
                        'source_url': reel_url,
                        'index': index + 1,
                        'status': status,
                        'timestamp': datetime.now().isoformat()
                    })
                    print(f"{Fore.GREEN}✅ Valid link {index + 1}: {status}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️ Invalid link {index + 1}: {status}{Style.RESET_ALL}")

        except Exception as e:
            self.logger.error(f"Error fetching reel: {e}", exc_info=True)
            print(f"{Fore.RED}❌ Error occurred: {e}{Style.RESET_ALL}")
        
        finally:
            if driver:
                print(f"{Fore.YELLOW}🔄 Keeping browser open for review...{Style.RESET_ALL}")
                time.sleep(5)
                driver.quit()
                print(f"{Fore.GREEN}✅ Browser closed{Style.RESET_ALL}")
        
        # Update session stats
        self.session_stats['reels_downloaded'] += 1
        self.session_stats['total_links'] += len(download_links)
        
        # Add to download history
        self.download_history.append({
            'type': 'reel',
            'target': reel_url,
            'links_found': len(download_links),
            'timestamp': datetime.now().isoformat(),
            'links': download_links
        })
        
        result_msg = f"Found {len(download_links)} valid download links for reel"
        self.logger.info(result_msg)
        print(f"{Fore.GREEN + Style.BRIGHT}🎉 {result_msg}{Style.RESET_ALL}")
        return download_links

    def display_results(self, links, content_type):
        """Display download links in an enhanced formatted way"""
        if not links:
            print(f"{Fore.RED}❌ No download links found for {content_type}.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.GREEN + Style.BRIGHT}🎉 SUCCESS! Found {len(links)} download link(s) for {content_type}:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
        for i, link_data in enumerate(links, 1):
            if isinstance(link_data, dict):
                url = link_data['url']
                status = link_data.get('status', 'Unknown')
                timestamp = link_data.get('timestamp', 'Unknown')
            else:
                url = link_data
                status = 'Legacy format'
                timestamp = 'Unknown'
            
            print(f"{Fore.YELLOW}📎 Link {i}:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}   URL: {url}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}   Status: {status}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}   Generated: {timestamp[:19] if timestamp != 'Unknown' else timestamp}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'-'*80}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}💡 Copy these links and paste them in your browser to download.{Style.RESET_ALL}")
        print(f"{Fore.BLUE}💾 Use option 5 to save results to a file for later use.{Style.RESET_ALL}")

    def show_session_statistics(self):
        """Display current session statistics"""
        print(f"\n{Fore.BLUE + Style.BRIGHT}📊 SESSION STATISTICS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        duration = datetime.now() - self.session_stats['session_start']
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        stats = [
            ("📖 Stories Downloaded", self.session_stats['stories_downloaded']),
            ("🎥 Reels Downloaded", self.session_stats['reels_downloaded']),
            ("🔗 Total Links Found", self.session_stats['total_links']),
            ("⏰ Session Duration", f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"),
            ("🕐 Session Started", self.session_stats['session_start'].strftime("%Y-%m-%d %H:%M:%S"))
        ]
        
        for label, value in stats:
            print(f"{Fore.WHITE}{label}: {Fore.GREEN}{value}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    def show_download_history(self):
        """Display download history"""
        if not self.download_history:
            print(f"\n{Fore.YELLOW}📋 No download history available yet.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.BLUE + Style.BRIGHT}📋 DOWNLOAD HISTORY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
        for i, entry in enumerate(self.download_history, 1):
            entry_type = entry['type'].upper()
            target = entry['target']
            links_count = entry['links_found']
            timestamp = entry['timestamp'][:19]  # Remove microseconds
            
            icon = "📖" if entry['type'] == 'stories' else "🎥"
            
            print(f"{Fore.YELLOW}{i}. {icon} {entry_type}{Style.RESET_ALL}")
            print(f"   {Fore.WHITE}Target: {target}{Style.RESET_ALL}")
            print(f"   {Fore.GREEN}Links Found: {links_count}{Style.RESET_ALL}")
            print(f"   {Fore.CYAN}Time: {timestamp}{Style.RESET_ALL}")
            
            if entry['links']:
                print(f"   {Fore.MAGENTA}Sample URL: {entry['links'][0]['url'][:60]}...{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}{'-'*80}{Style.RESET_ALL}")

    def save_results_to_file(self):
        """Save download history and links to JSON file"""
        if not self.download_history:
            print(f"\n{Fore.YELLOW}💾 No data to save yet.{Style.RESET_ALL}")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_downloads_{timestamp}.json"
            
            data = {
                'session_stats': self.session_stats,
                'download_history': self.download_history,
                'export_timestamp': datetime.now().isoformat(),
                'total_entries': len(self.download_history)
            }
            
            # Convert datetime objects to strings for JSON serialization
            data['session_stats']['session_start'] = data['session_stats']['session_start'].isoformat()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"\n{Fore.GREEN}✅ Results saved successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📁 File: {filename}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}📊 Entries: {len(self.download_history)}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}🔗 Total Links: {sum(entry['links_found'] for entry in self.download_history)}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error saving file: {e}{Style.RESET_ALL}")
            self.logger.error(f"Error saving results: {e}")

    def run(self):
        """Main application loop with enhanced menu system"""
        self.print_banner()
        
        while True:
            try:
                self.print_menu()
                choice = self.get_user_choice()
                
                if choice == 1:
                    # Download Instagram Stories
                    print(f"\n{Fore.BLUE + Style.BRIGHT}📖 INSTAGRAM STORIES DOWNLOADER{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
                    
                    username = self.get_username_input()
                    if username:
                        print(f"\n{Fore.YELLOW}🚀 Starting download process...{Style.RESET_ALL}")
                        links = self.get_instagram_story_links(username)
                        self.display_results(links, f"stories from @{username}")
                
                elif choice == 2:
                    # Download Instagram Reel
                    print(f"\n{Fore.BLUE + Style.BRIGHT}🎥 INSTAGRAM REEL DOWNLOADER{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
                    
                    reel_url = self.get_reel_url_input()
                    if reel_url:
                        print(f"\n{Fore.YELLOW}🚀 Starting download process...{Style.RESET_ALL}")
                        links = self.get_instagram_reel_links(reel_url)
                        self.display_results(links, "reel")
                
                elif choice == 3:
                    # View Session Statistics
                    self.show_session_statistics()
                
                elif choice == 4:
                    # View Download History
                    self.show_download_history()
                
                elif choice == 5:
                    # Save Results to File
                    self.save_results_to_file()
                
                elif choice == 6:
                    # Exit
                    print(f"\n{Fore.GREEN + Style.BRIGHT}👋 Thank you for using Instagram Downloader Pro!{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}📊 Session Summary:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}   • Stories: {self.session_stats['stories_downloaded']}{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}   • Reels: {self.session_stats['reels_downloaded']}{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}   • Total Links: {self.session_stats['total_links']}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Made with ❤️ for visual Instagram content downloading{Style.RESET_ALL}")
                    break
                
                # Ask if user wants to continue
                print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
                continue_choice = input(f"{Fore.CYAN}Continue with another operation? (Y/n): {Style.RESET_ALL}").strip().lower()
                if continue_choice in ['n', 'no', 'exit', 'quit']:
                    print(f"\n{Fore.GREEN + Style.BRIGHT}👋 Goodbye!{Style.RESET_ALL}")
                    break
                    
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}👋 Application interrupted by user.{Style.RESET_ALL}")
                self.show_session_statistics()
                print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"\n{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
                self.logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                
                continue_choice = input(f"{Fore.CYAN}Would you like to try again? (Y/n): {Style.RESET_ALL}").strip().lower()
                if continue_choice in ['n', 'no']:
                    break


def main():
    """Entry point for the application"""
    try:
        downloader = InstagramDownloader()
        downloader.run()
    except Exception as e:
        print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()