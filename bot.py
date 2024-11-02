# 모듈 불러오기
import discord
from discord.ext import commands
import bot_token
import logging
import logging.handlers

# 로그 파일 갯수랑 용량 지정
LOG_MAX_SIZE = 1024 * 1024 * 10
LOG_FILE_CNT = 100

# 로그 저장
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
    filename="/home/ubuntu/bot/logs/bot.log",
    encoding="utf-8",
    mode="w",
    maxBytes=LOG_MAX_SIZE,
    backupCount=LOG_FILE_CNT,
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="#",
            intents=discord.Intents.all(),
            sync_commands=True,
            application_id=1069616255880925204,
        )
        self.initial_extension = [
            "Cogs.challenge",
            "Cogs.sheet",
            "Cogs.autoupdate",
            "Cogs.new_ingame",
            "Cogs.AutoCM",
        ]

    async def setup_hook(self):
        # add reload, load command
        @self.tree.command(name="reload", description="Reload a cog")
        async def reload(interaction: discord.Interaction, cog: str):
            if not await self.is_owner(interaction.user):
                await interaction.response.send_message("이 명령어는 봇 소유자만 사용할 수 있습니다.", ephemeral=True)
                return
            try:
                await interaction.response.defer(ephemeral=True)
                await self.reload_extension(f"Cogs.{cog}")
                await interaction.followup.send(f"Cog {cog} reloaded successfully!", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"Error reloading cog {cog}: {str(e)}", ephemeral=True)

        @self.tree.command(name="load", description="Load a new cog")
        async def load(interaction: discord.Interaction, cogs: str):
            if not self.is_owner(interaction.user):
                await interaction.response.send_message("이 명령어는 봇 소유자만 사용할 수 있습니다.", ephemeral=True)
                return
            try:
                await interaction.response.defer(ephemeral=True)
                await self.load_extension(f"Cogs.{cogs}")
                await self.tree.sync()
                await interaction.followup.send(f"Cog {cogs} loaded successfully!", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"Error loading cog {cogs}: {str(e)}", ephemeral=True)

        for ext in self.initial_extension:
            await self.load_extension(ext)
        await self.tree.sync(guild=discord.Object(id=769953233070194698))
        await self.tree.sync()

    async def on_ready(self):
        print("다음으로 로그인 합니다 : ")
        print(self.user.name)
        print(self.user.id)
        print("=============")
        game = discord.Game("Tree Of Savior 🌳")
        await self.change_presence(status=discord.Status.online, activity=game)


bot = MyBot()
bot.remove_command("help")
bot.run(bot_token.main_token)
