# Tree-of-savior Automatic Matching Challenge Routine discord Bot

ktos automatic matching challenge routine Bot

use Python 3.10

```bash
pip install discord.py

```

## Features / 기능 소개

### 1. Challenge Menu (Cogs.challenge)
**챌린지 메뉴**
- `/menu` - 챌린지 정보를 확인할 수 있는 메인 메뉴
- Interactive menu providing access to:
  - Today's Challenge (오늘의 챌린지)
  - Tomorrow's Challenge (내일의 챌린지)
  - Weekly Challenge (주간 챌린지)
  - Relics Information (면류관 정보)
  - Skill Enchant Table (스킬 연성표)
  - Common ToS Terms (공통 용어)

### 2. Auto Challenge Map (Cogs.AutoCM)
**자동 챌린지맵 업로드**
- `/setchallenge` - Set channel for auto challenge map uploads (관리자 전용)
- `/checkchallenge` - Check current challenge channel setting
- `/removechallenge` - Remove challenge channel setting (관리자 전용)
- Automatically posts daily challenge maps at 00:00 KST (매일 한국시간 00:00에 챌린지맵 자동 업로드)

### 3. Game Updates (Cogs.autoupdate)
**게임 업데이트 자동 알림**
- `/set_channel_update` - Set channel for automatic game update notifications
- Monitors Steam RSS feed for Tree of Savior updates
- Automatically posts new game updates with rich embeds (스팀 RSS 피드를 모니터링하여 새로운 게임 업데이트를 자동으로 알림)

### 4. Player Count (Cogs.new_ingame)
**동접자 수 조회**
- `/동접자` - Shows current online players across all servers
- Displays player counts for:
  - KTOS (한국 서버)
  - JTOS (일본 서버)
  - ITOS (글로벌 서버 - 북미, 남미, 통합, W Server)

### 5. Buff Information (Cogs.buffs)
**버프 정보 조회 (KTOS 기준)**
- `/버프 [buff_name]` - Search for buff information by name (KTOS 기준으로 조회)
- `/버프검색 [search_term]` - Search buffs with partial matching (부분 검색 지원)
- Shows detailed buff information based on KTOS data including:
  - Duration (지속 시간)
  - Description (설명)
  - Category (분류)
  - Removability (제거 가능 여부)

### 6. Item Information (Cogs.items)
**아이템 정보 조회 (KTOS 기준)**
- `/아이템검색 [item_name]` - Search items by name (KTOS 기준, 부분 검색 지원)
- `/아이템상세 [item_id]` - Get detailed item information by ID
- `/아이템목록 [page] [limit] [weekly]` - Browse item list with pagination
- Shows comprehensive item details based on KTOS data including:
  - Grade/Rarity (등급)
  - Category (카테고리)
  - Description (설명)
  - Equipment stats (장비 정보)

## Bot Invite link
https://discord.com/oauth2/authorize?client_id=1069616255880925204


## Contact / 문의
mail : gihyeon@gihyeon.com  
discord : 21in7


## API KEY
각 서비스 api key를 따로 발급하셔야 합니다.  
You need to obtain API keys for each service.

steam web api : https://steamcommunity.com/dev/apikey