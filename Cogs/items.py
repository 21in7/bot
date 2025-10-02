import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
import requests
import json
import urllib.parse
from typing import Optional
from datetime import datetime, timedelta
import calendar

API_URL = "https://api.gihyeonofsoul.com/api/"

class ItemSelectView(View):
    def __init__(self, items_data, api_url, headers):
        super().__init__(timeout=60)
        self.items_data = items_data or []  # None일 경우 빈 리스트로 초기화
        self.API_URL = api_url
        self.headers = headers
        
        # Select Menu 생성 (안전하게 처리)
        if self.items_data:
            try:
                options = []
                for i, item in enumerate(self.items_data[:25]):  # Discord는 최대 25개 옵션만 지원
                    if item:  # item이 None이 아닌지 확인
                        # 모든 필드를 안전하게 처리
                        name = item.get('name')
                        if name and name != 'null' and str(name).strip():
                            label_text = str(name)[:100]
                        else:
                            label_text = 'N/A'
                        
                        descriptions = item.get('descriptions')
                        if descriptions and descriptions != 'null' and str(descriptions).strip():
                            description_text = str(descriptions)[:100]
                        else:
                            description_text = '설명 없음'
                        
                        option = discord.SelectOption(
                            label=label_text,
                            description=description_text,
                            value=str(i),
                            emoji="📦"
                        )
                        options.append(option)
                
                select = Select(
                    placeholder="상세 정보를 보고 싶은 아이템을 선택하세요",
                    options=options
                )
                select.callback = self.on_select
                self.add_item(select)
            except Exception as e:
                print(f"[DEBUG] Select Menu 생성 오류: {e}")
                raise
    
    async def on_select(self, interaction: discord.Interaction):
        try:
            selected_index = int(interaction.data['values'][0])
            
            # 안전하게 인덱스 확인
            if not self.items_data or selected_index >= len(self.items_data):
                await interaction.response.send_message("❌ **오류**: 선택한 아이템을 찾을 수 없습니다.", ephemeral=True)
                return
                
            selected_item = self.items_data[selected_index]
            
            # 선택된 아이템의 상세 정보를 가져와서 표시
            await self.show_item_details(interaction, selected_item)
        except Exception as e:
            await interaction.response.send_message(f"❌ **오류**: {str(e)}", ephemeral=True)
    
    async def show_item_details(self, interaction: discord.Interaction, item_data):
        """선택된 아이템의 상세 정보를 표시합니다."""
        try:
            # 안전하게 데이터 확인
            if not item_data:
                await interaction.response.send_message("❌ **오류**: 아이템 데이터를 찾을 수 없습니다.", ephemeral=True)
                return
                
            # 임베드 생성 (안전하게 처리)
            name = item_data.get('name')
            title_text = str(name) if name and name != 'null' else 'N/A'
            
            descriptions = item_data.get('descriptions')
            desc_text = str(descriptions) if descriptions and descriptions != 'null' else 'N/A'
            
            embed = discord.Embed(
                title=f"📦 {title_text}",
                description=desc_text,
                color=0x4ecdc4
            )
            
            # 기본 정보 추가
            embed.add_field(
                name="🆔 아이템 ID", 
                value=item_data.get('id', 'N/A'), 
                inline=True
            )
            
            embed.add_field(
                name="⭐ 등급", 
                value=item_data.get('grade', 'N/A'), 
                inline=True
            )
            
            embed.add_field(
                name="📂 카테고리", 
                value=item_data.get('category', 'N/A'), 
                inline=True
            )
            
            # 아이콘 URL이 있으면 썸네일로 설정
            icon_url = item_data.get('icon_url')
            if icon_url:
                embed.set_thumbnail(url=icon_url)
            
            # 추가 정보
            if item_data.get('type'):
                embed.add_field(
                    name="🏷️ 타입", 
                    value=item_data.get('type'), 
                    inline=True
                )
            
            if item_data.get('weight'):
                embed.add_field(
                    name="⚖️ 무게", 
                    value=item_data.get('weight'), 
                    inline=True
                )
            
            if item_data.get('tradability'):
                embed.add_field(
                    name="🔄 거래 가능", 
                    value=item_data.get('tradability'), 
                    inline=True
                )
            
            # 푸터에 타임스탬프
            embed.set_footer(text=f"요청자: {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ **오류**: {str(e)}", ephemeral=True)

class ItemCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    @app_commands.command(name="아이템목록", description="최근 생성된 아이템 목록을 조회합니다")
    @app_commands.describe(page="조회할 페이지 번호 (기본값: 1)", limit="페이지당 아이템 수 (기본값: 10)", weekly="매주 화요일 기준으로 필터링 (기본값: False)")
    async def item_list(self, interaction: discord.Interaction, page: int = 1, limit: int = 10, weekly: bool = False):
        """최근 생성된 아이템 목록을 조회합니다"""
        await interaction.response.defer()
        
        try:
            # 화요일 기준 필터링이 활성화된 경우 날짜 범위 계산
            date_filter = ""
            if weekly:
                start_date, end_date = self.get_tuesday_week_range()
                date_filter = f"&start_date={start_date}&end_date={end_date}"
            
            url = f"{API_URL}items?page={page}&limit={limit}{date_filter}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    items_data = data.get('data', [])
                    total_count = data.get('total', 0)
                    current_page = data.get('page', 1)
                    total_pages = data.get('total_pages', 1)
                    
                    if not items_data:
                        embed = discord.Embed(
                            title="📦 아이템 목록",
                            description="조회된 아이템이 없습니다.",
                            color=0xff6b6b
                        )
                        await interaction.followup.send(embed=embed)
                        return
                    
                    # 임베드 생성
                    title = "📦 최근 생성된 아이템 목록"
                    description = f"총 {total_count}개의 아이템 중 {current_page}/{total_pages} 페이지"
                    
                    if weekly:
                        start_date, end_date = self.get_tuesday_week_range()
                        title = "📅 화요일 기준 주간 아이템 목록"
                        description = f"📅 기간: {start_date} ~ {end_date}\n총 {total_count}개의 아이템 중 {current_page}/{total_pages} 페이지"
                    
                    embed = discord.Embed(
                        title=title,
                        description=description,
                        color=0x4ecdc4
                    )
                    
                    # 아이템 목록 추가
                    item_list = ""
                    for i, item in enumerate(items_data, 1):
                        item_name = item.get('name', 'N/A')
                        item_id = item.get('id', 'N/A')
                        item_grade = item.get('grade', 'N/A')
                        item_category = item.get('category', 'N/A')
                        
                        # 아이템 정보를 클릭 가능한 링크로 표시
                        item_list += f"**{i}.** [{item_name}](https://api.gihyeonofsoul.com/api/items/{item_id}) "
                        item_list += f"`ID: {item_id}` `등급: {item_grade}` `카테고리: {item_category}`\n"
                    
                    embed.add_field(name="아이템 목록", value=item_list[:1024], inline=False)
                    
                    # 페이지 정보 추가
                    embed.set_footer(text=f"페이지 {current_page}/{total_pages} • 총 {total_count}개 아이템")
                    
                    # 페이지네이션 버튼 생성
                    view = ItemListView(self, current_page, total_pages, limit, weekly)
                    await interaction.followup.send(embed=embed, view=view)
                    
                else:
                    embed = discord.Embed(
                        title="❌ 오류",
                        description=f"API 오류: {data.get('message', '알 수 없는 오류')}",
                        color=0xff6b6b
                    )
                    await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="❌ 오류",
                    description=f"HTTP 오류: {response.status_code}",
                    color=0xff6b6b
                )
                await interaction.followup.send(embed=embed)
                
        except requests.exceptions.ConnectionError:
            embed = discord.Embed(
                title="❌ 연결 오류",
                description="API 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.",
                color=0xff6b6b
            )
            await interaction.followup.send(embed=embed)
        except requests.exceptions.Timeout:
            embed = discord.Embed(
                title="❌ 타임아웃",
                description="요청 시간이 초과되었습니다. 서버가 느릴 수 있으니 잠시 후 다시 시도해주세요.",
                color=0xff6b6b
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ 오류",
                description=f"예상치 못한 오류가 발생했습니다: {str(e)}",
                color=0xff6b6b
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="아이템검색", description="아이템 이름으로 검색합니다 (부분 검색 지원)")
    @app_commands.describe(name="검색할 아이템 이름 (일부만 입력해도 됩니다)")
    async def item_search(self, interaction: discord.Interaction, name: str):
        """아이템 이름으로 검색합니다 (부분 검색 지원)"""
        await interaction.response.defer()
        
        try:
            # 부분 검색을 위해 search 파라미터 사용 (URL 인코딩)
            encoded_name = urllib.parse.quote(name)
            url = f"{API_URL}items?search={encoded_name}&limit=20"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('data'):
                    items_data = data.get('data', [])
                    
                    # pagination 객체에서 total 값 가져오기 (안전하게 처리)
                    pagination = data.get('pagination')
                    if pagination and isinstance(pagination, dict):
                        total_count = pagination.get('total', 0)
                    else:
                        total_count = len(items_data)  # pagination이 없으면 데이터 길이로 대체
                    
                    if not items_data or total_count == 0:
                        embed = discord.Embed(
                            title="🔍 아이템 검색 결과",
                            description=f"'{name}'에 해당하는 아이템을 찾을 수 없습니다.",
                            color=0xff6b6b
                        )
                        await interaction.followup.send(embed=embed)
                        return
                    
                    # 검색 결과가 1개인 경우 상세 정보 표시
                    if len(items_data) == 1:
                        embed = await self.create_item_detail_embed(items_data[0])
                        await interaction.followup.send(embed=embed)
                    else:
                        # 검색 결과가 여러 개인 경우 드롭다운으로 표시
                        embed = discord.Embed(
                            title=f"🔍 '{name}' 검색 결과",
                            description="아래 드롭다운에서 상세 정보를 보고 싶은 아이템을 선택하세요!",
                            color=0x4ecdc4
                        )
                        
                        # 최대 10개까지만 표시 (안전하게 처리)
                        for i, item in enumerate(items_data[:10]):
                            try:
                                name = item.get('name', 'N/A') if item else 'N/A'
                                item_id = item.get('id', 'N/A') if item else 'N/A'
                                descriptions = item.get('descriptions') if item else None
                                
                                if descriptions and descriptions != 'null' and str(descriptions).strip():
                                    desc_preview = str(descriptions)[:50] + "..."
                                else:
                                    desc_preview = "설명 없음"
                                
                                embed.add_field(
                                    name=f"{i+1}. {name}",
                                    value=f"ID: {item_id} | 설명: {desc_preview}",
                                    inline=False
                                )
                            except Exception as e:
                                print(f"[DEBUG] 임베드 필드 추가 오류 (아이템 {i}): {e}")
                                embed.add_field(
                                    name=f"{i+1}. 오류",
                                    value="아이템 정보를 불러올 수 없습니다.",
                                    inline=False
                                )
                        
                        if total_count > 10:
                            embed.set_footer(text=f"총 {total_count}개 중 10개만 표시")
                        
                        # Select Menu View 생성
                        try:
                            view = ItemSelectView(items_data, API_URL, self.headers)
                            await interaction.followup.send(embed=embed, view=view)
                        except Exception as e:
                            print(f"[DEBUG] ItemSelectView 생성/전송 오류: {e}")
                            # View 없이 임베드만 전송
                            await interaction.followup.send(embed=embed)
                    
                else:
                    embed = discord.Embed(
                        title="❌ 오류",
                        description=f"API 오류: {data.get('message', '알 수 없는 오류')}",
                        color=0xff6b6b
                    )
                    await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="❌ 오류",
                    description=f"HTTP 오류: {response.status_code}",
                    color=0xff6b6b
                )
                await interaction.followup.send(embed=embed)
                
        except requests.exceptions.ConnectionError:
            embed = discord.Embed(
                title="❌ 연결 오류",
                description="API 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.",
                color=0xff6b6b
            )
            await interaction.followup.send(embed=embed)
        except requests.exceptions.Timeout:
            embed = discord.Embed(
                title="❌ 타임아웃",
                description="검색 시간이 초과되었습니다. 서버가 느릴 수 있으니 잠시 후 다시 시도해주세요.",
                color=0xff6b6b
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ 오류",
                description=f"검색 중 오류가 발생했습니다: {str(e)}",
                color=0xff6b6b
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="아이템상세", description="아이템 ID로 상세 정보를 조회합니다")
    @app_commands.describe(item_id="조회할 아이템 ID")
    async def item_detail(self, interaction: discord.Interaction, item_id: str):
        """아이템 ID로 상세 정보를 조회합니다"""
        await interaction.response.defer()
        
        try:
            url = f"{API_URL}items/{item_id}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    item_data = data.get('data', {})
                    
                    if not item_data:
                        embed = discord.Embed(
                            title="🔍 아이템 상세 정보",
                            description=f"ID '{item_id}'에 해당하는 아이템을 찾을 수 없습니다.",
                            color=0xff6b6b
                        )
                        await interaction.followup.send(embed=embed)
                        return
                    
                    # 아이템 상세 정보 임베드 생성
                    embed = await self.create_item_detail_embed(item_data)
                    await interaction.followup.send(embed=embed)
                    
                else:
                    embed = discord.Embed(
                        title="❌ 오류",
                        description=f"API 오류: {data.get('message', '알 수 없는 오류')}",
                        color=0xff6b6b
                    )
                    await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="❌ 오류",
                    description=f"HTTP 오류: {response.status_code}",
                    color=0xff6b6b
                )
                await interaction.followup.send(embed=embed)
                
        except requests.exceptions.ConnectionError:
            embed = discord.Embed(
                title="❌ 연결 오류",
                description="API 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.",
                color=0xff6b6b
            )
            await interaction.followup.send(embed=embed)
        except requests.exceptions.Timeout:
            embed = discord.Embed(
                title="❌ 타임아웃",
                description="조회 시간이 초과되었습니다. 서버가 느릴 수 있으니 잠시 후 다시 시도해주세요.",
                color=0xff6b6b
            )
            await interaction.followup.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ 오류",
                description=f"조회 중 오류가 발생했습니다: {str(e)}",
                color=0xff6b6b
            )
            await interaction.followup.send(embed=embed)

    async def create_item_detail_embed(self, item_data):
        """아이템 상세 정보 임베드를 생성합니다"""
        item_name = item_data.get('name', 'N/A')
        item_id = item_data.get('id', 'N/A')
        descriptions = item_data.get('descriptions', 'N/A')
        grade = item_data.get('grade', 'N/A')
        category = item_data.get('category', 'N/A')
        icon_url = item_data.get('icon_url', '')
        
        # 등급에 따른 색상 설정
        grade_colors = {
            'Common': 0x9e9e9e,
            'Uncommon': 0x4caf50,
            'Rare': 0x2196f3,
            'Epic': 0x9c27b0,
            'Legendary': 0xff9800,
            'Mythic': 0xf44336
        }
        
        color = grade_colors.get(grade, 0x4ecdc4)
        
        embed = discord.Embed(
            title=f"📦 {item_name}",
            description=descriptions,
            color=color
        )
        
        embed.add_field(name="🆔 ID", value=item_id, inline=True)
        embed.add_field(name="⭐ 등급", value=grade, inline=True)
        embed.add_field(name="📂 카테고리", value=category, inline=True)
        
        # 장비 정보가 있는 경우
        if 'equipment' in item_data and item_data['equipment']:
            equipment_info = item_data['equipment']
            equipment_text = ""
            
            for key, value in equipment_info.items():
                if value:
                    equipment_text += f"**{key}**: {value}\n"
            
            if equipment_text:
                embed.add_field(name="⚔️ 장비 정보", value=equipment_text[:1024], inline=False)
        
        # 아이콘 설정
        if icon_url:
            embed.set_thumbnail(url=icon_url)
        
        embed.set_footer(text=f"아이템 ID: {item_id}")
        
        return embed

    def get_tuesday_week_range(self):
        """현재 날짜 기준으로 화요일부터 다음 화요일까지의 날짜 범위를 반환합니다"""
        today = datetime.now()
        
        # 오늘의 요일 (월요일=0, 화요일=1, ..., 일요일=6)
        current_weekday = today.weekday()
        
        # 화요일(1)까지의 일수 계산
        days_until_tuesday = (1 - current_weekday) % 7
        if days_until_tuesday == 0 and today.weekday() != 1:  # 오늘이 화요일이 아닌 경우
            days_until_tuesday = 7
        
        # 이번 주 화요일 계산
        this_tuesday = today - timedelta(days=current_weekday) + timedelta(days=1)
        if today.weekday() > 1:  # 수요일 이후인 경우
            this_tuesday = today - timedelta(days=current_weekday) + timedelta(days=1)
        elif today.weekday() < 1:  # 월요일인 경우
            this_tuesday = today + timedelta(days=1)
        
        # 다음 주 화요일 계산
        next_tuesday = this_tuesday + timedelta(days=7)
        
        # 날짜를 YYYY-MM-DD 형식으로 변환
        start_date = this_tuesday.strftime('%Y-%m-%d')
        end_date = next_tuesday.strftime('%Y-%m-%d')
        
        return start_date, end_date

    async def get_item_list(self, page: int, limit: int, weekly: bool = False):
        """아이템 목록을 조회합니다"""
        try:
            # 화요일 기준 필터링이 활성화된 경우 날짜 범위 계산
            date_filter = ""
            if weekly:
                start_date, end_date = self.get_tuesday_week_range()
                date_filter = f"&start_date={start_date}&end_date={end_date}"
            
            url = f"{API_URL}items?page={page}&limit={limit}{date_filter}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data
            return None
        except:
            return None


