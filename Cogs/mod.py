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