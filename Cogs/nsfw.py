from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import random


class Nsfw(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="nsfw")
    async def randjpg(self, ctx):
        res = requests.get('https://nsfwimg.com/random/')
# print(res.content)
        soup = BeautifulSoup(res.content, 'html.parser')
        img = soup.select(
            'body > div:nth-child(4) > div.content-wrapper > div.page > article > div.single-wrapper > div.single-content > div.single-media')
        for i in img:
            href = i.select_one('img').get('src')
            print(href)
            await ctx.send(href)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        Nsfw(bot)
    )
