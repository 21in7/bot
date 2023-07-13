from discord.ext import commands
from discord import app_commands, Interaction
import requests
from bs4 import BeautifulSoup


class Ingame(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="동접자", description="트오세 동시 접속자 수 확인")
    async def in_game(self, interaction: Interaction):
        urls = 'https://steamcharts.com/app/2178420'
        response = requests.get(url=urls, headers={
                   'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'})

        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html,'html.parser')
            ingame = soup.select_one('#app-heading > div:nth-child(2) > span')
            await interaction.response.send_message('동시 접속자 수는 '+ingame.get_text()+'명 입니다')
        else:
            await interaction.response.send_message(response.status_code)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        Ingame(bot)
    )
