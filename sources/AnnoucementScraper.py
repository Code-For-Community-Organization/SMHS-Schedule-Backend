import aiohttp
import asyncio
import requests
import xml.etree.ElementTree as ET
from dateutil import parser
from bs4 import BeautifulSoup

ANNOUCEMENT_URL = "https://www.smhs.org/fs/post-manager/boards/75/posts/feed"

def getTagName(tag: str) -> str:
  return "{http://www.w3.org/2005/Atom}"+tag

async def annoucementAsyncFetch():
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(ANNOUCEMENT_URL) as response:
                #Response code error in networking
                if not 200 <= response.status <= 300:
                    return
                
                html = await response.text()
                root = ET.fromstring(html)
                for entry_tag in root.findall(getTagName("entry")):
                    date = entry_tag.find(getTagName("published")).text
                    date = parser.parse(date)
                    print(date)
                    index_tag = entry_tag.find(getTagName("id")).text
                    annoucement_index = index_tag.split("/", 1)[1]
                    response = requests.get(f"https://www.smhs.org/fs/elements/7031?is_popup=true&post_id={annoucement_index}&show_post=true&is_draft=false")
                    html = response.text
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    annoucement_text = soup.findAll("div", {"class":"fsBody"})[0].text
                    print(annoucement_text)

        await asyncio.sleep(60*60*24)

def stop():
    task.cancel()

loop = asyncio.get_event_loop()
task = loop.create_task(annoucementAsyncFetch())
loop.call_later(10, stop)
try:
    loop.run_until_complete(task)
except asyncio.CancelledError:
    pass
