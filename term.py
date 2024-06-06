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

# API 엔드포인트 URL
endpoint = "http://apis.data.go.kr/1320000/LosfundInfoInqireService/getLosfundInfoAccToClAreaPd"
# 서비스키
service_key = "nzC0XJi2SwXBHZ85MgwpTlycTYqYelKfi94f+R1oVUMrCEYSZ7ociwxUPUZ8PzC0y63zFmme0KtVHKTwEy+FrQ=="
# Google Maps API 키
google_maps_api_key = 'AIzaSyCzFgc9OGnXckq1-JNhSCVGo9zIq1kSWcE'

# GUI 생성
window = tk.Tk()
window.title("분실물 조회 서비스")

# program name
program_name_label = tk.Label(window, text="분실물 조회 서비스", font=("Helvetica", 24))
program_name_label.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

# map/mail
map_button = tk.Button(window, text="지도", width=10, command=lambda: open_map())
map_button.grid(row=0, column=4, padx=10, pady=10)

mail_button = tk.Button(window, text="메일", width=10, command=lambda: open_email_window())
mail_button.grid(row=0, column=5, padx=10, pady=10)

# image url
url_entry = tk.Entry(window, width=30)
url_entry.grid(row=1, column=4, padx=10, pady=5)

image_label = tk.Label(window)
image_label.grid(row=2, column=4, columnspan=2, padx=10, pady=10)

# image load button
load_image_button = tk.Button(window, text="이미지 로드", width=20, height=2, command=lambda: show_image())
load_image_button.grid(row=1, column=5, padx=10, pady=5)

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


def show_image():
    url = url_entry.get()
    try:
        response = requests.get(url)
        response.raise_for_status()
        image_data = response.content
        image = Image.open(io.BytesIO(image_data))

        max_width = 400
        max_height = 400
        image.thumbnail((max_width, max_height), Image.LANCZOS)

        photo = ImageTk.PhotoImage(image)

        # 새로운 창 생성
        new_window = tk.Toplevel(window)
        new_window.title("이미지 보기")

        new_image_label = tk.Label(new_window, image=photo)
        new_image_label.image = photo
        new_image_label.pack(padx=10, pady=10)
    except requests.exceptions.RequestException as e:
        result_listbox.insert(tk.END, f"이미지 요청 오류: {e}\n")
    except IOError as e:
        result_listbox.insert(tk.END, f"이미지 처리 오류: {e}\n")
    except Exception as e:
        result_listbox.insert(tk.END, f"예기치 않은 오류가 발생했습니다: {e}\n")


url_entry.bind("<Return>", lambda event: show_image())


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


search_button.config(command=search)

window.mainloop()