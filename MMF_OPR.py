import time
import json
import sqlite3
import os.path
import logging
import traceback

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import unquote

#global variables
default_dowmnload_path = "<target chrome download files>//" #you should finifh the path with //
myminifactory_urls = []
myminifactory_archives = []
myminifactory_images = []
login = "your login"
pwd = "your password"
sqlite_db_name = "the target path for the sqlite db file"

options = Options()
#options.add_argument("--headless")
#options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-notifications")
options.add_argument('--no-sandbox')
options.add_argument('--verbose')
options.add_experimental_option("prefs", {
        "download.default_directory": "{}".format(default_dowmnload_path),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
})
options.add_argument('--disable-gpu')
options.add_argument('--disable-software-rasterizer')
#Instansiation du driver
driver = webdriver.Chrome(service=Service(), options=options)

logging.basicConfig(level=logging.INFO)

def get_pages(url):
  #open the shared OPR library page
  driver.get('{}'.format(url))
  wait = WebDriverWait(driver, 10)
  element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

  while True:
    #démarer l'analayse de la page courante
    analyse_current_page()
    try:
      # trouver si un element page suivante est present dans la page
      #next = driver.find_element(By.XPATH, "//a[text()='next']")
      next = wait.until(EC.visibility_of_element_located((By.XPATH, "//a[text()='next']")))
      logging.debug(next.get_attribute("outerHTML"))
      link = next.get_attribute("href")
      link = unquote(link)
      if link:
        logging.info("next page: {}".format(link))
        driver.get('{}'.format(link))
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='object-card']/div/a")))
        #element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        #https://www.myminifactory.com/library?v=shared&s=all%2Fonepagerules&page=2
      else:
        logging.error("next page XPATH was not found, I'm not allowed to discover all the pages.")
        break;
    except:
      #traceback.print_exc()
      #last page have no next link, so after the 10 sec the code raise a timeout error, skip it.
      break;

def analyse_current_page():
  #declare the global variable
  global myminifactory_urls
  #logging.info("I will iterate through all the pages and compare the URLs I already have in memory.\nIf necessary, I will add new ones.")
  logging.info("--- open a new page")
  objects = driver.find_elements(By.XPATH, "//div[@class='object-card']/div/a");
  for obj in objects:
    obj_list = {}
    obj_name = obj.get_attribute("title")
    obj_url = obj.get_attribute("href")
    last_dash_index = obj_url.rfind("-")
    url_id = obj_url[last_dash_index + 1:]
    obj_list["name"] = obj_name
    obj_list["url"] = obj_url
    obj_list["url_id"] = url_id
    #append list in myminifactory_object collection list if not already inside
    in_memory = False
    in_memory =  in_myminifactory_objects(obj_url)
    if in_memory:
      logging.info(f"--- Object {obj_list['url_id']} is already in memory, no need to extract details.")
    else:
      myminifactory_urls.append(obj_list)
      logging.info(f"--- A new object {obj_list['url_id']} has been found. Extracting details is necessary.")

    #show the myminifactory objects collection list
    #for col2 in myminifactory_objects:

def in_myminifactory_objects(obj_url):
  #try to find the same obj url in memeory
  found = False
  for my_col in myminifactory_urls:
    my_url = my_col["url"]
    my_obj_url = obj_url
    logging.debug(f"    comparing {my_url} & {my_obj_url}")
    if  my_url == my_obj_url:
      found = True
      break
  return found

def objects_details():
  #for each url in the collection
  i = 0
  for obj_url in myminifactory_urls:
    logging.debug("- in objects_details: myminifactory_urls iteration")
    logging.debug(obj_url)
    #detect if details was already downloaded for this object
    result = False
    if len(myminifactory_archives) > 0:
      for obj_archive in myminifactory_archives:
        logging.debug("- in objects_details: myminifactory_urls iteration")
        logging.debug(obj_archive)
        if obj_archive["url_id"] == obj_url["url_id"]:
          #match: it's mean I already get the details previously
          logging.debug("--- details found")
          result = True
          break

    if result == False:
      get_details(obj_url['url_id'], obj_url["url"])

