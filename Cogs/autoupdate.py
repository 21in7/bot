import asyncio
import json
import os
from discord.ext import commands
from discord import Embed, SelectOption
import feedparser
import re
import hashlib
from discord.ui import Select, View, Button
from discord import app_commands, Interaction
from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup
import aiohttp

class UpdateAuto(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.update_channel_ids = self.load_update_channels()  # 서버별 업데이트 채널 ID 저장
        self.latest_update_title = self.load_latest_updates()  # 마지막 업데이트 상태 로드
        self.cleanup_invalid_entries()  # 유효하지 않은 항목들 정리
        self.update_task = bot.loop.create_task(self.check_for_updates())

    def _normalized_link(self, link: str) -> str:
        try:
            if not link:
                return ""
            parsed = urlparse(link)
            # 쿼리스트링과 프래그먼트를 제거해 추적 파라미터 변화에 영향받지 않도록 함
            return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
        except Exception:
            return link or ""

    def _compute_entry_identity(self, entry) -> str:
        # 1차: 안정적 id 사용
        entry_id = entry.get('id')
        if entry_id:
            return entry_id
        # 2차: 정규화된 링크 사용
        normalized_link = self._normalized_link(entry.get('link', ''))
        if normalized_link:
            return normalized_link
        # 3차: 제목/게시일/내용 해시 기반 식별자
        title = entry.get('title', '') or ''
        published = entry.get('published', '') or entry.get('updated', '') or ''
        # feedparser는 summary/description 중 하나만 제공할 수 있음
        raw_desc = entry.get('summary', '') or entry.get('description', '') or ''
        cleaned_desc = re.sub(r'<.*?>', '', raw_desc)
        hash_base = f"{title}\n{published}\n{cleaned_desc}"
        content_hash = hashlib.sha256(hash_base.encode('utf-8')).hexdigest()[:16]
        return f"fallback:{title}|{published}|{content_hash}"

    def extract_images_from_content(self, content: str) -> list:
        """HTML 내용에서 이미지 URL들을 추출합니다."""
        soup = BeautifulSoup(content, 'html.parser')
        images = []
        
        # img 태그에서 이미지 URL 추출
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                images.append(src)
        
        # 스팀 특정 이미지 패턴도 찾기
        steam_img_pattern = r'https://cdn\.akamai\.steamstatic\.com/steam/apps/\d+/.*?\.(jpg|jpeg|png|gif)'
        steam_images = re.findall(steam_img_pattern, content)
        for img in steam_images:
            if img not in images:
                images.append(img)
        
        return images[:5]  # 최대 5개 이미지만 반환

    def extract_links_from_content(self, content: str) -> list:
        """HTML 내용에서 링크들을 추출합니다."""
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        
        # a 태그에서 링크 추출
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href', '')
            text = a_tag.get_text().strip()
            if href and text:
                links.append({
                    'url': href,
                    'text': text
                })
        
        return links[:3]  # 최대 3개 링크만 반환

    async def fetch_steam_news_detail(self, url: str) -> str:
        """스팀 공지 상세 페이지를 가져와서 숨겨진 테이블 데이터를 추출합니다."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        return html_content
        except Exception as e:
            print(f"스팀 공지 상세 페이지 가져오기 실패: {e}")
        return ""

    def extract_hidden_tables(self, html_content: str) -> list:
        """HTML에서 숨겨진 테이블 데이터를 추출합니다."""
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = []
        
        # 숨겨진 div나 span에서 테이블 데이터 찾기
        hidden_elements = soup.find_all(['div', 'span'], style=lambda x: x and 'display: none' in x)
        
        for element in hidden_elements:
            # 테이블 형태의 데이터 찾기
            table_data = element.get_text().strip()
            if table_data and len(table_data) > 10:  # 의미있는 데이터만
                # 불필요한 내비게이션 항목이 포함된 데이터는 제외
                banned_phrases = {"home", "discovery queue", "wishlist", "points shop", "news", "stats"}
                if not any(phrase in table_data.lower() for phrase in banned_phrases):
                    tables.append(table_data)
        
        # JavaScript 변수에서 테이블 데이터 찾기
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # JSON 형태의 데이터 찾기
                json_pattern = r'\{[^{}]*"table"[^{}]*\}'
                matches = re.findall(json_pattern, script.string)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if 'table' in data:
                            table_str = str(data['table'])
                            # 불필요한 내비게이션 항목이 포함된 데이터는 제외
                            banned_phrases = {"home", "discovery queue", "wishlist", "points shop", "news", "stats"}
                            if not any(phrase in table_str.lower() for phrase in banned_phrases):
                                tables.append(table_str)
                    except:
                        pass
        
        return tables

    def format_table_data(self, table_data: str) -> str:
        """테이블 데이터를 디스코드에서 보기 좋게 포맷팅합니다."""
        # 줄바꿈으로 구분된 데이터를 정리
        lines = table_data.split('\n')
        formatted_lines = []
        
        # 언어 목록이나 불필요한 내용을 더 강력하게 필터링
        language_indicators = {
            "chinese", "japanese", "korean", "thai", "bulgarian", "czech", "danish", 
            "german", "spanish", "greek", "french", "italian", "indonesian", 
            "hungarian", "dutch", "norwegian", "polish", "portuguese", "romanian", 
            "russian", "finnish", "swedish", "turkish", "vietnamese", "ukrainian",
            "简体中文", "繁體中文", "日本語", "한국어", "ไทย", "български", "čeština",
            "dansk", "deutsch", "español", "ελληνικά", "français", "italiano",
            "bahasa indonesia", "magyar", "nederlands", "norsk", "polski", "português",
            "română", "русский", "suomi", "svenska", "türkçe", "tiếng việt", "українська"
        }
        
        for line in lines:
            line = line.strip()
            if line:
                # 탭이나 여러 공백으로 구분된 데이터를 |로 변환
                if '\t' in line:
                    parts = line.split('\t')
                    formatted_line = ' | '.join(part.strip() for part in parts if part.strip())
                elif '  ' in line:  # 여러 공백
                    parts = re.split(r'\s{2,}', line)
                    formatted_line = ' | '.join(part.strip() for part in parts if part.strip())
                else:
                    formatted_line = line
                
                # 스팀 내비게이션 및 언어 목록 필터링
                banned_phrases = {
                    "home", "discovery queue", "wishlist", "points shop", "news", "stats",
                    "report a translation problem", "translation", "language", "languages"
                }
                
                line_lower = formatted_line.lower()
                
                # 금지된 구문이 포함되어 있으면 제외
                if any(phrase in line_lower for phrase in banned_phrases):
                    continue
                
                # 언어 관련 내용이 포함되어 있으면 제외
                if any(lang in line_lower for lang in language_indicators):
                    continue
                
                # 구분선만 있는 라인 제외
                if re.match(r'^[-=_\s|]+$', formatted_line):
                    continue
                
                # 괄호 안에 언어명이 있는 경우 제외 (예: "简体中文 (Simplified Chinese)")
                if re.search(r'\([^)]*(chinese|japanese|korean|thai|bulgarian|czech|danish|german|spanish|greek|french|italian|indonesian|hungarian|dutch|norwegian|polish|portuguese|romanian|russian|finnish|swedish|turkish|vietnamese|ukrainian)[^)]*\)', line_lower):
                    continue

                if formatted_line:
                    formatted_lines.append(formatted_line)
        
        if formatted_lines:
            # 충분한 의미있는 데이터가 없으면 표시하지 않음 (단일 라인 등)
            if len(formatted_lines) <= 1:
                return ""
            
            # 헤더와 데이터 구분
            header = formatted_lines[0]
            data_lines = formatted_lines[1:]
            
            # 헤더 구분선 추가
            separator = '---' * (len(header.split('|')) - 1) + '---'
            
            return f"**📊 상세 데이터:**\n```\n{header}\n{separator}\n" + '\n'.join(data_lines) + "\n```"
        
        return ""

    def clean_html_content(self, content: str) -> str:
        """HTML 태그를 제거하고 깔끔한 텍스트로 변환합니다."""
        # <br /> 태그를 줄바꿈으로 변환
        content = content.replace('<br />', '\n').replace('<br>', '\n')
        
        # 스팀 특정 태그들 처리
        content = content.replace('[h5]', '**').replace('[/h5]', '**')
        content = content.replace('[b]', '**').replace('[/b]', '**')
        content = content.replace('[i]', '*').replace('[/i]', '*')
        
        # a 태그를 디스코드 마크다운 링크로 변환
        soup = BeautifulSoup(content, 'html.parser')
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href', '')
            text = a_tag.get_text()
            if href and text:
                # 디스코드 마크다운 링크 형식으로 변환
                link_markdown = f"[{text}]({href})"
                a_tag.replace_with(link_markdown)
        
        # 변환된 HTML을 문자열로 변환
        content = str(soup)
        
        # HTML 태그 제거 (a 태그는 이미 변환됨)
        cleanr = re.compile('<.*?>')
        content = re.sub(cleanr, '', content)
        
        # 연속된 줄바꿈 정리
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        return content.strip()

    async def create_rich_embed(self, entry):
        """스팀 공지처럼 풍부한 임베드를 생성합니다."""
        title = entry.get('title', '제목 없음')
        link = entry.get('link', '')
        published = entry.get('published', '')
        
        # HTML 내용 정리
        raw_content = entry.get('description', '') or entry.get('summary', '')
        cleaned_content = self.clean_html_content(raw_content)
        
        # 이미지와 링크 추출
        images = self.extract_images_from_content(raw_content)
        links = self.extract_links_from_content(raw_content)
        
        # 스팀 공지 상세 페이지에서 숨겨진 테이블 데이터 추출
        table_data = ""
        if link and "steampowered.com" in link:
            try:
                html_content = await self.fetch_steam_news_detail(link)
                if html_content:
                    hidden_tables = self.extract_hidden_tables(html_content)
                    if hidden_tables:
                        table_data = self.format_table_data(hidden_tables[0])  # 첫 번째 테이블만 사용
            except Exception as e:
                print(f"테이블 데이터 추출 실패: {e}")
        
        # 임베드 생성
        embed = Embed(
            title=title,
            description=cleaned_content[:4000] + "..." if len(cleaned_content) > 4000 else cleaned_content,
            url=link,
            color=0x1b2838  # 스팀 브랜드 컬러
        )
        
        # 게시일 추가
        if published:
            embed.add_field(name="게시일", value=published, inline=True)
        
        # 원본 링크 필드 추가
        if link:
            embed.add_field(name="원본 링크", value=f"[스팀 공지 보기]({link})", inline=True)
        
        # 공지 내부 링크들 추가
        if links:
            links_text = ""
            for i, link_info in enumerate(links, 1):
                links_text += f"{i}. [{link_info['text']}]({link_info['url']})\n"
            embed.add_field(name="📎 관련 링크", value=links_text, inline=False)
        
        # 첫 번째 이미지를 썸네일로 설정
        if images:
            embed.set_thumbnail(url=images[0])
        
        # 푸터 설정
        embed.set_footer(text="Tree of Savior - Steam 공지", icon_url="https://cdn.akamai.steamstatic.com/store/home/store_home_share.jpg")
        
        return embed, images, table_data

    def create_view_with_buttons(self, link: str) -> View:
        """링크 버튼이 포함된 View를 생성합니다."""
        view = View()
        
        # 스팀 링크 버튼
        steam_button = Button(
            label="스팀에서 보기",
            url=link,
            style=1,  # Primary (파란색)
            emoji="🎮"
        )
        view.add_item(steam_button)
        
        return view

    def load_update_channels(self):
        if not os.path.exists('json/update_channels.json'):
            return {}
        with open('json/update_channels.json', 'r') as f:
            return json.load(f)

    def save_update_channels(self):
        with open('json/update_channels.json', 'w') as f:
            json.dump(self.update_channel_ids, f, indent=4)

    def load_latest_updates(self):
        try:
            if os.path.exists('json/latest_updates.json'):
                with open('json/latest_updates.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"최근 업데이트 로드 중 오류: {e}")
        return {}

    def save_latest_updates(self):
        try:
            with open('json/latest_updates.json', 'w') as f:
                json.dump(self.latest_update_title, f, indent=4)
        except Exception as e:
            print(f"최근 업데이트 저장 중 오류: {e}")

    def cleanup_invalid_entries(self):
        """유효하지 않은 서버 ID들을 정리합니다."""
        try:
            # update_channels.json에 있는 서버 ID들만 유지
            valid_guild_ids = set(self.update_channel_ids.keys())
            
            # latest_updates.json에서 유효하지 않은 항목들 제거
            cleaned_updates = {}
            for guild_id, update_id in self.latest_update_title.items():
                if guild_id in valid_guild_ids:
                    cleaned_updates[guild_id] = update_id
                else:
                    print(f"유효하지 않은 서버 ID 정리: {guild_id}")
            
            self.latest_update_title = cleaned_updates
            self.save_latest_updates()
            print(f"정리 완료: {len(cleaned_updates)}개 서버만 유지")
            
        except Exception as e:
            print(f"정리 중 오류 발생: {e}")

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
            latest_update = feed_data.entries[0]

            # (수정) 제목 대신 고유 ID를 가져와 저장합니다. 실패 시 정규화 링크, 최후에는 콘텐츠 해시 사용
            latest_update_id = self._compute_entry_identity(latest_update)
            self.latest_update_title[str(guild_id)] = latest_update_id # guild_id를 문자열로 변환하는 것이 좋습니다.
            self.save_latest_updates() # 초기 설정 후에도 파일에 바로 저장합니다.

            # 풍부한 임베드 생성
            embed, images, table_data = await self.create_rich_embed(latest_update)
            view = self.create_view_with_buttons(latest_update.get('link', ''))
            
            channel_info = self.update_channel_ids[guild_id]
            channel = self.bot.get_channel(channel_info["channel_id"])
            if channel:
                await channel.send(embed=embed, view=view)
                
                # 테이블 데이터가 있다면 별도 메시지로 전송
                if table_data:
                    await channel.send(table_data)
                
                # 추가 이미지들이 있다면 별도 메시지로 전송
                if len(images) > 1:
                    image_message = "**📸 추가 이미지들:**\n"
                    for i, img_url in enumerate(images[1:], 1):
                        image_message += f"{i}. {img_url}\n"
                    await channel.send(image_message)
            else:
                print(f"지정된 채널을 찾을 수 없습니다: {channel_info['channel_id']}")
        except Exception as e:
            print(f"초기 업데이트 전송 중 오류 발생: {e}")

    async def check_for_updates(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            # 유효한 채널만 처리하도록 필터링
            valid_channels = {}
            for guild_id, channel_info in list(self.update_channel_ids.items()):
                channel = self.bot.get_channel(channel_info["channel_id"])
                if channel:
                    valid_channels[guild_id] = channel_info
                else:
                    print(f"유효하지 않은 채널 제거: {channel_info['channel_id']} (서버: {guild_id})")
                    # 유효하지 않은 채널 정보 제거
                    if guild_id in self.update_channel_ids:
                        del self.update_channel_ids[guild_id]
                    if str(guild_id) in self.latest_update_title:
                        del self.latest_update_title[str(guild_id)]
            
            # 유효하지 않은 채널 정보 저장
            if len(valid_channels) != len(self.update_channel_ids):
                self.save_update_channels()
                self.save_latest_updates()
            
            # 유효한 채널들에 대해서만 업데이트 확인
            for guild_id, channel_info in valid_channels.items():
                try:
                    feed_data = feedparser.parse('https://store.steampowered.com/feeds/news/app/2178420/?cc=KR&l=koreana&snr=1_2108_9__2107')
                    
                    if not feed_data.entries:
                        continue
                        
                    latest_update = feed_data.entries[0]
                    latest_update_id = self._compute_entry_identity(latest_update)

                    # 새로운 업데이트가 있을 때만 메시지 전송
                    if str(guild_id) not in self.latest_update_title or self.latest_update_title[str(guild_id)] != latest_update_id:
                        self.latest_update_title[str(guild_id)] = latest_update_id
                        self.save_latest_updates()
                        
                        # 풍부한 임베드 생성
                        embed, images, table_data = await self.create_rich_embed(latest_update)
                        view = self.create_view_with_buttons(latest_update.get('link', ''))
                        
                        channel = self.bot.get_channel(channel_info["channel_id"])
                        if channel:
                            await channel.send(embed=embed, view=view)
                            
                            # 테이블 데이터가 있다면 별도 메시지로 전송
                            if table_data:
                                await channel.send(table_data)
                            
                            # 추가 이미지들이 있다면 별도 메시지로 전송
                            if len(images) > 1:
                                image_message = "**📸 추가 이미지들:**\n"
                                for i, img_url in enumerate(images[1:], 1):
                                    image_message += f"{i}. {img_url}\n"
                                await channel.send(image_message)
                            
                            print(f"업데이트 전송 완료: {latest_update.title} (서버: {guild_id})")
                        else:
                            print(f"채널을 찾을 수 없습니다: {channel_info['channel_id']}")
                            del self.update_channel_ids[guild_id]
                            self.save_update_channels()
                            
                except Exception as e:
                    print(f"업데이트 확인 중 오류 발생 - 서버: {guild_id}, 오류: {str(e)}")
                    await asyncio.sleep(5)  # 오류 발생 시 잠시 대기
            
            await asyncio.sleep(300)  # 5분 대기

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UpdateAuto(bot))
    #bot.tree.add_command(AutoUpdate.set_update_channel)