# 영 -> 한 번역
from discord.ext import commands
from discord import app_commands, Interaction
from config import API_KEY
import requests


class Translate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="translate", description="Translate en -> kr")
    async def translate(self, interaction: Interaction, text: str):
        data = {"text": text, "source": "en", "target": "ko"}
        url = "https://openapi.naver.com/v1/papago/n2mt"

        header = {
            "X-Naver-Client-Id": API_KEY.PAPAGO_ID,
            "X-Naver-Client-Secret": API_KEY.PAPAGO_SECRET,
        }

        response = requests.post(url, headers=header, data=data)
        rescode = response.status_code

        if rescode == 200:
            t_data = response.json()
            # print(t_data["message"]["result"]["translatedText"])
            await interaction.response.send_message(
                t_data["message"]["result"]["translatedText"]
            )
        else:
            print("Error Code:", rescode)


async def setup(bot: commands.Bot):
    await bot.add_cog(Translate(bot))
