import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

st.set_page_config(page_title="הגמד והענק - פורים 2026", layout="centered", page_icon="🎭")

# חיבור לנתונים
conn = st.connection("gsheets", type=GSheetsConnection)

def perform_lottery(df):
    """מבצע הגרלה: עובד (ענק) מקבל גמד"""
    df = df.dropna(subset=['Name', 'ID']).copy()
    names = df['Name'].tolist()
    shuffled = names.copy()
    
    attempts = 0
    while any(names[i] == shuffled[i] for i in range(len(names))) and attempts < 100:
        random.shuffle(shuffled)
        attempts += 1
        
    df['Target'] = shuffled # עמודת ה-Target היא למעשה ה'גמד'
    return df

menu = st.sidebar.selectbox("תפריט ניווט", ["כניסת עובדים", "ניהול (HR)"])

# --- חלק הניהול ---
if menu == "ניהול (HR)":
    st.title("ניהול משאבי אנוש 🎭")
    admin_pw = st.text_input("הזיני סיסמת מנהלת", type="password")
    
    if admin_pw == "פורים2026":
        if st.button("🎰 בצע הגרלה כללית"):
            try:
                df = conn.read(ttl=0)
                df_results = perform_lottery(df)
                conn.update(data=df_results)
                st.success("ההגרלה הסתיימה! הגמדים שובצו לענקים.")
            except Exception as e:
                st.error(f"שגיאה בניהול: {e}")

# --- חלק העובדים ---
elif menu == "כניסת עובדים":
    st.title("🎈 פורים 2026: מי הגמד שלי?")
    
    try:
        data = conn.read(ttl=0)
        # ניקוי פורמט ID (מספרים/טקסט)
        data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
        
        if 'Target' not in data.columns or data['Target'].isnull().all():
            st.warning("ההגרלה טרם בוצעה על ידי משאבי אנוש.")
        else:
            names_list = sorted(data['Name'].dropna().unique().tolist())
            selected_user = st.selectbox("בחר/י את שמך (את/ה הענק):", [""] + names_list)
            
            if selected_user:
                emp_id = st.text_input("הזינו מספר עובד לזיהוי:", type="password")
                
                if st.button("🎡 הפעל רולטה: מי הגמד שלי?"):
                    user_row = data[data['Name'] == selected_user].iloc[0]
                    
                    if str(emp_id).strip() == str(user_row['ID']):
                        target_name = user_row['Target']
                        
                        # --- אפקט הרולטה ---
                        st.write("---")
                        placeholder = st.empty() # יצירת מקום דינמי לשמות
                        all_names = data['Name'].tolist()
                        
                        # שלב 1: ריצה מהירה
                        for _ in range(20):
                            placeholder.markdown(f"<h2 style='text-align: center; color: gray;'>{random.choice(all_names)}</h2>", unsafe_allow_html=True)
                            time.sleep(0.05)
                        
                        # שלב 2: האטה
                        for i in range(1, 10):
                            placeholder.markdown(f"<h2 style='text-align: center; color: #FF4B4B;'>{random.choice(all_names)}</h2>", unsafe_allow_html=True)
                            time.sleep(0.1 * i)
                        
                        # שלב 3: עצירה על השם הנכון
                        placeholder.markdown(f"<h1 style='text-align: center; color: #00CC00; font-size: 50px;'>✨ {target_name} ✨</h1>", unsafe_allow_html=True)
                        st.balloons()
                        st.success(f"חג שמח! הגמד שלך הוא/היא: **{target_name}**")
                        st.info("אל תשכחו להכין משלוח מנות מפנק! 🍬")
                    else:
                        st.error("מספר עובד לא תקין. נסו שוב.")
                        
    except Exception as e:
        st.error(f"שגיאה בטעינת נתונים: {e}")
