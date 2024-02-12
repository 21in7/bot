import asyncio
from discord.ext import commands
from discord import Interaction
from discord import Embed
import feedparser
import re

class Update(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.update_task = bot.loop.create_task(self.check_for_updates())

    async def check_for_updates(self):
        await self.bot.wait_until_ready()  # 봇이 준비될 때까지 대기
        while not self.bot.is_closed():
            feed_data = feedparser.parse(
                'https://store.steampowered.com/feeds/news/app/2178420/?cc=KR&l=koreana&snr=1_2108_9__2107')

            latest_update_title = feed_data.entries[0].title

            if latest_update_title != getattr(self, 'latest_update_title', None):
                self.latest_update_title = latest_update_title
                content = feed_data.entries[0].description.replace('<br />', '\n').replace('[h5]', '').replace('[/h5]', '')
                cleanr = re.compile('<.*?>')
                update = Embed(title=feed_data.entries[0].title, description=re.sub(cleanr, '', content))
                
                # 여기에 실제로 메시지를 보낼 채널의 ID를 사용하세요
                channel = self.bot.get_channel(1095731889546993684)
                await channel.send(embed=update)

            # 30분마다 다시 확인하기 전에 대기
            await asyncio.sleep(300)  # 1800 초 = 30 분

    @commands.command(name="업데이트", description="Most recent updates")
    async def in_game(self, interaction: Interaction):
        feed_data = feedparser.parse(
            'https://store.steampowered.com/feeds/news/app/2178420/?cc=KR&l=koreana&snr=1_2108_9__2107')
        content = feed_data.entries[0].description.replace('<br />', '\n').replace('[h5]', '').replace('[/h5]', '')
        cleanr = re.compile('<.*?>')
        update = Embed(title=feed_data.entries[0].title, description=re.sub(cleanr, '', content))
        await interaction.response.send_message(embed=update)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        Update(bot)
    )