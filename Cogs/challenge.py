from discord import File, Embed, app_commands, Interaction, ButtonStyle, SelectOption
from discord.ext import commands
from discord.ui import Button, View, Select
from Cogs.mod import Today_challenge, Tomorrow_challenge, Today_file, Tomorrow_file, Weekend_challenge, Weekend_file, Weekend_day_challenge
import datetime


class challenge(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name='shutdown', description='Shutdown Bot')
    async def shutdown(self, interaction: Interaction):
        if interaction.user.id != 247253360930062336:
            await interaction.response.send_message("이 명령어는 봇 주인만 사용할 수 있습니다.", ephemeral=True)
            return
        
        await interaction.response.send_message("봇을 종료합니다.", ephemeral=True)
        await self.bot.close()

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
        weekend_embed = Embed(title="주간 챌린지", description=Weekend_challenge())
        weekend_embed.set_footer(text="루틴표 제공 : 한입할게요 \n맵 파일 제공 : 한입할게요 \n봇 문의 : 기현")

        today = Button(label="오늘의 챌(Today Challenge)", style=ButtonStyle.green, row=1)
        tomorrow = Button(label="내일의 챌(Tomorrow Challenge)", style=ButtonStyle.primary, row=1)
        weekend = Button(label="주간 챌(Weekend Challenge)", style=ButtonStyle.primary, row=1)
        burning = Button(label="이달의 버닝(Burning of the Month)", style=ButtonStyle.danger, row=2)
        tjdanf = Button(label="면류관(Relics)", style=ButtonStyle.gray, row=2)
        # Season_relic = Button(label="시즌서버 면류관", style=ButtonStyle.blurple)
        tavern = Button(
            label="gihyeonofsoul",
            style=ButtonStyle.link,
            url="https://gihyeonofsoul.com",
            row=3
        )
        contact = Button(label="문의", style=ButtonStyle.blurple, row=4)
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
            await interaction.response.send_message(file=today_file, embed=today_embed, ephemeral=True)

        async def tommorow_callback(interaction: Interaction):
            await interaction.response.send_message(
                file=tomorrow_file, embed=tomorrow_embed, ephemeral=True
            )

        async def weekend_callback(interaction: Interaction):
            # SelectMenu 생성
            select = Select(
                placeholder="요일을 선택하세요",
                options=[
                    SelectOption(label="월요일(Monday)", value="0", emoji="📅"),
                    SelectOption(label="화요일(Tuesday)", value="1", emoji="📅"),
                    SelectOption(label="수요일(Wednesday)", value="2", emoji="📅"),
                    SelectOption(label="목요일(Thursday)", value="3", emoji="📅"),
                    SelectOption(label="금요일(Friday)", value="4", emoji="📅"),
                    SelectOption(label="토요일(Saturday)", value="5", emoji="📅"),
                    SelectOption(label="일요일(Sunday)", value="6", emoji="📅")
                ]
            )
            
            async def select_callback(select_interaction: Interaction):
                day_offset = int(select.values[0])
                day_names = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
                selected_file = Weekend_file(day_offset)
                challenge_info = Weekend_day_challenge(day_offset)
                
                select_embed = Embed(title=f"{day_names[day_offset]} 챌린지", description=challenge_info)
                select_embed.set_image(url="attachment://image.jpg")
                select_embed.set_footer(text="루틴표 제공 : 한입할게요 \n맵 파일 제공 : 한입할게요 \n봇 문의 : 기현")
                
                await select_interaction.response.send_message(
                    file=selected_file, embed=select_embed, ephemeral=True
                )
            
            select.callback = select_callback
            select_view = View(timeout=30.0)
            select_view.add_item(select)
            
            await interaction.response.send_message(
                embed=weekend_embed, view=select_view, ephemeral=True
            )


        async def tjdanf_callback(interaction: Interaction):
            await interaction.response.send_message(
                file=File("/home/ubuntu/bot/img/db28631695a79b9e.jpg"), ephemeral=True
            )

        # async def Season_relic_callback(interaction: Interaction):
        #    await interaction.response.send_message(file=File("./img/season_relic.jpg"))

        async def contact_callback(interaction: Interaction):
            await interaction.response.send_message(
                "email : gihyeon@gihyeon.com\ndiscord : 21in7#0523\n트오세 문의 : cs.tos@imc.co.kr", ephemeral=True
            )

        async def skill_common_callback(interaction: Interaction):
            await interaction.response.send_message(
                file=File("/home/ubuntu/bot/img/skill.png"), ephemeral=True
            )

        today.callback = today_callback
        tomorrow.callback = tommorow_callback
        weekend.callback = weekend_callback
        tjdanf.callback = tjdanf_callback
        # Season_relic.callback = Season_relic_callback
        contact.callback = contact_callback
        skill_common.callback = skill_common_callback
        view = View(timeout=120.0)
        view.add_item(today)
        view.add_item(tomorrow)
        view.add_item(tjdanf)
        view.add_item(tavern)
        # view.add_item(Season_relic)
        view.add_item(contact)
        view.add_item(common)
        view.add_item(skill_common)
        view.add_item(weekend)
        # view.add_item(update)
        await interaction.response.send_message("Select menu", view=view, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(challenge(bot))
