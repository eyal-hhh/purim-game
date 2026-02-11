import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
from datetime import datetime, timedelta

# הגדרות עמוד
st.set_page_config(page_title="הגמד והענק 2026", layout="centered", page_icon="🎭")

# עיצוב RTL והתאמה למובייל
st.markdown("""
    <style>
    .main { direction: rtl; }
    h1, h2, h3, p, div { text-align: right; direction: rtl; }
    div.stButton > button, div.stForm submit_button > button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background-color: #FF4B4B; color: white; font-weight: bold; font-size: 18px;
    }
    .welcome-msg { 
        background-color: #f8f9fa; padding: 15px; border-radius: 15px; 
        border-right: 8px solid #FF4B4B; margin-bottom: 20px; color: #202124;
    }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_israel_time():
    return (datetime.utcnow() + timedelta(hours=2)).strftime("%d/%m/%Y %H:%M:%S")

def perform_lottery(df):
    df = df.dropna(subset=['Name', 'ID']).copy()
    names = df['Name'].tolist()
    shuffled = names.copy()
    attempts = 0
    while any(names[i] == shuffled[i] for i in range(len(names))) and attempts < 100:
        random.shuffle(shuffled)
        attempts += 1
    df['Target'] = shuffled
    df['Try'] = 0
    df['Timestamp'] = ""
    return df

def load_and_clean_data():
    """טעינה וניקוי נתונים כדי למנוע שגיאות סוגי נתונים"""
    try:
        df = conn.read(ttl=0)
        # המרה לטקסט וניקוי רווחים/נקודות עשרוניות
        for col in ['ID', 'Try', 'Name', 'Target', 'Timestamp']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('.0', '', regex=False).str.strip().replace('nan', '')
        return df
    except Exception as e:
        st.error(f"שגיאה בגישה לנתונים: {e}")
        return None

menu = st.sidebar.selectbox("ניווט:", ["כניסת עובדים", "ניהול (HR)"])

# --- מסך ניהול ---
if menu == "ניהול (HR)":
    st.markdown("<h1 style='text-align: center;'>ניהול משאבי אנוש 🎭</h1>", unsafe_allow_html=True)
    if 'admin_logged_in' not in st.session_state: st.session_state['admin_logged_in'] = False

    if not st.session_state['admin_logged_in']:
        with st.form("admin_login"):
            pw = st.text_input("סיסמת מנהלת:")
            if st.form_submit_button("כניסה"):
                if pw == "פורים2026":
                    st.session_state['admin_logged_in'] = True
                    st.rerun()
                else: st.error("סיסמה שגויה")
    else:
        data = load_and_clean_data()
        if data is not None:
            if st.button("🎰 הפעל הגרלה"):
                df_results = perform_lottery(data)
                conn.update(data=df_results)
                st.success("ההגרלה הסתיימה!")
                st.rerun()
            
            st.write("### 📊 דוח מעקב")
            st.dataframe(data[['Name', 'Try', 'Timestamp', 'Target']].rename(
                columns={'Name': 'שם', 'Try': 'צפיות', 'Timestamp': 'זמן', 'Target': 'גמד'}), 
                use_container_width=True)

# --- מסך עובדים ---
elif menu == "כניסת עובדים":
    st.markdown("<h1 style='text-align: center;'>🎈 פורים 2026: מי הגמד שלי?</h1>", unsafe_allow_html=True)
    
    if 'logged_in_user_id' not in st.session_state:
        with st.form("login_form"):
            emp_id_input = st.text_input("הזינו מספר עובד:")
            if st.form_submit_button("כניסה"):
                data = load_and_clean_data()
                if data is not None:
                    # חיפוש חכם שמתעלם מפורמט המספר
                    input_clean = str(emp_id_input).strip()
                    user_match = data[data['ID'] == input_clean]
                    
                    if not user_match.empty:
                        st.session_state['logged_in_user_id'] = input_clean
                        st.session_state['logged_in_name'] = user_match.iloc[0]['Name']
                        st.rerun()
                    else: st.error("מספר עובד לא נמצא.")
    else:
        data = load_and_clean_data()
        if data is not None:
            user_idx = data[data['ID'] == st.session_state['logged_in_user_id']].index[0]
            user_data = data.loc[user_idx]
            
            st.markdown(f'<div class="welcome-msg"><h3>שלום, {st.session_state["logged_in_name"]}! 👋</h3></div>', unsafe_allow_html=True)

            # בדיקת ניסיונות - המרה בטוחה למספר
            try_val = user_data.get('Try', '0')
            try_val = int(float(try_val)) if try_val != '' else 0
            
            if try_val > 0:
                st.warning("המערכת מזהה שכבר הגרלת גמד בעבר.")
                st.info(f"בוצע בתאריך: {user_data.get('Timestamp', 'לא ידוע')}")
                st.error("מטעמי אבטחה, לא ניתן לצפות בשם שוב.")
                st.markdown("---")
                st.markdown("### 📞 שכחת מי הגמד? פנה/י למשאבי אנוש.")
            else:
                if st.button("🎡 הפעל רולטה!"):
                    target_name = user_data['Target']
                    now = get_israel_time()
                    
                    data.at[user_idx, 'Try'] = "1"
                    data.at[user_idx, 'Timestamp'] = now
                    conn.update(data=data)
                    
                    placeholder = st.empty()
                    names = data['Name'].tolist()
                    for _ in range(12):
                        placeholder.markdown(f"<h2 style='text-align: center; color: gray;'>{random.choice(names)}</h2>", unsafe_allow_html=True)
                        time.sleep(0.08)
                    
                    placeholder.markdown(f"<h1 style='text-align: center; color: #00CC00; font-size: 40px;'>✨ {target_name} ✨</h1>", unsafe_allow_html=True)
                    st.balloons()
                    st.success(f"חג שמח! הגמד שלך הוא/היא: {target_name}")

    if 'logged_in_user_id' in st.session_state:
        if st.sidebar.button("יציאת עובד"):
            del st.session_state['logged_in_user_id']
            del st.session_state['logged_in_name']
            st.rerun()
