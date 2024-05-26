import tkinter as tk
import tkinter.ttk as ttk
import requests
import webbrowser
from PIL import Image, ImageTk
import tkinter.messagebox as msgbox
import io
import xml.etree.ElementTree as ET

# API 엔드포인트 URL
endpoint = "http://apis.data.go.kr/1320000/LosfundInfoInqireService/getLosfundInfoAccToClAreaPd"
# 서비스키
service_key = "nzC0XJi2SwXBHZ85MgwpTlycTYqYelKfi94f+R1oVUMrCEYSZ7ociwxUPUZ8PzC0y63zFmme0KtVHKTwEy+FrQ=="

# GUI 생성
window = tk.Tk()
window.title("분실물 조회 서비스")

# 상단 프로그램명
program_name_label = tk.Label(window, text="분실물 조회 서비스", font=("Helvetica", 24))
program_name_label.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

# 우측 상단 버튼 (지도 및 메일)
map_button = tk.Button(window, text="지도", width=10, command=lambda: open_map())
map_button.grid(row=0, column=4, padx=10, pady=10)

mail_button = tk.Button(window, text="메일", width=10)
mail_button.grid(row=0, column=5, padx=10, pady=10)

# 이미지 URL 입력 및 표시
url_entry = tk.Entry(window, width=30)
url_entry.grid(row=1, column=4, padx=10, pady=5)

image_label = tk.Label(window)
image_label.grid(row=2, column=4, columnspan=2, padx=10, pady=10)

# 이미지 로드 버튼
load_image_button = tk.Button(window, text="이미지 로드", width=20, height=2, command=lambda: show_image())
load_image_button.grid(row=1, column=5, padx=10, pady=5)

# 물품분류 카테고리
category_label = tk.Label(window, text="물품분류")
category_label.grid(row=3, column=0, padx=10, pady=10)

category_combobox = ttk.Combobox(window)
category_combobox['values'] = (
    "가방", "도서용품", "서류", "산업용품", "스포츠용품", "자동차", "전자기기", "지갑", "컴퓨터",
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
    "강원", "경기", "경남", "경북", "광주", "대구", "대전", "부산", "서울", "세종", "울산", "인천", "전남", "전북", "제주", "충남", "충북")
location_combobox.grid(row=7, column=1, columnspan=3, padx=10, pady=10)

# 결과 출력창
result_text = tk.Text(window, height=10)
result_text.grid(row=8, column=0, columnspan=6, padx=10, pady=10)

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
        result_text.insert(tk.END, f"이미지 요청 오류: {e}\n")
    except IOError as e:
        result_text.insert(tk.END, f"이미지 처리 오류: {e}\n")
    except Exception as e:
        result_text.insert(tk.END, f"예기치 않은 오류가 발생했습니다: {e}\n")


# URL 입력 창의 엔터키 이벤트와 함수 연결
url_entry.bind("<Return>", lambda event: show_image())


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
        search_query = f"{location_map[location]} 경찰서 OR 지구대 OR 파출소"
        url = f"https://www.google.com/maps/search/{search_query}"
        webbrowser.open(url)
    else:
        result_text.insert(tk.END, "올바른 지역을 선택해 주세요.\n")


# 갱신 버튼 함수
def refresh():
    global previous_filters  # 전역 변수로 사용

    # 이전 필터들을 사용하여 검색 수행
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
    result_text.delete("1.0", tk.END)
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
        result_text.insert(tk.END,
                           f"관리ID: {atcId}, 보관장소: {depPlace}, 이미지: {fdFilePathImg}, 물품명: {fdPrdtNm}, 게시제목: {fdSbjt}, 습득순번: {fdSn}, 습득일자: {fdYmd}, 물품분류명: {prdtClNm}, 일련번호: {rnum}\n")
    # 갱신 완료 메시지 창 표시
    msgbox.showinfo("갱신 완료", "검색 결과가 갱신되었습니다.")


# 이전에 선택된 필터들을 저장할 변수
previous_filters = {
    "category": None,
    "start_date": None,
    "end_date": None,
    "location": None
}

# 갱신 버튼에 갱신 함수 연결
refresh_button = tk.Button(window, text="갱신", width=10, height=2, command=refresh)
refresh_button.grid(row=9, column=7, columnspan=2, padx=10, pady=20)


# 검색 함수
def search():
    global previous_filters
    category = category_combobox.get()
    if category == "가방":
        category = "PRA000"
    elif category == "도서용품":
        category = "PRB000"
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

    previous_filters = {  # 이전 필터들 업데이트
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
    result_text.delete("1.0", tk.END)
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
        result_text.insert(tk.END,
                           f"관리ID: {atcId}, 보관장소: {depPlace}, 이미지: {fdFilePathImg}, 물품명: {fdPrdtNm}, 게시제목: {fdSbjt}, 습득순번: {fdSn}, 습득일자: {fdYmd}, 물품분류명: {prdtClNm}, 일련번호: {rnum}\n")


# 검색 버튼에 검색 함수 연결
search_button.config(command=search)

window.mainloop()
