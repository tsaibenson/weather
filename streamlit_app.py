import streamlit as st
import requests
import base64
import sqlite3
import random

url = 'https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-C0032-001?Authorization=CWA-FFA499CF-64DE-47AD-9E7C-7CC3B32ABD4F&downloadType=WEB&format=JSON'

def fetch_weather_data():
    try:
        data = requests.get(url)
        data.raise_for_status()
        return data.json()
    except requests.RequestException as e:
        st.error(f"Error fetching weather data: {e}")
        return None

def create_weather_table():
    conn = sqlite3.connect('weather_database.db')
    cursor = conn.cursor()
    cursor.execute('''DROP TABLE IF EXISTS weather''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            weather_condition TEXT,
            max_temperature REAL,
            min_temperature REAL,
            comfort TEXT,
            rain_probability INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def insert_weather_data(city, weather_condition, max_temperature, min_temperature, comfort, rain_probability):
    conn = sqlite3.connect('weather_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO weather (city, weather_condition, max_temperature, min_temperature, comfort, rain_probability)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (city, weather_condition, max_temperature, min_temperature, comfort, rain_probability))
    conn.commit()
    conn.close()

def populate_weather_data():
    data_json = fetch_weather_data()
    if data_json:
        location = data_json['cwaopendata']['dataset']['location']
        for i in location:
            city = i['locationName']
            wth = i['weatherElement'][0]['time'][0]['parameter']['parameterName']
            max_tem = i['weatherElement'][1]['time'][0]['parameter']['parameterName']
            min_tem = i['weatherElement'][2]['time'][0]['parameter']['parameterName']
            com = i['weatherElement'][3]['time'][0]['parameter']['parameterName']
            rain = i['weatherElement'][4]['time'][0]['parameter']['parameterName']
            insert_weather_data(city, wth, float(max_tem), float(min_tem), com, int(rain))

def display_city_weather(city):
    conn = sqlite3.connect('weather_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM weather WHERE city = ?', (city,))
    result = cursor.fetchone()
    conn.close()
    if result:
        st.header(f"{city}")
        st.subheader(f"天氣現象 : {result[2]}")
        st.subheader(f"最高溫度 : {result[3]} °C")
        st.subheader(f"最低溫度 : {result[4]} °C")
        st.subheader(f"舒適度 : {result[5]}")
        st.subheader(f"降雨機率 : {result[6]}%")
        if int(result[6]) > 65:
           st.subheader(":red[很有可能會下雨，出門記得帶把傘喔!!]")
        elif int(result[3]) > 27:
             st.subheader(":red[太陽很大，外出要記得防曬，小心中暑!!]")
        elif int(result[4]) < 16:
             st.subheader(":red[外頭有點冷，記得多穿一點再出門，以免感冒!!]")

def main_bg(main_bg):
    main_bg_ext = "png"
    st.markdown(
         f"""
          <style>
          .stApp {{
              background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
              background-size: orignal;
         }}
         </style>
         """,
         unsafe_allow_html=True
    )


# 創建和填充數據庫
create_weather_table()
populate_weather_data()

st.sidebar.title(":rainbow[好天氣好心情]")
st.sidebar.divider()
st.sidebar.header("功能選項")
main_page = st.sidebar.button("主頁")
page1 = st.sidebar.button("以城市搜尋")
page2 = st.sidebar.button("以溫度推薦城市")
page3 = st.sidebar.button("以降雨機率推薦城市")
page4 = st.sidebar.button("今天要去哪")
st.sidebar.image('map.jpg')

# 使用 session state 來跟踪當前頁面
if 'current_page' not in st.session_state:
    st.session_state.current_page = "主頁"
if main_page:
    st.session_state.current_page = "主頁"
elif page1:
    st.session_state.current_page = "以城市搜尋"
elif page2:
    st.session_state.current_page = "以溫度推薦城市"
elif page3:
    st.session_state.current_page = "以降雨機率推薦城市"
elif page4:
    st.session_state.current_page = "隨機顯示城市天氣"

#背景圖片



if st.session_state.current_page == "主頁":
    st.header("歡迎來到好天氣好心情網站")
    st.write("這是一個天氣預報應用網站，你可以在這裡找到各種天氣相關的資訊 !!")
    st.write(":red[利用左側欄的功能選項來進行查詢 !]")
    st.image('sea.jpg')

if st.session_state.current_page == "以城市搜尋":
    st.title(":green[_搜尋城市天氣_]")
    st.header("",divider='rainbow')
    city = st.selectbox("城市名稱", ["基隆市", "臺北市", "新北市", "桃園市", "新竹縣", "新竹市", "苗栗縣", "臺中市", "南投縣", "彰化縣", "雲林縣", "嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣", "臺東縣", "花蓮縣", "宜蘭縣", "澎湖縣", "金門縣", "連江縣"])
    if st.button("搜尋"):
        display_city_weather(city)

elif st.session_state.current_page == "以溫度推薦城市":
    st.title(":orange[_溫度推薦城市_]")
    st.header("",divider='rainbow')
    min_temp = st.number_input("最低溫度", step=0.1)
    max_temp = st.number_input("最高溫度", step=0.1)
    if st.button("搜尋"):
        conn = sqlite3.connect('weather_database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT city, max_temperature, min_temperature FROM weather 
            WHERE max_temperature <= ? AND min_temperature >= ?
        ''', (max_temp, min_temp))
        results = cursor.fetchall()
        conn.close()
        if results:
            st.write(f"(溫度介於 {min_temp}°C &#126; {max_temp}°C)")
            for result in results:
                st.subheader(f"{result[0]} :  {result[2]} °C  &#126;  {result[1]} °C")
        else:
            st.error("找不到符合條件的城市。")

elif st.session_state.current_page == "以降雨機率推薦城市":
    st.title(":blue[_降雨機率推薦城市_]")
    st.header("",divider='rainbow')
    rain_prob = st.number_input("降雨機率 (%)", step=1)
    condition = st.selectbox("條件", ["大於", "小於"])
    if st.button("搜尋"):
        conn = sqlite3.connect('weather_database.db')
        cursor = conn.cursor()
        if condition == "大於":
            cursor.execute('SELECT city, rain_probability FROM weather WHERE rain_probability >= ?', (rain_prob,))
        else:
            cursor.execute('SELECT city, rain_probability FROM weather WHERE rain_probability <= ?', (rain_prob,))
        results = cursor.fetchall()
        conn.close()
        if results:
            st.write(f"(降雨機率 {condition} {rain_prob}%)")
            for result in results:
                st.subheader(f"{result[0]} : {result[1]}%")
        else:
            st.error("找不到符合條件的城市。")
            
elif st.session_state.current_page == "隨機顯示城市天氣":
    st.title(":violet[_今天要去哪兒_]")
    st.header("",divider='rainbow')
    conn = sqlite3.connect('weather_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT city FROM weather')
    cities = cursor.fetchall()
    conn.close()
    if cities:
        random_city = random.choice(cities)[0]
        display_city_weather(random_city)



