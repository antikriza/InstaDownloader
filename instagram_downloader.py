import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_instagram_story_links(username):
    """
    Get Instagram story links for a given username.
    
    Args:
        username (str): Instagram username
    
    Returns:
        list: List of direct download URLs for stories
    """
    logger.info(f"Starting to fetch stories for username: {username}")
    
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    driver = None
    download_links = []
    
    try:
        logger.info("Initializing Chrome WebDriver")
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()

        logger.info("Navigating to fastdl.app")
        driver.get("https://fastdl.app/")

        # Cookies consent
        logger.info("Waiting for cookies button")
        try:
            cookies_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Consent']"))
            )
            cookies_button.click()
            logger.info("Cookies button clicked")
        except Exception as e:
            logger.warning(f"No cookies button found or could not click it: {e}")

        # Username input
        logger.info(f"Entering username: {username}")
        url_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='search-form-input']"))
        )
        url_input.send_keys(f"{username}")

        # Download button
        logger.info("Clicking download button")
        download_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//button[@class='search-form__button']"))
        )
        download_button.click()

        # Remove popup ad if it appears
        try:
            logger.info("Checking for popup ads")
            popup_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ads-modal"))
            )
            driver.execute_script("""
                var element = arguments[0];
                element.parentNode.removeChild(element);
                """, popup_element)
            logger.info("Popup ad removed")
        except Exception as e:
            logger.info(f"No popup ad detected or error removing it: {e}")

        time.sleep(6)

        # Click the "Stories" tab
        try:
            logger.info("Clicking Stories tab")
            stories_tab = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//li[@class='tabs-component__item']/button[contains(text(), 'stories')]"))
            )
            stories_tab.click()
            logger.info("Stories tab clicked")
        except Exception as e:
            logger.error(f"Error clicking Stories tab: {e}")
            return []

        # Click "See more" buttons until they no longer appear
        see_more_count = 0
        while True:
            try:
                see_more_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//button[@class='button button--see-more profile-media-list__button--see-more']"))
                )
                see_more_button.click()
                see_more_count += 1
                logger.info(f"See more button clicked ({see_more_count})")
                time.sleep(2)  # Wait for new content to load
            except Exception:
                logger.info("No more See more buttons found")
                break

        # Wait for download buttons to become clickable
        logger.info("Looking for download buttons")
        download_buttons = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.button--filled"))
        )
        logger.info(f"Found {len(download_buttons)} download buttons")

        # Get URLs without downloading
        for index, download_button in enumerate(download_buttons):
            download_url = download_button.get_attribute("href")
            
            # Check if URL is valid
            try:
                response = requests.head(download_url, timeout=10)
                if 200 <= response.status_code < 300:
                    download_links.append(download_url)
                    logger.info(f"Valid download URL found: {download_url}")
                else:
                    logger.warning(f"URL returned non-success status code {response.status_code}: {download_url}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error checking URL {download_url}: {e}")

    except Exception as e:
        logger.error(f"Error fetching stories: {e}", exc_info=True)
    
    finally:
        if driver:
            driver.quit()
            logger.info("WebDriver closed")
    
    logger.info(f"Found {len(download_links)} valid download links for {username}")
    return download_links