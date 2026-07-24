# imports
import bs4 # type: ignore
import requests # type: ignore
import os
import shutil
from dotenv import load_dotenv
from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from datetime import datetime

load_dotenv()

# constants
image_page_url = 'https://bingwallpaper.anerg.com'
image_main_page_url = image_page_url + '/gb'
description_page_url = 'https://peapix.com'
description_main_page_url = description_page_url + '/bing/gb'
floorp_directory = 'Floorp/'
file_extension = '.jpg'
root_path = os.getenv('ROOT_PATH')
description_path = root_path + 'html/'

driver_options = webdriver.EdgeOptions()
# driver_options.add_argument('--headless')
driver = webdriver.Edge(options = driver_options)

await_loading = 3
start_html_text = '''
<link rel="stylesheet" href="../css/style.css">
<meta charset="UTF-8">
<div id="content">
'''

# main page
response = requests.get(description_main_page_url)
response.raise_for_status()
soup = bs4.BeautifulSoup(response.text, 'html.parser')
images_links = soup.find_all('a', class_ = 'd-block')
last_image_link = images_links[0].get('href')

# find description
response = driver.get(description_page_url + last_image_link)
soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
charset = soup.find('meta').get('charset')
description = str(soup.find('h3', class_ = 'mb-4 fs-6').parent)

date = soup.find('time').get('datetime')
consent = driver.find_element(By.CLASS_NAME, 'fc-footer-buttons').find_elements(By.TAG_NAME, 'button')[0]
if consent:
   driver.execute_script('arguments[0].click();', consent)
driver.implicitly_wait(await_loading)

# save description
relative_path = description_path + 'today.html'
with open(relative_path, 'w', encoding = charset) as file:
   formatted_date = '<p id="date">(' + datetime.fromisoformat(str(date)).strftime('%d/%m/%Y') + ')</p></div>'
   text = (start_html_text + description + formatted_date)
   file.write(text)
file.close()

# save image
expand = driver.find_element(By.XPATH, '//button[@class="position-absolute z-10 end-0 bottom-0 btn btn-link link-light link-opacity-75 link-opacity-100-hover"]')
if expand:
   driver.execute_script('arguments[0].click();', expand)
driver.implicitly_wait(await_loading)
image_src = driver.find_element(By.TAG_NAME, 'picture').find_element(By.TAG_NAME, 'img').get_attribute('src')
relative_path = floorp_directory + 'today' + file_extension
result = requests.get(image_src, stream=True)
if result.status_code == 200:
   actual_relative_path = os.path.join(os.path.dirname(__file__), relative_path)
   with open(actual_relative_path, 'wb') as file:
      result.raw.decode_content = True
      shutil.copyfileobj(result.raw, file)

# make zip file
try:
   os.chdir(root_path)
   zip_file_name = 'Walltexter.zip'
   delete_zip_command = 'del ' + zip_file_name
   os.system(delete_zip_command)
   create_zip_command = 'tar.exe -a -c -f ' + zip_file_name + ' css html icons manifest.json'
   os.system(create_zip_command)
except:
   pass

driver.close()