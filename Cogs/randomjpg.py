from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import random


class Randomjpg(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="랜짤", with_app_command=True, description="랜덤 십덕짤(현재 빗금 명령어 에러 '#랜짤'로 이용바람)")
    async def randjpg(self, ctx):
        res = requests.get('https://gihyeon.com/img')
        soup = BeautifulSoup(res.content, 'html.parser')
        links = soup.find_all('a')
        cell_line = []
        for i in links:
            href = i.attrs['href']
            cell_line.append(href)

        baseurl = 'https://gihyeon.com/img/'
        sumurl = baseurl + random.choice(cell_line)
        await ctx.send(sumurl)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        Randomjpg(bot)
    )
