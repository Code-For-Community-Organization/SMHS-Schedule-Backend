import json
from typing import Collection, Dict, Optional
import aiohttp
import asyncio
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import os
import collections

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

    def getTagName(self, tag: str) -> str:
        return "{http://www.w3.org/2005/Atom}"+tag

    def saveToDB(self, object: Dict[str, str]):
        with open(self.dbName, "w+") as db:
            json.dump(object, db)

    def fetchFromDB(self, date: str) -> Optional[str]:
        with open(self.dbName, "r+") as db:
            content = json.load(db)
            return content.get(date)

    async def annoucementAsyncFetch(self):
        while True:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.ANNOUCEMENT_URL) as response:
                    #Response code error in networking
                    if not 200 <= response.status <= 300:
                        return
                    
                    html = await response.text()
                    root = ET.fromstring(html)
                    all_annoucements: Dict[str, str] = {}

                    for entry_tag in root.findall(self.getTagName("entry")):
                        date = entry_tag.find(self.getTagName("published")).text

                        index_tag = entry_tag.find(self.getTagName("id")).text
                        annoucement_index = index_tag.split("/", 1)[1]
                        response = requests.get(f"https://www.smhs.org/fs/elements/7031?is_popup=true&post_id={annoucement_index}&show_post=true&is_draft=false")
                        html = response.text
                        soup = BeautifulSoup(html, 'html.parser')
                        annoucement_text = soup.findAll("div", {"class":"fsBody"})[0].text

                        all_annoucements[date] = annoucement_text

            all_annoucements = sorted(all_annoucements.items())
            self.saveToDB(collections.OrderedDict(all_annoucements))
            await asyncio.sleep(60*60*24)

#def stop():
    #task.cancel()
annoucementScraper = AnnoucementScraper()
loop = asyncio.get_event_loop()
#task = loop.create_task(annoucementScraper.annoucementAsyncFetch())
#loop.call_later(10, stop)
# try:
#     loop.run_until_complete(task)
# except asyncio.CancelledError:
#     pass