def get_details(url_id, url):
  #global myminifactory_urls
  global myminifactory_archives
  global myminifactory_images

  #object page openeing and details is now extracted
  driver.get(url)
  wait = WebDriverWait(driver, 10)
  element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
  #lister les images
  objects = driver.find_elements(By.XPATH, "//div[@class='slick-slide']/img");
  for obj in objects:
    my_img_object = {}
    my_img_url = unquote(obj.get_attribute("src"))
    #transform the url to get the 720x720
    my_img_url = my_img_url.replace("70X70", "720X720")
    #append the object in the global images object
    my_img_object["url"] = my_img_url
    my_img_object["url_id"] = url_id
    my_img_object["img_timestamp"] = 0
    myminifactory_images.append(my_img_object)

  try:
    #extract details from script tag
    download = driver.find_element(By.XPATH, "//div[@class='no-padding cont-download']/script")
    soup = BeautifulSoup(download.get_attribute("outerHTML"), 'html.parser')
    tag = soup.find('script')
    json_object = json.loads(tag.get_text())
    my_list = json_object["archives"]
    for item in my_list:
      my_archive_object = {}
      my_archive_object["url_id"] = url_id
      my_archive_object["download_url"] = item['download_url']
      my_archive_object["archive_id"] = item['id']
      my_archive_object["archive_path"] = item['path']
      my_archive_object["archive_size"] = item['size']
      my_archive_object["archive_timestamp"] = 0
      myminifactory_archives.append(my_archive_object)
  except NoSuchElementException:
    # Gestion de l'erreur lorsque l'élément n'est pas trouvé
    logging.error(f"XPATH was not found in {url}, please restart the app")

def download_archives():
  #inititlize global variable
  global myminifactory_archives
  #for each download_url in the collection
  for collection in myminifactory_archives:
    #detect how many urls I need to download
    if int(collection["archive_timestamp"]) == 0:
      #test if the file is in the target directory or not.
      logging.debug(default_dowmnload_path[:-1] + collection["archive_path"])
      if not os.path.exists(default_dowmnload_path[:-1] + collection["archive_path"]):
        logging.info(f"--- download file :{collection['download_url']}")
        #download the file via javascript to avoid ads
        driver.execute_script("window.open(arguments[0], '_blank');", collection["download_url"])
        #attente infinie jusqu'à la fin de l'exécution du script javascript
        while not os.path.exists(default_dowmnload_path + "/" + collection["archive_path"]):
          time.sleep(1)
        logging.info(f"--- The file {collection['archive_path']} was successfully downloaded")
        #record the downloaded_timestamp in the db
        timestamp = int(time.time())
        #update the memory object with the timestamp
        collection["archive_timestamp"] = timestamp
        #update the db object with the time stamp
        logging.debug(f"timestamp was updated in memory and db: {collection['archive_timestamp']} ")
        update_timestamp(collection["download_url"], timestamp)

def update_timestamp(url, timestamp):
  conn = sqlite3.connect(sqlite_db_name)
  cur = conn.cursor()
  # Mise à jour de l'enregistrement avec le nouveau timestamp
  cur.execute(f'UPDATE MMF_archives SET downloaded_timestamp = ? WHERE download_url = ?', (timestamp, url))
  # Validation des modifications
  conn.commit()
  # Fermeture de la connexion
  conn.close()


def login_page(url):
  driver.get('{}'.format(url))
  wait = WebDriverWait(driver, 10)
  element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

  #click on the login button
  login_input = driver.find_element(By.NAME, "_username")
  #send the login name
  login_input.send_keys("{}".format(login))
  #search the password input
  login_input = driver.find_element(By.NAME, "_password")
  #send the password
  login_input.send_keys("{}".format(pwd))
  #click on the login button
  login_input = driver.find_element(By.ID, "_submit").click()
  time.sleep(3)


def record_db():
  # Établir une connexion à la base de données (elle sera créée si elle n'existe pas)
  conn = sqlite3.connect(sqlite_db_name)
  # Créer un curseur pour exécuter des requêtes SQL
  cur = conn.cursor()

  cur.execute(f'''CREATE TABLE IF NOT EXISTS MMF_objects (
                url_id INTEGER,
                name TEXT,
                url TEXT
              )''')

  cur.execute(f'''CREATE TABLE IF NOT EXISTS MMF_images (
                url_id INTEGER,
                img_url TEXT,
                downloaded_timestamp TEXT
              )''')

  cur.execute(f'''CREATE TABLE IF NOT EXISTS MMF_archives (
                url_id INTEGER,
                id INTEGER,
                download_url TEXT,
                file_name TEXT,
                size INTEGER,
                downloaded_timestamp INTEGER
              )''')

