import tkinter as tk
import tkinter.ttk as ttk
import requests
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk
import io
import tkinter.messagebox as msgbox
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import subprocess
import os
import telepot
import time
import threading
import spam

# API 엔드포인트 URL
endpoint = "http://apis.data.go.kr/1320000/LosfundInfoInqireService/getLosfundInfoAccToClAreaPd"
# 서비스키
service_key = "nzC0XJi2SwXBHZ85MgwpTlycTYqYelKfi94f+R1oVUMrCEYSZ7ociwxUPUZ8PzC0y63zFmme0KtVHKTwEy+FrQ=="
# Google Maps API 키
google_maps_api_key = 'AIzaSyCzFgc9OGnXckq1-JNhSCVGo9zIq1kSWcE'

# 텔레그램 봇 토큰
TOKEN = '6807488269:AAHODGHyjtsmajUz6ZZ4OtkPeVWkcjGqHXM'

# GUI 생성
window = tk.Tk()
window.title("분실물 조회 서비스")

# 버튼 이미지 로드 및 리사이즈 함수
def load_and_resize_image(path, size):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)

# 이미지 경로 설정 및 크기 조정
map_image_path = "C:\\Drill_cys\\Lost---Found-Service\\map_logo.png"
email_image_path = "C:\\Drill_cys\\Lost---Found-Service\\mail_logo.png"  # 여기에 이메일 이미지 경로 입력
telegram_image_path = "C:\\Drill_cys\\Lost---Found-Service\\telegram_logo.png"  # 여기에 텔레그램 이미지 경로 입력

map_image = load_and_resize_image(map_image_path, (50, 50))
email_image = load_and_resize_image(email_image_path, (50, 50))
telegram_image = load_and_resize_image(telegram_image_path, (50, 50))

# program name
program_name_label = tk.Label(window, text="분실물 조회 서비스", font=("Helvetica", 24))
program_name_label.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

# map/mail
map_button = tk.Button(window, image=map_image, width=50, command=lambda: open_map())
map_button.grid(row=0, column=4, padx=10, pady=10)

mail_button = tk.Button(window, image=email_image, width=50, command=lambda: open_email_window())
mail_button.grid(row=0, column=5, padx=10, pady=10)

image_label = tk.Label(window)
image_label.grid(row=2, column=4, columnspan=2, padx=10, pady=10)

# 물품분류 카테고리
category_label = tk.Label(window, text="물품분류")
category_label.grid(row=3, column=0, padx=10, pady=10)

category_combobox = ttk.Combobox(window)
category_combobox['values'] = (
    " - ", "가방", "도서용품", "서류", "산업용품", "스포츠용품", "자동차", "전자기기", "지갑", "컴퓨터",
    "휴대폰", "의류", "현금", "유가증권", "증명서", "귀금속", "카드", "쇼핑백", "악기", "유류품",
    "무주물", "기타"
)
category_combobox.grid(row=3, column=1, columnspan=3, padx=10, pady=10)

# 습득일자 시작일 카테고리
start_date_label = tk.Label(window, text="습득일자(시작일) ex)20240524")
start_date_label.grid(row=5, column=0, padx=10, pady=10)

start_date_entry = tk.Entry(window)
start_date_entry.grid(row=5, column=1, columnspan=3, padx=10, pady=10)

# 습득일자 종료일 카테고리
end_date_label = tk.Label(window, text="습득일자(종료일) ex)20240525")
end_date_label.grid(row=6, column=0, padx=10, pady=10)

end_date_entry = tk.Entry(window)
end_date_entry.grid(row=6, column=1, columnspan=3, padx=10, pady=10)

# 습득지역 카테고리
location_label = tk.Label(window, text="습득지역")
location_label.grid(row=7, column=0, padx=10, pady=10)

location_combobox = ttk.Combobox(window)
location_combobox['values'] = (
    " - ", "강원", "경기", "경남", "경북", "광주", "대구", "대전", "부산", "서울", "세종", "울산", "인천", "전남", "전북", "제주", "충남", "충북")
