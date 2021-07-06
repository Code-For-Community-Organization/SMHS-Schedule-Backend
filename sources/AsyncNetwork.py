import aiohttp
import asyncio

async def asyncNetworkGet(loginURL: str,
                          summaryURL: str,
                          username: str,
                          password: str):
    
    async with aiohttp.ClientSession() as session:
        payload: dict[str, str] = {
        'portalAccountUsername': username,
        'portalAccountPassword': password}
        async with session.post(loginURL, data=payload) as response:
            async with session.get(summaryURL) as response:
                print(f"Now fetching {username}. Status:", response.status)
                html = await response.text()
                print(f"{html[:10]}...")

async def main():
    await asyncio.gather(*[asyncNetworkGet(loginURL='https://aeries.smhs.org/Parent/LoginParent.aspx',
                    summaryURL='https://aeries.smhs.org/Parent/Widgets/ClassSummary/GetClassSummary?IsProfile=True',
                    username='jingwen.mao@smhsstudents.org',
                    password='Mao511969') for i in range(1)])
asyncio.run(main())
