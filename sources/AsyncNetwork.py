from sources.Student import Student
import aiohttp
import asyncio
from typing import List
import time

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

def getOutdatedStudents(students: List[Student], secondsThreshold: int):
    currentTime = time.time()
    print("Time diference", currentTime - students[0].lastUpdated)
    outdatedStudents = filter(lambda a: currentTime - a.lastUpdated >  secondsThreshold, students)
    return outdatedStudents

async def scheduleTask(students: List[Student]):
    while True:
        loginURL = 'https://aeries.smhs.org/Parent/LoginParent.aspx'
        summaryURL = 'https://aeries.smhs.org/Parent/Widgets/ClassSummary/GetClassSummary?IsProfile=True'

        minute = 60 #60 seconds in a minute
        hour = minute * 60 #60 minutes in a hour
        outdatedStudents = getOutdatedStudents(students, secondsThreshold=hour)
        print(f"Outdated students: {outdatedStudents}")
        await asyncio.gather(*[asyncNetworkGet(loginURL,
                                            summaryURL,
                                            email=s.email,
                                            password=s.password) for s in outdatedStudents])
        await asyncio.sleep(1)

async def scheduleAsyncFetch(students: List[Student]):
    asyncio.create_task(scheduleTask(students))
