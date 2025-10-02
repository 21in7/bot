import datetime
import json
import os
from Cogs.mod import Today_challenge, Today_file
from discord.ext import commands, tasks
from discord import Embed, app_commands, Interaction
from discord.app_commands import checks


class AutoCM(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.config_file = "/home/ubuntu/bot/json/autoCM_channels.json"
        self.channels = self.load_channels()
        self.check_time.start()

    def cog_unload(self):
        self.check_time.cancel()

    def load_channels(self):
        """JSON 파일에서 채널 설정을 불러옵니다."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"채널 설정 로드 실패: {e}")
                return {}
        return {}

    def save_channels(self):
        """채널 설정을 JSON 파일에 저장합니다."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.channels, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"채널 설정 저장 실패: {e}")
            return False

    @app_commands.command(name="setchallenge", description="자동 챌린지맵을 올릴 채널을 설정합니다 (Set auto challenge map channel - KST 00:00 daily)")
    @app_commands.describe(channel="챌린지맵을 자동으로 올릴 채널을 선택하세요 (Select channel for auto challenge map)")
    @checks.has_permissions(administrator=True)
    async def set_challenge_channel(self, interaction: Interaction, channel: str):
        """서버 관리자가 챌린지맵을 자동으로 올릴 채널을 설정합니다."""
        # 채널 멘션에서 채널 ID 추출
        channel_id = None
        if channel.startswith('<#') and channel.endswith('>'):
            channel_id = int(channel[2:-1])
        else:
            try:
                channel_id = int(channel)
            except ValueError:
                await interaction.response.send_message(
                    "❌ 올바른 채널을 입력해주세요. (예: #채널이름 또는 채널ID)\n"
                    "❌ Please enter a valid channel (Example: #channel-name or channel ID)",
                    ephemeral=True
                )
                return

        # 채널이 실제로 존재하는지 확인
        target_channel = self.bot.get_channel(channel_id)
        if target_channel is None:
            await interaction.response.send_message(
                "❌ 해당 채널을 찾을 수 없습니다. 채널이 존재하는지 확인해주세요.\n"
                "❌ Channel not found. Please check if the channel exists.",
                ephemeral=True
            )
            return

        # 서버 ID를 키로 채널 ID 저장
        guild_id = str(interaction.guild_id)
        self.channels[guild_id] = channel_id
        
        if self.save_channels():
            await interaction.response.send_message(
                f"✅ 자동 챌린지맵 채널이 {target_channel.mention}(으)로 설정되었습니다! (매일 한국시간 00:00에 자동 업로드)\n"
                f"✅ Auto challenge map channel has been set to {target_channel.mention}! (Daily upload at 00:00 KST)",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ 채널 설정 저장에 실패했습니다. 봇 관리자에게 문의해주세요.\n"
                "❌ Failed to save channel settings. Please contact bot administrator.",
                ephemeral=True
            )

    @app_commands.command(name="checkchallenge", description="현재 설정된 챌린지맵 채널을 확인합니다 (Check current challenge map channel)")
    async def check_challenge_channel(self, interaction: Interaction):
        """현재 설정된 챌린지맵 채널을 확인합니다."""
        guild_id = str(interaction.guild_id)
        
        if guild_id not in self.channels:
            await interaction.response.send_message(
                "⚠️ 아직 챌린지맵 채널이 설정되지 않았습니다.\n"
                "⚠️ Challenge map channel has not been set yet.\n\n"
                "서버 관리자는 `/setchallenge` 명령어로 채널을 설정할 수 있습니다.\n"
                "Server administrators can set the channel with `/setchallenge` command.",
                ephemeral=True
            )
            return

        channel_id = self.channels[guild_id]
        channel = self.bot.get_channel(channel_id)
        
        if channel:
            await interaction.response.send_message(
                f"📌 현재 설정된 챌린지맵 채널: {channel.mention} (매일 한국시간 00:00 자동 업로드)\n"
                f"📌 Current challenge map channel: {channel.mention} (Daily upload at 00:00 KST)",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "⚠️ 설정된 채널이 존재하지 않습니다. 채널이 삭제되었을 수 있습니다.\n"
                "⚠️ Set channel does not exist. The channel may have been deleted.\n\n"
                "서버 관리자는 `/setchallenge` 명령어로 다시 설정해주세요.\n"
                "Server administrators can reset the channel with `/setchallenge` command.",
                ephemeral=True
            )

    @app_commands.command(name="removechallenge", description="설정된 챌린지맵 채널을 삭제합니다 (Remove challenge map channel setting)")
    @checks.has_permissions(administrator=True)
    async def remove_challenge_channel(self, interaction: Interaction):
        """설정된 챌린지맵 채널을 삭제합니다."""
        guild_id = str(interaction.guild_id)
        
        if guild_id not in self.channels:
            await interaction.response.send_message(
                "⚠️ 설정된 챌린지맵 채널이 없습니다.\n"
                "⚠️ No challenge map channel has been set.",
                ephemeral=True
            )
            return

        del self.channels[guild_id]
        
        if self.save_channels():
            await interaction.response.send_message(
                "✅ 챌린지맵 채널 설정이 삭제되었습니다.\n"
                "✅ Challenge map channel setting has been removed.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ 채널 설정 삭제에 실패했습니다.\n"
                "❌ Failed to remove channel setting.",
                ephemeral=True
            )

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
            
            # 설정된 모든 서버의 채널에 메시지 전송
            for guild_id, channel_id in self.channels.items():
                try:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        # 파일 객체는 한 번만 사용할 수 있으므로 매번 새로 생성
                        file = Today_file()
                        await channel.send(file=file, embed=today_embed)
                        print(f"서버 {guild_id}의 채널 {channel_id}에 메시지 전송 완료")
                    else:
                        print(f"채널 {channel_id}를 찾을 수 없습니다.")
                except Exception as e:
                    print(f"메시지 전송 실패 (서버: {guild_id}, 채널: {channel_id}): {e}")

    @check_time.before_loop
    async def before_check_time(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(AutoCM(bot))

    