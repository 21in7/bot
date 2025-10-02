import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
import requests
import urllib.parse
import json

class BuffSelectView(View):
    def __init__(self, buffs_data, api_url, headers):
        super().__init__(timeout=60)
        self.buffs_data = buffs_data
        self.API_URL = api_url
        self.headers = headers
        
        # Select Menu 생성
        select = Select(
            placeholder="상세 정보를 보고 싶은 버프를 선택하세요",
            options=[
                discord.SelectOption(
                    label=buff.get('name', 'N/A')[:100],  # Discord 제한으로 100자로 제한
                    description=buff.get('descriptions', 'N/A')[:100] if buff.get('descriptions') else '설명 없음',
                    value=str(i),
                    emoji="🔮"
                )
                for i, buff in enumerate(buffs_data[:25])  # Discord는 최대 25개 옵션만 지원
            ]
        )
        select.callback = self.on_select
        self.add_item(select)
    
    async def on_select(self, interaction: discord.Interaction):
        selected_index = int(interaction.data['values'][0])
        selected_buff = self.buffs_data[selected_index]
        
        # 선택된 버프의 상세 정보를 가져와서 표시
        await self.show_buff_details(interaction, selected_buff)
    
    async def show_buff_details(self, interaction: discord.Interaction, buff_data):
        """선택된 버프의 상세 정보를 표시합니다."""
        try:
            # 임베드 생성
            embed = discord.Embed(
                title=f"🔮 {buff_data.get('name', 'N/A')}",
                description=buff_data.get('descriptions', 'N/A'),
                color=0x00ff00
            )
            
            # 기본 정보 추가
            embed.add_field(
                name="🆔 버프 ID", 
                value=buff_data.get('ids', 'N/A'), 
                inline=True
            )
            
            # 지속 시간을 초 단위로 변환
            applytime = buff_data.get('applytime', 0)
            if applytime and applytime > 0:
                duration_seconds = applytime / 1000
                if duration_seconds >= 60:
                    duration_text = f"{duration_seconds/60:.1f}분"
                else:
                    duration_text = f"{duration_seconds:.1f}초"
            else:
                duration_text = "영구"
            
            embed.add_field(
                name="⏱️ 지속 시간", 
                value=duration_text, 
                inline=True
            )
            
            # 아이콘 URL이 있으면 썸네일로 설정
            icon_url = buff_data.get('icon_url')
            if icon_url:
                embed.set_thumbnail(url=icon_url)
            
            # 그룹 정보
            group1 = buff_data.get('group1', '')
            group2 = buff_data.get('group2', '')
            if group1 or group2:
                group_text = f"{group1}" + (f" > {group2}" if group2 else "")
                embed.add_field(
                    name="📂 분류", 
                    value=group_text, 
                    inline=False
                )
            
            # 추가 정보
            if buff_data.get('overbuff'):
                embed.add_field(
                    name="🔄 중복 가능", 
                    value="✅ 중복 적용 가능", 
                    inline=True
                )
            
            if buff_data.get('userremove'):
                embed.add_field(
                    name="❌ 제거 가능", 
                    value="✅ 사용자가 제거 가능", 
                    inline=True
                )
            
            # 푸터에 타임스탬프
            embed.set_footer(text=f"요청자: {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ **오류**: {str(e)}", ephemeral=True)

class BuffCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.API_URL = "https://api.gihyeonofsoul.com/api/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    @commands.command(name='버프', aliases=['buff'])
    async def buff_info(self, ctx, *, buff_name: str):
        """버프 정보를 조회합니다."""
        try:
            # URL 인코딩
            encoded_name = urllib.parse.quote(buff_name)
            url = f"{self.API_URL}buffs/name/{encoded_name}"
            
            # API 요청
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    buff_data = data.get('data', {})
                    
                    # 임베드 생성
                    embed = discord.Embed(
                        title=f"🔮 {buff_data.get('name', 'N/A')}",
                        description=buff_data.get('descriptions', 'N/A'),
                        color=0x00ff00
                    )
                    
                    # 기본 정보 추가
                    embed.add_field(
                        name="🆔 버프 ID", 
                        value=buff_data.get('ids', 'N/A'), 
                        inline=True
                    )
                    
                    # 지속 시간을 초 단위로 변환
                    applytime = buff_data.get('applytime', 0)
                    if applytime and applytime > 0:
                        duration_seconds = applytime / 1000
                        if duration_seconds >= 60:
                            duration_text = f"{duration_seconds/60:.1f}분"
                        else:
                            duration_text = f"{duration_seconds:.1f}초"
                    else:
                        duration_text = "영구"
                    
                    embed.add_field(
                        name="⏱️ 지속 시간", 
                        value=duration_text, 
                        inline=True
                    )
                    
                    # 아이콘 URL이 있으면 썸네일로 설정
                    icon_url = buff_data.get('icon_url')
                    if icon_url:
                        embed.set_thumbnail(url=icon_url)
                    
                    # 그룹 정보
                    group1 = buff_data.get('group1', '')
                    group2 = buff_data.get('group2', '')
                    if group1 or group2:
                        group_text = f"{group1}" + (f" > {group2}" if group2 else "")
                        embed.add_field(
                            name="📂 분류", 
                            value=group_text, 
                            inline=False
                        )
                    
                    # 추가 정보
                    if buff_data.get('overbuff'):
                        embed.add_field(
                            name="🔄 중복 가능", 
                            value="✅ 중복 적용 가능", 
                            inline=True
                        )
                    
                    if buff_data.get('userremove'):
                        embed.add_field(
                            name="❌ 제거 가능", 
                            value="✅ 사용자가 제거 가능", 
                            inline=True
                        )
                    
                    # 푸터에 타임스탬프
                    embed.set_footer(text=f"요청자: {ctx.author.display_name}")
                    
                    await ctx.send(embed=embed)
                    
                else:
                    error_msg = data.get('message', '알 수 없는 오류가 발생했습니다.')
                    await ctx.send(f"❌ **오류**: {error_msg}")
                    
            else:
                await ctx.send(f"❌ **HTTP 오류**: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            await ctx.send("❌ **연결 오류**: API 서버에 연결할 수 없습니다.")
        except requests.exceptions.Timeout:
            await ctx.send("❌ **타임아웃**: 요청 시간이 초과되었습니다.")
        except Exception as e:
            await ctx.send(f"❌ **오류**: {str(e)}")

    @app_commands.command(name="버프", description="버프 정보를 조회합니다")
    @app_commands.describe(buff_name="조회할 버프 이름")
    async def buff_info_slash(self, interaction: discord.Interaction, buff_name: str):
        """버프 정보를 조회합니다."""
        try:
            # URL 인코딩
            encoded_name = urllib.parse.quote(buff_name)
            url = f"{self.API_URL}buffs/name/{encoded_name}"
            
            # API 요청
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    buff_data = data.get('data', {})
                    
                    # 임베드 생성
                    embed = discord.Embed(
                        title=f"🔮 {buff_data.get('name', 'N/A')}",
                        description=buff_data.get('descriptions', 'N/A'),
                        color=0x00ff00
                    )
                    
                    # 기본 정보 추가
                    embed.add_field(
                        name="🆔 버프 ID", 
                        value=buff_data.get('ids', 'N/A'), 
                        inline=True
                    )
                    
                    # 지속 시간을 초 단위로 변환
                    applytime = buff_data.get('applytime', 0)
                    if applytime and applytime > 0:
                        duration_seconds = applytime / 1000
                        if duration_seconds >= 60:
                            duration_text = f"{duration_seconds/60:.1f}분"
                        else:
                            duration_text = f"{duration_seconds:.1f}초"
                    else:
                        duration_text = "영구"
                    
                    embed.add_field(
                        name="⏱️ 지속 시간", 
                        value=duration_text, 
                        inline=True
                    )
                    
                    # 아이콘 URL이 있으면 썸네일로 설정
                    icon_url = buff_data.get('icon_url')
                    if icon_url:
                        embed.set_thumbnail(url=icon_url)
                    
                    # 그룹 정보
                    group1 = buff_data.get('group1', '')
                    group2 = buff_data.get('group2', '')
                    if group1 or group2:
                        group_text = f"{group1}" + (f" > {group2}" if group2 else "")
                        embed.add_field(
                            name="📂 분류", 
                            value=group_text, 
                            inline=False
                        )
                    
                    # 추가 정보
                    if buff_data.get('overbuff'):
                        embed.add_field(
                            name="🔄 중복 가능", 
                            value="✅ 중복 적용 가능", 
                            inline=True
                        )
                    
                    if buff_data.get('userremove'):
                        embed.add_field(
                            name="❌ 제거 가능", 
                            value="✅ 사용자가 제거 가능", 
                            inline=True
                        )
                    
                    # 푸터에 타임스탬프
                    embed.set_footer(text=f"요청자: {interaction.user.display_name}")
                    
                    await interaction.response.send_message(embed=embed)
                    
                else:
                    error_msg = data.get('message', '알 수 없는 오류가 발생했습니다.')
                    await interaction.response.send_message(f"❌ **오류**: {error_msg}")
                    
            else:
                await interaction.response.send_message(f"❌ **HTTP 오류**: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            await interaction.response.send_message("❌ **연결 오류**: API 서버에 연결할 수 없습니다.")
        except requests.exceptions.Timeout:
            await interaction.response.send_message("❌ **타임아웃**: 요청 시간이 초과되었습니다.")
        except Exception as e:
            await interaction.response.send_message(f"❌ **오류**: {str(e)}")

    @commands.command(name='버프검색', aliases=['buffsearch'])
    async def buff_search(self, ctx, *, search_term: str):
        """버프를 검색합니다. (부분 일치)"""
        try:
            # 검색 API 엔드포인트 (실제 API에 맞게 수정 필요)
            search_url = f"{self.API_URL}buffs"
            params = {'search': search_term}
            
            response = requests.get(search_url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('data'):
                    buffs = data.get('data', [])
                    
                    if len(buffs) > 0:
                        embed = discord.Embed(
                            title=f"🔍 '{search_term}' 검색 결과",
                            description="아래 드롭다운에서 상세 정보를 보고 싶은 버프를 선택하세요!",
                            color=0x0099ff
                        )
                        
                        # 최대 10개까지만 표시
                        for i, buff in enumerate(buffs[:10]):
                            embed.add_field(
                                name=f"{i+1}. {buff.get('name', 'N/A')}",
                                value=f"ID: {buff.get('ids', 'N/A')} | 설명: {buff.get('descriptions', 'N/A')[:50]}...",
                                inline=False
                            )
                        
                        if len(buffs) > 10:
                            embed.set_footer(text=f"총 {len(buffs)}개 중 10개만 표시")
                        
                        # Select Menu View 생성
                        view = BuffSelectView(buffs, self.API_URL, self.headers)
                        await ctx.send(embed=embed, view=view)
                    else:
                        await ctx.send(f"❌ '{search_term}'에 대한 검색 결과가 없습니다.")
                else:
                    await ctx.send("❌ 검색 결과를 가져올 수 없습니다.")
            else:
                await ctx.send(f"❌ **HTTP 오류**: {response.status_code}")
                
        except Exception as e:
            await ctx.send(f"❌ **오류**: {str(e)}")

    @app_commands.command(name="버프검색", description="버프를 검색합니다 (부분 일치)")
    @app_commands.describe(search_term="검색할 버프 이름")
    async def buff_search_slash(self, interaction: discord.Interaction, search_term: str):
        """버프를 검색합니다. (부분 일치)"""
        try:
            # 검색 API 엔드포인트 (실제 API에 맞게 수정 필요)
            search_url = f"{self.API_URL}buffs"
            params = {'search': search_term}
            
            response = requests.get(search_url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('data'):
                    buffs = data.get('data', [])
                    
                    if len(buffs) > 0:
                        embed = discord.Embed(
                            title=f"🔍 '{search_term}' 검색 결과",
                            description="아래 드롭다운에서 상세 정보를 보고 싶은 버프를 선택하세요!",
                            color=0x0099ff
                        )
                        
                        # 최대 10개까지만 표시
                        for i, buff in enumerate(buffs[:10]):
                            embed.add_field(
                                name=f"{i+1}. {buff.get('name', 'N/A')}",
                                value=f"ID: {buff.get('ids', 'N/A')} | 설명: {buff.get('descriptions', 'N/A')[:50]}...",
                                inline=False
                            )
                        
                        if len(buffs) > 10:
                            embed.set_footer(text=f"총 {len(buffs)}개 중 10개만 표시")
                        
                        # Select Menu View 생성
                        view = BuffSelectView(buffs, self.API_URL, self.headers)
                        await interaction.response.send_message(embed=embed, view=view)
                    else:
                        await interaction.response.send_message(f"❌ '{search_term}'에 대한 검색 결과가 없습니다.")
                else:
                    await interaction.response.send_message("❌ 검색 결과를 가져올 수 없습니다.")
            else:
                await interaction.response.send_message(f"❌ **HTTP 오류**: {response.status_code}")
                
        except Exception as e:
            await interaction.response.send_message(f"❌ **오류**: {str(e)}")

    @buff_info.error
    async def buff_info_error(self, ctx, error):
        """버프 명령어 오류 처리"""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ **사용법**: `!버프 <버프이름>`")
        else:
            await ctx.send(f"❌ **오류**: {str(error)}")

    @buff_search.error
    async def buff_search_error(self, ctx, error):
        """버프 검색 명령어 오류 처리"""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ **사용법**: `!버프검색 <검색어>`")
        else:
            await ctx.send(f"❌ **오류**: {str(error)}")

async def setup(bot):
    await bot.add_cog(BuffCog(bot))
