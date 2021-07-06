from sources.User import Student
import aiohttp
import asyncio
from typing import List


async def asyncNetworkGet(loginURL: str,
                          summaryURL: str,
                          email: str,
                          password: str):

    async with aiohttp.ClientSession() as session:
        payload: dict[str, str] = {
            'portalAccountUsername': email,
            'portalAccountPassword': password}
        async with session.post(loginURL, data=payload) as response:
            async with session.get(summaryURL) as response:
                print(f"Now fetching {email}. Status:", response.status)
                html = await response.text()
                print(f"{html[:10]}...")


async def scheduleAsyncFetch(students: List[Student]):
    loginURL = 'https://aeries.smhs.org/Parent/LoginParent.aspx'
    summaryURL = 'https://aeries.smhs.org/Parent/Widgets/ClassSummary/GetClassSummary?IsProfile=True'

    await asyncio.gather(*[asyncNetworkGet(loginURL,
                                           summaryURL,
                                           email=s.email,
                                           password=s.password) for s in students])
    await asyncio.sleep(5)

