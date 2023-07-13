from discord.ext import commands
from discord import app_commands, Interaction, Embed
import feedparser
import re


class Jpn_Update(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="jpnupdate", description="Most recent updates")
    async def in_game(self, interaction: Interaction):
        feed_data = feedparser.parse(
            "https://store.steampowered.com/feeds/news/app/1175730/?cc=JP&l=koreana&snr=1_2108_9__2107"
        )
        content = (
            feed_data.entries[0]
            .description.replace("<br />", "\n")
            .replace("[h5]", "")
            .replace("[/h5]", "")
        )
        cleanr = re.compile("<.*?>")
        update = Embed(
            title=feed_data.entries[0].title, description=re.sub(cleanr, "", content)
        )
        await interaction.response.send_message(embed=update)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Jpn_Update(bot))
