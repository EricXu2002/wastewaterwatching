from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

# URL of the local map page
map_page_url = 'http://127.0.0.1:5000/map'  # Update with the correct URL to your map page

# Create a new instance of the Chrome driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

driver.get(map_page_url)

try:
    # Wait until the map is loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'map'))
    )
    print("Map loaded successfully.")

finally:
    # Clean up: close the browser window
    driver.quit()