location_combobox.grid(row=7, column=1, columnspan=3, padx=10, pady=10)

# 리스트박스 추가
result_listbox = tk.Listbox(window, height=10, width=100)
result_listbox.grid(row=8, column=0, columnspan=6, padx=10, pady=10)

# 리스트박스 스크롤바 추가
scrollbar = tk.Scrollbar(window)
scrollbar.grid(row=8, column=6, sticky='ns')
result_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=result_listbox.yview)

previous_filters = {
    "category": None,
    "start_date": None,
    "end_date": None,
    "location": None
}

# 갱신 버튼에 갱신 함수 연결
refresh_button = tk.Button(window, text="갱신", width=10, height=2, command=lambda: refresh())
refresh_button.grid(row=9, column=7, columnspan=2, padx=10, pady=20)

# 검색 버튼
search_button = tk.Button(window, text="검색", width=20, height=2)
search_button.grid(row=9, column=0, columnspan=6, padx=10, pady=20)


def show_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image_data = response.content
        image = Image.open(io.BytesIO(image_data))

        max_width = 200
        max_height = 200
        image.thumbnail((max_width, max_height), Image.LANCZOS)

        photo = ImageTk.PhotoImage(image)

        image_label.config(image=photo)
        image_label.image = photo
    except requests.exceptions.RequestException as e:
        result_listbox.insert(tk.END, f"이미지 요청 오류: {e}\n")
    except IOError as e:
        result_listbox.insert(tk.END, f"이미지 처리 오류: {e}\n")
    except Exception as e:
        result_listbox.insert(tk.END, f"예기치 않은 오류가 발생했습니다: {e}\n")

def on_listbox_select(event):
    selected = event.widget.curselection()
    if selected:
        index = selected[0]
        item = event.widget.get(index)
        start = item.find('이미지: ') + len('이미지: ')
        end = item.find(', 물품명: ')
        image_url = item[start:end]
        show_image(image_url)

result_listbox.bind('<<ListboxSelect>>', on_listbox_select)



def find_nearby_police_stations(location):
    lat, lng = get_location_coordinates(location)
    if lat is None or lng is None:
        result_listbox.insert(tk.END, "해당 지역의 좌표를 찾을 수 없습니다.\n")
        return

    police_stations = []
    radius = 10000  # 10km 반경으로 검색
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type=policestation&key={google_maps_api_key}"

    while url:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            police_stations.extend(data.get("results", []))
            url = data.get("next_page_token")
            if url:
                url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={url}&key={google_maps_api_key}"
        else:
            break

    if not police_stations:
        result_listbox.insert(tk.END, "해당 지역에 경찰서가 없습니다.\n")
    else:
        show_map_with_stations(lat, lng, police_stations)


