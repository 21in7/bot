import json
import datetime
from discord import File

# challenge.json 파일 로드
with open("/home/ubuntu/bot/challenge.json", "r") as file:
    challenge_data = json.load(file)

# 오늘의 챌린지 맵
def Today_challenge():
    d = datetime.datetime.now()
    str_now = str(d.strftime("%y-%m-%d\n"))
    # 홀수달일 때는 'om', 짝수달일 때는 'em'에서 데이터를 가져옴
    data_key = 'om' if d.month % 2 != 0 else 'em'
    # 날짜에 맞는 id 찾기 (1부터 시작하므로 d.day를 그대로 사용)
    challenge = challenge_data[data_key][d.day - 1]  # 리스트는 0부터 시작하므로 d.day - 1
    challenge_name = challenge['name'].replace("\\n", "\n")
    send_message = f"{str_now}{challenge_name}"
    return send_message

# 오늘의 챌린지 맵 파일
def Today_file():
    d = datetime.datetime.now()
    data_key = 'om' if d.month % 2 != 0 else 'em'
    challenge = challenge_data[data_key][d.day - 1]
    file_path = f"./{data_key}/{challenge['image']}"  # 파일 경로 수정
    file = File(file_path, filename="image.jpg")
    return file

# 내일의 챌린지 맵
def Tomorrow_challenge():
    d = datetime.datetime.now() + datetime.timedelta(days=1)
    str_tomorrow = str(d.strftime("%y-%m-%d\n"))
    data_key = 'om' if d.month % 2 != 0 else 'em'
    challenge = challenge_data[data_key][d.day - 1]
    send_message = f"{str_tomorrow}{challenge['name']}"
    return send_message

# 내일의 챌린지 맵 파일
def Tomorrow_file():
    d = datetime.datetime.now() + datetime.timedelta(days=1)
    data_key = 'om' if d.month % 2 != 0 else 'em'
    challenge = challenge_data[data_key][d.day - 1]
    file_path = f"./{data_key}/{challenge['image']}"
    file = File(file_path, filename="image.jpg")
    return file

def Weekend_challenge():
    """오늘 기준 이번 주 월요일부터 일요일까지 7개의 챌린지 name을 반환"""
    today = datetime.datetime.now()
    
    # 이번 주 월요일 찾기 (월요일 = 0, 일요일 = 6)
    days_since_monday = today.weekday()  # 오늘이 월요일부터 몇일 지났는지
    monday = today - datetime.timedelta(days=days_since_monday)
    
    weekly_challenges = []
    
    for i in range(7):  # 월요일부터 일요일까지 7일
        current_day = monday + datetime.timedelta(days=i)
        
        # 날짜 문자열 생성
        date_str = current_day.strftime("%y-%m-%d")
        
        # 홀수달은 'om', 짝수달은 'em'
        data_key = 'om' if current_day.month % 2 != 0 else 'em'
        
        # 해당 날짜의 챌린지 데이터 가져오기
        try:
            challenge = challenge_data[data_key][current_day.day - 1]
            challenge_name = challenge['name'].replace("\\n", ",")
            day_name = ['월', '화', '수', '목', '금', '토', '일'][i]
            send_message = f"{day_name}({date_str}) : {challenge_name}"
            weekly_challenges.append(send_message)
        except IndexError:
            # 해당 날짜의 데이터가 없는 경우 (예: 31일이 없는 달)
            day_name = ['월', '화', '수', '목', '금', '토', '일'][i]
            send_message = f"{day_name}({date_str}) : 데이터 없음"
            weekly_challenges.append(send_message)
    
    # Discord embed에서 한 줄씩 표시되도록 개행 문자로 연결
    return "\n".join(weekly_challenges)

# 주간 챌린지 특정 요일의 챌린지 정보 반환
def Weekend_day_challenge(day_offset):
    """
    day_offset: 0(월) ~ 6(일)
    이번 주 특정 요일의 챌린지 정보를 반환
    """
    today = datetime.datetime.now()
    days_since_monday = today.weekday()
    monday = today - datetime.timedelta(days=days_since_monday)
    target_day = monday + datetime.timedelta(days=day_offset)
    
    date_str = target_day.strftime("%y-%m-%d")
    data_key = 'om' if target_day.month % 2 != 0 else 'em'
    challenge = challenge_data[data_key][target_day.day - 1]
    challenge_name = challenge['name'].replace("\\n", "\n")
    
    return f"{date_str}\n{challenge_name}"

# 주간 챌린지 특정 요일의 파일 반환
def Weekend_file(day_offset):
    """
    day_offset: 0(월) ~ 6(일)
    이번 주 특정 요일의 챌린지 이미지 파일을 반환
    """
    today = datetime.datetime.now()
    days_since_monday = today.weekday()
    monday = today - datetime.timedelta(days=days_since_monday)
    target_day = monday + datetime.timedelta(days=day_offset)
    
    data_key = 'om' if target_day.month % 2 != 0 else 'em'
    challenge = challenge_data[data_key][target_day.day - 1]
    file_path = f"./{data_key}/{challenge['image']}"
    file = File(file_path, filename="image.jpg")
    return file