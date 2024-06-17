from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from PIL import Image
import time
import os
import traceback

max_wait = 10
ignored_exceptions=(NoSuchElementException, StaleElementReferenceException)
known_category_words = ['lion', 'cat', 'tiger', 'panther', 'dog', 'wolf']
url = 'https://nationalzoo.si.edu/animals/list'
chrome_driver_path = './drivers/chrome/chromedriver-win64/chromedriver.exe'
cService = webdriver.ChromeService(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service = cService)

try:
    # Open the animal list website
    driver.get(url)

    # Wait for modal to popup and close it
    modal_close_button = WebDriverWait(driver, max_wait, ignored_exceptions=ignored_exceptions).until(
        EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'modal-close')]"))
    )
    modal_close_button.click()

    # Get the current page number
    current_page = int(WebDriverWait(driver, max_wait, ignored_exceptions=ignored_exceptions).until(
        EC.presence_of_element_located((By.XPATH, "//a[@class='pagination__item' and contains(@title , 'Current page')]"))
    ).text)
    
    animal_index = 0
    should_scrape = True

    while should_scrape:
        # Delay for image list loading
        time.sleep(2)

        image_elements = WebDriverWait(driver, max_wait, ignored_exceptions=ignored_exceptions).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//img[contains(@src, '/sites/default/files/styles/square_large/public/')]"))
        )
        
        if EC.staleness_of(image_elements[len(image_elements)-1]).__call__(False) or EC.staleness_of(image_elements[0]).__call__(False):
            continue

        for index, image_element in enumerate(image_elements):
            # Determine if we should save a screenshot of the element based on the alt text
            alt_text = driver.execute_script('return arguments[0].alt', image_element).lower()
            
            # Ignore "photos coming soon" image
            if not 'photos coming soon' in alt_text:
                directory = ''
                name = ''
                file_name = ''

                # Determine directory and fil name based on if the alt text indicates that this may be a cat or dog
                if any(word in alt_text for word in known_category_words):
                    directory = './UncategorizedImages/'
                    name = str(len(os.listdir(directory))+1)
                else:
                    directory = './PetImages/Other/'
                    name = str(animal_index)
                    animal_index += 1

                # Open image in new tab
                image_url = str(driver.execute_script('return arguments[0].src', image_element))
                driver.execute_script('window.open(arguments[0], "_blank")', image_url)

                # Switch to newly opened tab and screenshot the image element
                driver.switch_to.window(driver.window_handles[-1])
                full_image_element = WebDriverWait(driver, max_wait, ignored_exceptions=ignored_exceptions).until(
                    EC.presence_of_element_located((By.XPATH, "//img[@src='"+image_url+"']"))
                ) 
                file_name = directory+name+'.png'
                full_image_element.screenshot(file_name)

                # Convert the image from a png to a jpg and delete the old image
                image = Image.open(file_name)
                rgb_image = image.convert('RGB')
                rgb_image.save(directory+name+'.jpg')

                if os.path.exists(file_name):
                    os.remove(file_name)

                # Close the new tab and return to the previous one
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            # If this is the last image on this page, go to the next page if there is one
            if index == len(image_elements)-1:
                current_page += 1
                next_page_element = WebDriverWait(driver, max_wait, ignored_exceptions=ignored_exceptions).until(
                    EC.presence_of_element_located((By.XPATH, "//ul[@class='pagination pager__items js-pager__items']//li//a[text()='"+str(current_page)+"']"))
                )
                
                if next_page_element and not EC.staleness_of(next_page_element).__call__(False):
                    next_page_element.click()
                else:
                    driver.quit() 
                    should_scrape = False

except Exception as e:
    print(traceback.format_exc())

finally:
    driver.quit()