def show_map_with_stations(lat, lng, stations):
    markers = "&".join([
                           f"markers=color:red%7Clabel:P%7C{station['geometry']['location']['lat']},{station['geometry']['location']['lng']}"
                           for station in stations])
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom=12&size=600x400&{markers}&key={google_maps_api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        image_data = response.content
        image = Image.open(io.BytesIO(image_data))
        photo = ImageTk.PhotoImage(image)

        # 새로운 창 생성
        new_window = tk.Toplevel(window)
        new_window.title("경찰서 지도")

        new_image_label = tk.Label(new_window, image=photo)
        new_image_label.image = photo
        new_image_label.pack(padx=10, pady=10)

def open_map():
    location = location_combobox.get()
    location_map = {
        "강원": "Gangwon-do",
        "경기": "Gyeonggi-do",
        "경남": "Gyeongsangnam-do",
        "경북": "Gyeongsangbuk-do",
        "광주": "Gwangju",
        "대구": "Daegu",
        "대전": "Daejeon",
        "부산": "Busan",
        "서울": "Seoul",
        "세종": "Sejong",
        "울산": "Ulsan",
        "인천": "Incheon",
        "전남": "Jeollanam-do",
        "전북": "Jeollabuk-do",
        "제주": "Jeju",
        "충남": "Chungcheongnam-do",
        "충북": "Chungcheongbuk-do"
    }
    if location in location_map:
        find_nearby_police_stations(location_map[location])


def get_location_coordinates(location_name):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location_name}&key={google_maps_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
    return None, None


# 갱신 버튼 함수
def refresh():
    global previous_filters

    category = previous_filters["category"]
    start_date = previous_filters["start_date"]
    end_date = previous_filters["end_date"]
    location = previous_filters["location"]
    params = {
        "serviceKey": service_key,
        "pageNo": "1",
        "numOfRows": "100",
        "PRDT_CL_CD_01": category,
        "START_YMD": start_date,
        "END_YMD": end_date,
        "N_FD_LCT_CD": location
    }
    response = requests.get(endpoint, params=params)
    root = ET.fromstring(response.content)

    # 결과 파싱 및 출력
    result_listbox.delete(0, tk.END)
    items = root.findall("body/items/item")
    for item in items:
        atcId = item.findtext("atcId")
        depPlace = item.findtext("depPlace")
        fdFilePathImg = item.findtext("fdFilePathImg")
        fdPrdtNm = item.findtext("fdPrdtNm")
        fdSbjt = item.findtext("fdSbjt")
        fdSn = item.findtext("fdSn")
        fdYmd = item.findtext("fdYmd")
        prdtClNm = item.findtext("prdtClNm")
        rnum = item.findtext("rnum")
        result_listbox.insert(tk.END,
                              f"관리ID: {atcId}, 보관장소: {depPlace}, 이미지: {fdFilePathImg}, 물품명: {fdPrdtNm}, 게시제목: {fdSbjt}, 습득순번: {fdSn}, 습득일자: {fdYmd}, 물품분류명: {prdtClNm}, 일련번호: {rnum}\n")

    msgbox.showinfo("갱신 완료", "검색 결과가 갱신되었습니다.")


# 검색 함수
def search():
    global previous_filters
    category = category_combobox.get()
    if category == "가방":
        category = "PRA000"
    elif category == "도서용품":
        category = "PRB000"
    elif category == " - ":
        category = None
    elif category == "서류":
        category = "PRC000"
    elif category == "산업용품":
        category = "PRD000"
    elif category == "스포츠용품":
        category = "PRE000"
    elif category == "자동차":
        category = "PRF000"
    elif category == "전자기기":
        category = "PRG000"
    elif category == "지갑":
        category = "PRH000"
    elif category == "컴퓨터":
        category = "PRI000"
    elif category == "휴대폰":
        category = "PRJ000"
    elif category == "의류":
        category = "PRK000"
    elif category == "현금":
        category = "PRL000"
    elif category == "유가증권":
        category = "PRM000"
    elif category == "증명서":
        category = "PRN000"
    elif category == "귀금속":
        category = "PRO000"
    elif category == "카드":
        category = "PRP000"
    elif category == "쇼핑백":
        category = "PRQ000"
    elif category == "악기":
        category = "PRR000"
    elif category == "유류품":
        category = "PRX000"
    elif category == "무주물":
        category = "PRY000"
    elif category == "기타":
        category = "PRZ000"
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    location = location_combobox.get()
    if location == "강원":
        location = "LCH000"
    elif location == "경기":
        location = "LCI000"
    elif location == " - ":
        location = None
    elif location == "경남":
        location = "LCJ000"
    elif location == "경북":
        location = "LCK000"
    elif location == "광주":
        location = "LCQ000"
    elif location == "대구":
        location = "LCR000"
    elif location == "대전":
        location = "LCS000"
    elif location == "부산":
        location = "LCT000"
    elif location == "서울":
        location = "LCA000"
    elif location == "세종":
        location = "LCW000"
    elif location == "울산":
        location = "LCU000"
    elif location == "인천":
        location = "LCV000"
    elif location == "전남":
        location = "LCL000"
    elif location == "전북":
        location = "LCM000"
    elif location == "제주":
        location = "LCP000"
    elif location == "충남":
        location = "LCN000"
    elif location == "충북":
        location = "LCO000"

    previous_filters = {
        "category": category,
        "start_date": start_date,
        "end_date": end_date,
        "location": location
    }

    params = {
        "serviceKey": service_key,
        "pageNo": "1",
        "numOfRows": "100",
        "PRDT_CL_CD_01": category,
        "START_YMD": start_date,
        "END_YMD": end_date,
        "N_FD_LCT_CD": location
    }
    response = requests.get(endpoint, params=params)
    root = ET.fromstring(response.content)

    # 결과 파싱 및 출력
    result_listbox.delete(0, tk.END)
    items = root.findall("body/items/item")
    for item in items:
        atcId = item.findtext("atcId")
        depPlace = item.findtext("depPlace")
        fdFilePathImg = item.findtext("fdFilePathImg")
        fdPrdtNm = item.findtext("fdPrdtNm")
        fdSbjt = item.findtext("fdSbjt")
        fdSn = item.findtext("fdSn")
        fdYmd = item.findtext("fdYmd")
        prdtClNm = item.findtext("prdtClNm")
        rnum = item.findtext("rnum")
        result_listbox.insert(tk.END,
                              f"관리ID: {atcId}, 보관장소: {depPlace}, 이미지: {fdFilePathImg}, 물품명: {fdPrdtNm}, 게시제목: {fdSbjt}, 습득순번: {fdSn}, 습득일자: {fdYmd}, 물품분류명: {prdtClNm}, 일련번호: {rnum}\n")

def open_email_window():
    email_window = tk.Toplevel(window)
    email_window.title("이메일 보내기")

    email_label = tk.Label(email_window, text="받는 사람 이메일:")
    email_label.grid(row=0, column=0, padx=10, pady=10)

    email_entry = tk.Entry(email_window)
    email_entry.grid(row=0, column=1, padx=10, pady=10)

    send_button = tk.Button(email_window, text="확인", command=lambda: send_email(email_entry.get()))
    send_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)