class ItemListView(discord.ui.View):
    def __init__(self, cog, current_page: int, total_pages: int, limit: int, weekly: bool = False):
        super().__init__(timeout=300)
        self.cog = cog
        self.current_page = current_page
        self.total_pages = total_pages
        self.limit = limit
        self.weekly = weekly
        
        # 버튼 상태 업데이트
        self.update_buttons()
    
    def update_buttons(self):
        """버튼 상태를 업데이트합니다"""
        # 이전 페이지 버튼
        self.previous_button.disabled = self.current_page <= 1
        self.previous_button.label = f"◀️ 이전 ({self.current_page - 1})"
        
        # 다음 페이지 버튼
        self.next_button.disabled = self.current_page >= self.total_pages
        self.next_button.label = f"다음 ({self.current_page + 1}) ▶️"
        
        # 페이지 정보
        self.page_info.label = f"📄 {self.current_page}/{self.total_pages}"
    
    @discord.ui.button(label="◀️ 이전", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            await self.change_page(interaction, self.current_page - 1)
    
    @discord.ui.button(label="📄 1/1", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass  # 정보 표시용 버튼
    
    @discord.ui.button(label="다음 ▶️", style=discord.ButtonStyle.primary, disabled=True)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages:
            await self.change_page(interaction, self.current_page + 1)
    
    async def change_page(self, interaction: discord.Interaction, new_page: int):
        """페이지를 변경합니다"""
        await interaction.response.defer()
        
        data = await self.cog.get_item_list(new_page, self.limit, self.weekly)
        
        if data:
            items_data = data.get('data', [])
            total_count = data.get('total', 0)
            current_page = data.get('page', 1)
            total_pages = data.get('total_pages', 1)
            
            # 현재 페이지 정보 업데이트
            self.current_page = current_page
            self.total_pages = total_pages
            self.update_buttons()
            
            if items_data:
                # 임베드 생성
                title = "📦 최근 생성된 아이템 목록"
                description = f"총 {total_count}개의 아이템 중 {current_page}/{total_pages} 페이지"
                
                if self.weekly:
                    start_date, end_date = self.cog.get_tuesday_week_range()
                    title = "📅 화요일 기준 주간 아이템 목록"
                    description = f"📅 기간: {start_date} ~ {end_date}\n총 {total_count}개의 아이템 중 {current_page}/{total_pages} 페이지"
                
                embed = discord.Embed(
                    title=title,
                    description=description,
                    color=0x4ecdc4
                )
                
                # 아이템 목록 추가
                item_list = ""
                for i, item in enumerate(items_data, 1):
                    item_name = item.get('name', 'N/A')
                    item_id = item.get('id', 'N/A')
                    item_grade = item.get('grade', 'N/A')
                    item_category = item.get('category', 'N/A')
                    
                    item_list += f"**{i}.** [{item_name}](https://api.gihyeonofsoul.com/api/items/{item_id}) "
                    item_list += f"`ID: {item_id}` `등급: {item_grade}` `카테고리: {item_category}`\n"
                
                embed.add_field(name="아이템 목록", value=item_list[:1024], inline=False)
                embed.set_footer(text=f"페이지 {current_page}/{total_pages} • 총 {total_count}개 아이템")
                
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                embed = discord.Embed(
                    title="📦 아이템 목록",
                    description="조회된 아이템이 없습니다.",
                    color=0xff6b6b
                )
                await interaction.edit_original_response(embed=embed, view=self)
        else:
            embed = discord.Embed(
                title="❌ 오류",
                description="페이지를 불러올 수 없습니다.",
                color=0xff6b6b
            )
            await interaction.edit_original_response(embed=embed, view=self)


async def setup(bot):
    await bot.add_cog(ItemCog(bot))
