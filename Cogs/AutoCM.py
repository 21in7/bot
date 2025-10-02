import datetime
from Cogs.mod import Today_challenge, Today_file
from discord.ext import commands, tasks
from discord import Embed


class AutoCM(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.check_time.start()

    def cog_unload(self):
        self.check_time.cancel()

    @tasks.loop(minutes=1)
    async def check_time(self):
        # 현재 시간을 가져옵니다.
        now = datetime.datetime.now()
        #print(f"현재 시간: {now.hour}:{now.minute}")  # 디버그 로그 추가

        today_embed = Embed(title="오늘의 챌린지", description=Today_challenge())
        today_file = Today_file()
        today_embed.set_image(url="attachment://image.jpg")
        today_embed.set_footer(text="루틴표 제공 : 한입할게요 \n맵 파일 제공 : 한입할게요 \n봇 문의 : 기현")
        
        # 매일 자정에 메시지를 보냅니다.
        if now.hour == 0 and now.minute == 0:
            print("메시지를 보냅니다.")  # 디버그 로그 추가
            channel = self.bot.get_channel(1095731889546993684)
            await channel.send(file=today_file, embed=today_embed)

    @check_time.before_loop
    async def before_check_time(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(AutoCM(bot))

    