# 이메일 보내기 함수
def send_email(to_email):
    if not to_email:
        msgbox.showerror("오류", "이메일을 입력하세요.")
        return

        # 이메일 설정
    from_email = "cys90115@gmail.com"  # 보내는 이메일 주소
    password = "rbpq keuf gnes xrme"  # 앱 비밀 번호

    # 이메일 메시지 설정
    subject = "분실물 조회 서비스 결과"

    # Listbox에서 항목을 가져와 이메일 본문 구성
    body = "\n".join(result_listbox.get(0, tk.END))

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    # SMTP 세션 설정 및 이메일 보내기
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        text = message.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        msgbox.showinfo("성공", "이메일이 성공적으로 전송되었습니다.")
    except smtplib.SMTPException as e:
        msgbox.showerror("오류", f"이메일을 보내는 중 오류가 발생했습니다: {e}")

def open_telegram():
    # 텔레그램 실행 파일의 경로를 설정합니다.
    telegram_path = r"C:\Program Files\Telegram Desktop\Telegram.exe"

    if os.path.exists(telegram_path):
        try:
            subprocess.Popen([telegram_path])
        except Exception as e:
            msgbox.showerror("오류", f"텔레그램을 여는 중 오류가 발생했습니다: {e}")
    else:
        msgbox.showerror("오류", "텔레그램 실행 파일을 찾을 수 없습니다. 경로를 확인하세요.")

telegram_button = tk.Button(window, image=telegram_image, width=50, command=open_telegram)
telegram_button.grid(row=0, column=6, padx=10, pady=10)


