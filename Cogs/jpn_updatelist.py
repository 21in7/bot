from discord.ext import commands
from discord import app_commands, Interaction, Embed
import feedparser
import re


class JPNNewupdate(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="jpnupdatelist", description="Update History")
    async def in_game(self, interaction: Interaction):
        feed_data = feedparser.parse(
            "https://store.steampowered.com/feeds/news/app/1175730/?cc=JP&l=koreana&snr=1_2108_9__2107"
        )
        update = Embed(title="更新履歴")
        for i in range(5):
            # content = feed_data.entries[i].description.replace('<br />', '\n').replace('[h5]', '').replace('[/h5]', '')
            # cleanr = re.compile('<.*?>')
            update.add_field(
                name=feed_data.entries[i].title, value=f"{feed_data.entries[i].link}"
            )
        await interaction.response.send_message(embed=update)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(JPNNewupdate(bot))
