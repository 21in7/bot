from discord import File, Embed, app_commands, Interaction, ButtonStyle
from discord.ext import commands
from discord.ui import Button, View
from Cogs.mod import Today_challenge, Tomorrow_challenge, Today_file, Tomorrow_file
import datetime


class challenge(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="menu", description="Main Menu")
    async def challage(self, interaction: Interaction) -> None:
        d = datetime.datetime.now()
        today_embed = Embed(title="오늘의 챌린지", description=Today_challenge())
        today_file = Today_file()
        today_embed.set_image(url="attachment://image.jpg")
        today_embed.set_footer(text="루틴표 제공 : 한입할게요 \n맵 파일 제공 : 한입할게요 \n봇 문의 : 기현")
        tomorrow_embed = Embed(title="내일의 챌린지", description=Tomorrow_challenge())
        tomorrow_file = Tomorrow_file()
        tomorrow_embed.set_image(url="attachment://image.jpg")
        tomorrow_embed.set_footer(text="루틴표 제공 : 한입할게요 \n맵 파일 제공 : 한입할게요 \n봇 문의 : 기현")

        today = Button(label="오늘의 챌(Today Challenge)", style=ButtonStyle.green, row=1)
        tomorrow = Button(label="내일의 챌(Tomorrow Challenge)", style=ButtonStyle.primary, row=1)
        burning = Button(label="이달의 버닝(Burning of the Month)", style=ButtonStyle.danger, row=2)
        tjdanf = Button(label="면류관(Relics)", style=ButtonStyle.gray, row=2)
        # Season_relic = Button(label="시즌서버 면류관", style=ButtonStyle.blurple)
        tavern = Button(
            label="gihyeonofsoul",
            style=ButtonStyle.link,
            url="https://gihyeonofsoul.com",
            row=3
        )
        contact = Button(label="문의", style=ButtonStyle.blurple, row=5)
        common = Button(
            label="공통 용어(Common ToS Terms)",
            style=ButtonStyle.link,
            url="https://docs.google.com/document/d/1MFxTpvBSPzHhmjhiygjf-Ih-Nm7i99w3RQjxO0_9bns/edit",
            row=4
        )
        skill_common = Button(
            label="스킬 연성표(Enchant Skill Table)", style=ButtonStyle.secondary, row=3
        )

        async def today_callback(interaction: Interaction):
            await interaction.response.send_message(file=today_file, embed=today_embed)

        async def tommorow_callback(interaction: Interaction):
            await interaction.response.send_message(
                file=tomorrow_file, embed=tomorrow_embed
            )

        async def burning_callback(interaction: Interaction):
            await interaction.response.send_message(
                file=File(f"/home/gihyeon/bot/img/{str(d.month)}b.png")
            )

        async def tjdanf_callback(interaction: Interaction):
            await interaction.response.send_message(
                file=File("/home/gihyeon/bot/img/db28631695a79b9e.jpg")
            )

        # async def Season_relic_callback(interaction: Interaction):
        #    await interaction.response.send_message(file=File("./img/season_relic.jpg"))

        async def contact_callback(interaction: Interaction):
            await interaction.response.send_message(
                "email : gihyeon@gihyeon.com\ndiscord : 21in7#0523\n트오세 문의 : cs.tos@imc.co.kr"
            )

        async def skill_common_callback(interaction: Interaction):
            await interaction.response.send_message(
                file=File("/home/gihyeon/bot/img/skill.png")
            )

        today.callback = today_callback
        tomorrow.callback = tommorow_callback
        burning.callback = burning_callback
        tjdanf.callback = tjdanf_callback
        # Season_relic.callback = Season_relic_callback
        contact.callback = contact_callback
        skill_common.callback = skill_common_callback
        view = View(timeout=120.0)
        view.add_item(today)
        view.add_item(tomorrow)
        view.add_item(burning)
        view.add_item(tjdanf)
        view.add_item(tavern)
        # view.add_item(Season_relic)
        view.add_item(contact)
        view.add_item(common)
        view.add_item(skill_common)
        # view.add_item(update)
        await interaction.response.send_message("Select menu", view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(challenge(bot))