def search_lost_items(category, start_date, end_date, location, chat_id=None):
    url = f"{endpoint}?serviceKey={service_key}&START_YMD={start_date}&END_YMD={end_date}&N_FD_LCT_CD={location}&N_FD_LCT_CD={category}"
    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        results = []
        for item in items:
            fdSbjt = item.findtext("fdSbjt")
            fdPrdtNm = item.findtext("fdPrdtNm")
            fdYmd = item.findtext("fdYmd")
            depPlace = item.findtext("depPlace")
            tel = item.findtext("tel")
            results.append(f"물품명: {fdPrdtNm}, 발견일자: {fdYmd}, 발견장소: {depPlace}, 전화번호: {tel}")

        if chat_id:
            if results:
                for result in results:
                    bot.sendMessage(chat_id, result)
            else:
                bot.sendMessage(chat_id, "해당 조건에 맞는 분실물이 없습니다.")
        else:
            result_listbox.delete(0, tk.END)
            for result in results:
                result_listbox.insert(tk.END, result)
    else:
        if chat_id:
            bot.sendMessage(chat_id, "분실물 조회 중 오류가 발생했습니다.")
        else:
            result_listbox.insert(tk.END, "분실물 조회 중 오류가 발생했습니다.")

def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    if command == '/start':
        welcome_message = (
            "분실물 조회 서비스에 오신 것을 환영합니다.\n"
            "다음 명령어를 사용할 수 있습니다:\n"
            "/search <카테고리> <시작일> <종료일> <지역>\n\n"
            "예시: /search PRA000 20240501 20240531 LCA000\n\n"
            "사용 가능한 카테고리:\n"
            "PRA000 - 가방\n"
            "PRB000 - 도서용품\n"
            "PRC000 - 서류\n"
            "PRD000 - 산업용품\n"
            "PRE000 - 스포츠용품\n"
            "PRF000 - 자동차\n"
            "PRG000 - 전자기기\n"
            "PRH000 - 지갑\n"
            "PRI000 - 컴퓨터\n"
            "PRJ000 - 휴대폰\n"
            "PRK000 - 의류\n"
            "PRL000 - 현금\n"
            "PRM000 - 유가증권\n"
            "PRN000 - 증명서\n"
            "PRO000 - 귀금속\n"
            "PRP000 - 카드\n"
            "PRQ000 - 쇼핑백\n"
            "PRR000 - 악기\n"
            "PRX000 - 유류품\n"
            "PRY000 - 무주물\n"
            "PRZ000 - 기타\n\n"
            "사용 가능한 지역:\n"
            "LCA000 - 서울\n"
            "LCB000 - 부산\n"
            "LCC000 - 대구\n"
            "LCD000 - 인천\n"
            "LCE000 - 광주\n"
            "LCF000 - 대전\n"
            "LCG000 - 울산\n"
            "LCH000 - 세종\n"
            "LCI000 - 경기\n"
            "LCJ000 - 강원\n"
            "LCK000 - 충북\n"
            "LCL000 - 충남\n"
            "LCM000 - 전북\n"
            "LCN000 - 전남\n"
            "LCO000 - 경북\n"
            "LCP000 - 경남\n"
            "LCQ000 - 제주\n"
        )
        bot.sendMessage(chat_id, welcome_message)
    elif command.startswith('/search'):
        params = command.split()
        if len(params) != 5:
            bot.sendMessage(chat_id, "잘못된 형식입니다. /search <카테고리> <시작일> <종료일> <지역> 형식으로 입력하세요.")
        else:
            category, start_date, end_date, location = params[1], params[2], params[3], params[4]
            search_lost_items(category, start_date, end_date, location, chat_id)
    else:
        bot.sendMessage(chat_id, "알 수 없는 명령어입니다.")

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)

def run_telegram_bot():
    while True:
        time.sleep(10)

telegram_thread = threading.Thread(target=run_telegram_bot)
telegram_thread.daemon = True
telegram_thread.start()

# Define a function to save content to a file
def save_content_to_file():
    filename = "service.txt"
    content = "\n".join(result_listbox.get(0, tk.END))
    spam.save_to_file(filename, content)
    print("Content saved to file:", filename)

# Create the Save button
save_button = tk.Button(window, text="저장", width=10, height=2, command=save_content_to_file)
save_button.grid(row=9, column=5, columnspan=2, padx=10, pady=20)


search_button.config(command=search)

window.mainloop()