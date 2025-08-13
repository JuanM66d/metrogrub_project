import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service # <-- NEW: Import the Service class
from selenium.webdriver.chrome.options import Options

INPUT_XPATH = '/html/body/div/div[1]/div[1]/div/div/section/div[1]/div[2]/div/div/div/div/div[4]/div/div/div[1]/div/textarea'
SEND_BUTTON_XPATH = '/html/body/div/div[1]/div[1]/div/div/section/div[1]/div[2]/div/div/div/div/div[4]/div/div/div[3]/button'
BOT_RESPONSE_XPATH = "/html/body/div/div[1]/div[1]/div/div/section/div[1]/div[2]/div/div/div/div/div[2]/div/div[3]/div/div[2]/div/div/div/div/p"

CHROME_DRIVER_PATH = "../chrome_test.app/Contents/MacOS/Google Chrome for Testing" # <-- CHANGED: Example for macOS .app bundle
STREAMLIT_APP_URL = "http://localhost:8501"

@pytest.fixture(scope="session")
def driver():
    """A pytest fixture to set up and tear down the browser for each test."""
    # Setup

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    browser_driver = webdriver.Chrome(options=chrome_options)
    browser_driver.get(STREAMLIT_APP_URL)
    # Yield the driver to the test
    yield browser_driver
    # Teardown
    # browser_driver.quit()

@pytest.mark.parametrize("user_message, key_words", [
    ("Hello", ["location scoring", "dashboard"]),
    ("Break down location scoring for me", ["Demand Potential", "Accessibility", "Complementary Businesses", "Competition"]),

])

def test_chatbot(driver, user_message, key_words):
    """
    Tests the chatbot's response to various user messages.
    """
    wait = WebDriverWait(driver, 15)

    # Find the chat input box and type the user message from the parameters
    chat_input = wait.until(EC.element_to_be_clickable((By.XPATH, INPUT_XPATH)))
    chat_input.send_keys(user_message)

    # Find and click the send button
    send_button = wait.until(EC.element_to_be_clickable((By.XPATH, SEND_BUTTON_XPATH)))
    send_button.click()

    # Explicitly wait for the bot's response element to appear
    bot_response_element = wait.until(
        EC.presence_of_element_located((By.XPATH, BOT_RESPONSE_XPATH))
    )

    actual_response = bot_response_element.text
    print(actual_response)
    
    for word in key_words:
        assert word in actual_response, f"Missing keyword in response: ${word}'"
    
