import asyncio
import json
import os
from discord.ext import commands
from discord import Embed, SelectOption
import feedparser
import re
from discord.ui import Select, View
from discord import app_commands, Interaction

class UpdateAuto(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.latest_update_title = {}
        self.update_task = bot.loop.create_task(self.check_for_updates())
        self.update_channel_ids = self.load_update_channels()  # 서버별 업데이트 채널 ID 저장

    def load_update_channels(self):
        if not os.path.exists('json/update_channels.json'):
            return {}
        with open('json/update_channels.json', 'r') as f:
            return json.load(f)

    def save_update_channels(self):
        with open('json/update_channels.json', 'w') as f:
            json.dump(self.update_channel_ids, f, indent=4)

    @app_commands.command(name="set_channel_update", description="업데이트를 받을 채널을 설정합니다.")
    async def set_update_channel(self, interaction: Interaction):
        # 서버의 텍스트 채널 리스트를 가져와서 Select 옵션으로 추가
        options = [SelectOption(label=channel.name, value=str(channel.id)) for channel in interaction.guild.text_channels]
        select = Select(placeholder="업데이트를 받을 채널을 선택하세요", options=options)

        async def select_callback(interaction):
            guild_id = str(interaction.guild.id)
            self.update_channel_ids[guild_id] = {
                "server_name": interaction.guild.name,
                "server_id": interaction.guild.id,
                "channel_name": interaction.guild.get_channel(int(select.values[0])).name,
                "channel_id": int(select.values[0])
            }
            self.save_update_channels()
            await interaction.response.send_message(f"업데이트 채널이 설정되었습니다: <#{self.update_channel_ids[guild_id]['channel_id']}>", ephemeral=True)
            
            # 첫 번째 업데이트 내용을 불러와서 전송
            await self.send_initial_update(guild_id)

        select.callback = select_callback
        view = View()
        view.add_item(select)
        await interaction.response.send_message("업데이트를 받을 채널을 선택하세요:", view=view, ephemeral=True)

    async def send_initial_update(self, guild_id):
        try:
            feed_data = feedparser.parse('https://store.steampowered.com/feeds/news/app/2178420/?cc=KR&l=koreana&snr=1_2108_9__2107')
            latest_update_title = feed_data.entries[0].title

            self.latest_update_title[guild_id] = latest_update_title
            content = feed_data.entries[0].description.replace('<br />', '\n').replace('[h5]', '').replace('[/h5]', '')
            cleanr = re.compile('<.*?>')
            update = Embed(title=feed_data.entries[0].title, description=re.sub(cleanr, '', content))
            
            channel_info = self.update_channel_ids[guild_id]
            channel = self.bot.get_channel(channel_info["channel_id"])
            if channel:
                await channel.send(embed=update)
            else:
                print(f"지정된 채널을 찾을 수 없습니다: {channel_info['channel_id']}")
        except Exception as e:
            print(f"초기 업데이트 전송 중 오류 발생: {e}")

    async def check_for_updates(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for guild_id, channel_info in self.update_channel_ids.items():
                try:
                    feed_data = feedparser.parse('https://store.steampowered.com/feeds/news/app/2178420/?cc=KR&l=koreana&snr=1_2108_9__2107')
                    latest_update_title = feed_data.entries[0].title

                    if latest_update_title != self.latest_update_title.get(guild_id):
                        self.latest_update_title[guild_id] = latest_update_title
                        content = feed_data.entries[0].description.replace('<br />', '\n').replace('[h5]', '').replace('[/h5]', '')
                        cleanr = re.compile('<.*?>')
                        update = Embed(title=feed_data.entries[0].title, description=re.sub(cleanr, '', content))
                    
                        channel = self.bot.get_channel(channel_info["channel_id"])
                        if channel:
                            await channel.send(embed=update)
                        else:
                            print(f"지정된 채널을 찾을 수 없습니다: {channel_info['channel_id']}")
                except Exception as e:
                    print(f"업데이트 확인 중 오류 발생: {e}")
                    await asyncio.sleep(60)  # 재시도 전 대기
            await asyncio.sleep(300)  # 정상 작동 시 대기

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UpdateAuto(bot))
    #bot.tree.add_command(AutoUpdate.set_update_channel)