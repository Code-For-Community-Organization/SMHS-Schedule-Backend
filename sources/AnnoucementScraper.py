import json
from typing import Dict, Optional
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import os
import collections
import time
import concurrent.futures

debug = True
if 'ON_HEROKU' in os.environ:
    debug = False

class AnnoucementScraper:
    def __init__(self) -> None:
        if debug:
            self.dbName = "debug-DB_annoucements.json"
        else:
            self.dbName = "DB_annoucements.json"
        self.ANNOUCEMENT_URL = "https://www.smhs.org/fs/post-manager/boards/75/posts/feed"

    def _getTagName(self, tag: str) -> str:
        return "{http://www.w3.org/2005/Atom}"+tag

    def _saveToDB(self, object: Dict[str, str]):
        with open(self.dbName, "w+") as db:
            json.dump(object, db)

    def fetchFromDB(self, date: str) -> Optional[str]:
        with open(self.dbName, "r+") as db:
            content = json.load(db)
            return content.get(date)

    def fetchAnnoucements(self):
        while True:
            session = requests.get(self.ANNOUCEMENT_URL)
            if not 200 <= session.status_code <= 300:
                return

            html = session.text
            root = ET.fromstring(html)
            all_annoucements: Dict[str, str] = {}

            for entry_tag in root.findall(self._getTagName("entry")):
                date = entry_tag.find(self._getTagName("published")).text

                index_tag = entry_tag.find(self._getTagName("id")).text
                annoucement_index = index_tag.split("/", 1)[1]
                response = requests.get(f"https://www.smhs.org/fs/elements/7031?is_popup=true&post_id={annoucement_index}&show_post=true&is_draft=false")
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                annoucement_text = soup.findAll("div", {"class":"fsBody"})[0].text

                all_annoucements[date] = annoucement_text

            all_annoucements = sorted(all_annoucements.items())
            self._saveToDB(collections.OrderedDict(all_annoucements))
            time.sleep(60 * 60 * 24) #Seconds in a day


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor() as executor:
        annoucementScraper = AnnoucementScraper()
        executor.submit(annoucementScraper.fetchAnnoucements)
    
   