# Save the modifications
  conn.commit()

  for objet in myminifactory_urls:
    #test if a record with the same id already exist in the db
    cur.execute(f"SELECT COUNT(*) FROM MMF_objects WHERE url_id = ?", (objet["url_id"],))
    if cur.fetchone()[0] == 0:
      logging.debug("get detail on :{}".format(collection["url"]))
      # Insertion de l'objet dans la table
      cur.execute(f'INSERT INTO MMF_objects VALUES (?, ?, ?)', (
        objet['url_id'],
        objet['name'],
        objet['url'],
      ))

  for objet in myminifactory_images:
    #test if a record with the same id already exist in the db
    cur.execute(f"SELECT COUNT(*) FROM MMF_images WHERE img_url = ?", (objet["url"],))
    if cur.fetchone()[0] == 0:
      logging.debug("get detail on :{}".format(collection["url"]))
      # Insertion de l'objet dans la table
      cur.execute(f'INSERT INTO MMF_images VALUES (?, ?, ?)', (
        objet['url_id'],
        objet['url'],
        objet['img_timestamp'],
      ))

  for objet in myminifactory_archives:
    #test if a record with the same id already exist in the db
    cur.execute(f"SELECT COUNT(*) FROM MMF_archives WHERE download_url = ?", (objet["download_url"],))
    if cur.fetchone()[0] == 0:
      logging.debug("get detail on :{}".format(collection["url"]))
      # Insertion de l'objet dans la table
      cur.execute(f'INSERT INTO MMF_archives VALUES (?, ?, ?, ?, ?, ?)', (
        objet['url_id'],
        objet['archive_id'],
        objet['download_url'],
        objet['archive_path'],
        objet['archive_size'],
        objet['archive_timestamp'],
      ))

  # Save the modifications
  conn.commit()

  # Fermeture de la connexion
  conn.close()

def load_myminifactory_objects():
  #declare the global variable
  global myminifactory_urls
  global myminifactory_images
  global myminifactory_archives

  #if the db file exist
  if os.path.isfile(sqlite_db_name):
    logging.info("--- Load db in memory")
    conn = sqlite3.connect(sqlite_db_name)
    cur = conn.cursor()

    # load all records from the MMF_objects table
    cur.execute(f'SELECT * FROM MMF_objects')
    objects = cur.fetchall()
    record_list = []
    i = 0
    for object in objects:
      record = {
        'url_id': object[0],
        'name': object[1],
        'url': object[2]
      }
      record_list.append(record)
      i += 1
    objet_json = json.dumps(record_list)
    myminifactory_urls = record_list.copy()
    logging.debug(f"------ myminifactory_urls is in memory: {i} records was loaded")

    # load all records from the MMF_images table
    cur.execute(f'SELECT * FROM MMF_images')
    objects = cur.fetchall()
    record_list = []
    i = 0
    for object in objects:
      record = {
        'url_id': object[0],
        'url': object[1],
        'img_timestamp': object[2]
      }
      record_list.append(record)
      i += 1
    objet_json = json.dumps(record_list)
    myminifactory_images = record_list.copy()
    logging.debug(f"------ myminifactory_images is in memory: {i} records was loaded")

    # load all records from the MMF_archives table
    cur.execute(f'SELECT * FROM MMF_archives')
    objects = cur.fetchall()
    record_list = []
    i = 0
    for object in objects:
      record = {
        'url_id': object[0],
        'archive_id': object[1],
        'download_url': object[2],
        'archive_path': object[3],
        'archive_size': object[4],
        'archive_timestamp': object[5]
      }
      record_list.append(record)
      i += 1
    objet_json = json.dumps(record_list)
    myminifactory_archives = record_list.copy()
    logging.debug(f"------ myminifactory_archives is in memory: {i} records was loaded")

    # Fermeture de la connexion
    conn.close()
  else:
    logging.debug("Une nouvelle db va être créée")

def main():
  #inititalize the environement
  load_myminifactory_objects()

  #login on MyMiniFactory web site
  login_page('https://www.myminifactory.com/login')

  #get the pages
  get_pages('https://www.myminifactory.com/library?v=shared&s=all/onepagerules&page=1')
  #get_pages('https://www.myminifactory.com/library?v=shared&s=13203')
  #get_pages('https://www.myminifactory.com/library?v=shared&s=19247')

  #get objects details
  objects_details()

  #record all details in the db
  record_db()

  #download objects
  download_archives()

  #quit
  #time.sleep(60)
  driver.close()

# Appel du point d'entrée principal
if __name__ == "__main__":
    main()
