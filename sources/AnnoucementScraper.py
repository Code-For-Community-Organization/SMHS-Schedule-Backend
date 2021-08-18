from datetime import datetime
import json
from typing import Any, Dict, Optional
from bs4.element import Tag
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import os
import collections
import time
import concurrent.futures
from dateutil import parser
import pytz

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

    def _normalizeDate(self, date_raw: str) -> str:
        date: datetime = parser.parse(date_raw)
        if date.tzinfo is None:
            date = pytz.utc.localize(date)
        date = date.replace(hour=0, minute=0, second=0)
        return date.isoformat(timespec="seconds")

    def fetchFromDB(self, date_raw: str) -> Optional[Dict[str, str]]: 
        target_date = self._normalizeDate(date_raw)
        if debug:
            print(date_raw)
            print(target_date)
        with open(self.dbName, "r+") as db:
            #Check if file empty and try fetching annoucements if so
            if os.stat(self.dbName).st_size == 0:
                self.fetchAnnoucements()
            else:
                content = json.load(db)
                return content.get(target_date)
    
    def _getBodyContent(self, soup: BeautifulSoup) -> Optional[Tag]:
       return soup.find("div", {"class":"fsBody"})

    def _getBodyText(self, soup: BeautifulSoup) -> Optional[str]:
        annoucement_text = self._getBodyContent(soup).text
        if annoucement_text is not None:
            annoucement_text_unescape = annoucement_text.replace("\n", "\n")
            return annoucement_text_unescape
        else:
            return None

    def _getSubtitle(self, soup: BeautifulSoup) -> Optional[str]:
        body = self._getBodyContent(soup)
        subtitle = body.find("i")
        if body is not None and subtitle is not None: 
            return subtitle.text
        else:
            return None

    def _getTitle(self, soup: BeautifulSoup) -> Optional[str]:
        body = self._getBodyContent(soup)
        title = body.find("b")

        if body is not None and title is not None:
            return title.text

    def _stripCharacters(self, raw: str, stripping: str = "\\n") -> str:
        return raw.strip(stripping).lstrip().lstrip()

    def fetchAnnoucements(self):
        while True:
            session = requests.get(self.ANNOUCEMENT_URL)
            if not 200 <= session.status_code <= 300:
                return

            html = session.text
            root = ET.fromstring(html)
            
            all_annoucements: Dict[str, Dict[str, str]] = {}
              
            for entry_tag in root.findall(self._getTagName("entry")):
                date_raw = entry_tag.find(self._getTagName("published")).text
                
                index_tag = entry_tag.find(self._getTagName("id")).text
                annoucement_index = index_tag.split("/", 1)[1]
                response = requests.get(f"https://www.smhs.org/fs/elements/7031?is_popup=true&post_id={annoucement_index}&show_post=true&is_draft=false")
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')

                date = self._normalizeDate(date_raw)

                title = self._getTitle(soup)
                subtitle = self._getSubtitle(soup)

                raw_body_text = self._getBodyText(soup)
                if title is not None:
                    raw_body_text = raw_body_text.replace(title, "")
                
                if subtitle is not None:
                    raw_body_text = raw_body_text.replace(subtitle, "")

                annoucement = {"title": title,
                               "subtitle": subtitle,
                               "body": self._stripCharacters(raw_body_text)}

                all_annoucements[date] = annoucement

            all_annoucements = sorted(all_annoucements.items())
            self._saveToDB(collections.OrderedDict(all_annoucements))
            time.sleep(60  * 5) #Seconds in 5 minute
    
if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor() as executor:
        annoucementScraper = AnnoucementScraper()
        annoucementScraper.fetchAnnoucements()

        #result1 = annoucementScraper.fetchFromDB(date_raw="2021-05-13T08:35:05+00:00")
        #print(result1)
    
   
