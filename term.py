import tkinter as tk
import tkinter.ttk as ttk
import requests
from PIL import Image, ImageTk
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
map_button = tk.Button(window, text="지도", width=10)
map_button.grid(row=0, column=4, padx=10, pady=10)

mail_button = tk.Button(window, text="메일", width=10)
mail_button.grid(row=0, column=5, padx=10, pady=10)

# 검색 버튼
search_button = tk.Button(window, text="검색", width=20, height=2)
search_button.grid(row=9, column=0, columnspan=6, padx=10, pady=20)

# URL 입력 창과 이미지 표시 공간
url_label = tk.Label(window, text="이미지 URL")
url_label.grid(row=1, column=4, padx=10, pady=5)

url_entry = tk.Entry(window, width=30)
url_entry.grid(row=1, column=5, padx=10, pady=5)

image_label = tk.Label(window)
image_label.grid(row=2, column=4, columnspan=2, padx=10, pady=10)

# 물품분류 카테고리
category_label = tk.Label(window, text="물품분류")
category_label.grid(row=3, column=0, padx=10, pady=10)

category_combobox = ttk.Combobox(window)
category_combobox['values'] = ("가방","도서용품", "서류","산업용품","스포츠용품","자동차","전자기기","지갑","컴퓨터","휴대폰","의류","현금","유가증권","증명서","귀금속","카드","쇼핑백","악기","유류품","무주물","기타")
category_combobox.grid(row=3, column=1, columnspan=3, padx=10, pady=10)

# 습득일자 시작일 카테고리
start_date_label = tk.Label(window, text="습득일자(시작일) ex)20240525")
start_date_label.grid(row=5, column=0, padx=10, pady=10)

start_date_entry = tk.Entry(window)
start_date_entry.grid(row=5, column=1, columnspan=3, padx=10, pady=10)

# 습득일자 종료일 카테고리
end_date_label = tk.Label(window, text="습득일자(종료일) ex)20240526")
end_date_label.grid(row=6, column=0, padx=10, pady=10)

end_date_entry = tk.Entry(window)
end_date_entry.grid(row=6, column=1, columnspan=3, padx=10, pady=10)

# 습득지역 카테고리
location_label = tk.Label(window, text="습득지역")
location_label.grid(row=7, column=0, padx=10, pady=10)

location_combobox = ttk.Combobox(window)
location_combobox['values'] = ("강원","경기","경남","경북","광주","대구","대전","부산","서울","세종","울산","인천","전남","전북","제주","충남","충북")
location_combobox.grid(row=7, column=1, columnspan=3, padx=10, pady=10)

# 결과 출력창
result_text = tk.Text(window, height=10)
result_text.grid(row=8, column=0, columnspan=6, padx=10, pady=10)


def show_image():
    pass


# 검색 함수
def search():
    pass


window.mainloop()
