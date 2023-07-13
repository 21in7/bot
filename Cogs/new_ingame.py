from discord.ext import commands
from discord import app_commands, Interaction
from config import API_KEY
import requests


class New_Ingame(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="동접자", description="jtos ingame player + ktos ingame player")
    async def in_game(self, interaction: Interaction):

        jpn_urls = f'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key={API_KEY.steam_api}&appid=1175730'
        kor_urls = f'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key={API_KEY.steam_api}&appid=2178420'
        kor_response= requests.get(url=kor_urls).json()
        jpn_response = requests.get(url=jpn_urls).json()
        sum = jpn_response.get('response').get('player_count') + kor_response.get('response').get('player_count')

        await interaction.response.send_message(str(sum)+" In-Game\nktos : "+str(kor_response.get('response').get('player_count'))+"\njtos : "+str(jpn_response.get('response').get('player_count')))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        New_Ingame(bot)
    )
