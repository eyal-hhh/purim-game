import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
from datetime import datetime, timedelta

# הגדרות עמוד
st.set_page_config(page_title="הגמד והענק 2026", layout="centered", page_icon="🎭")

# עיצוב CSS מותאם אישית למובייל ותיקון יישור טבלאות
st.markdown("""
    <style>
    .main { direction: rtl; }
    h1, h2, h3, p, div, span { text-align: right; direction: rtl; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stSidebar"] { display: none; }
    
    /* כפתורים גדולים למובייל */
    div.stButton > button, div.stForm submit_button > button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background-color: #FF4B4B; color: white; font-weight: bold; font-size: 18px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1); border: none;
    }
    
    /* תיקון נראות טבלה במובייל */
    .stDataFrame { direction: rtl; }
    [data-testid="stDataFrame"] td { text-align: right !important; color: #000000 !important; }
    
    .welcome-msg { 
        background-color: #f1f3f4; padding: 20px; border-radius: 15px; 
        border-right: 8px solid #FF4B4B; margin-bottom: 20px; color: #202124;
    }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_israel_time():
    return (datetime.utcnow() + timedelta(hours=2)).strftime("%d/%m/%Y %H:%M:%S")

def load_and_clean_data():
    try:
        df = conn.read(ttl=0)
        for col in ['Name', 'ID', 'Target', 'Try', 'Timestamp']:
            if col not in df.columns: df[col] = ""
        df = df.fillna("")
        for col in df.columns:
            df[col] = df[col].astype(str).str.replace('.0', '', regex=False).str.strip().replace('nan', '')
        return df
    except Exception as e:
        st.error(f"שגיאה בחיבור: {e}")
        return None

def play_roulette_sound():
    sound_url = "https://www.soundjay.com/misc/sounds/magic-chime-01.mp3"
    st.components.v1.html(f'<audio autoplay><source src="{sound_url}" type="audio/mp3"></audio>', height=0)

# ניווט עליון
menu = st.radio("", ["כניסת עובדים", "ניהול (HR)"], horizontal=True, label_visibility="collapsed")
st.write("---")

# --- מסך ניהול ---
if menu == "ניהול (HR)":
    st.markdown("<h2 style='text-align: center;'>ניהול משאבי אנוש 🎭</h2>", unsafe_allow_html=True)
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
            with st.expander("⚠️ אזור רגיש - ביצוע הגרלה"):
                st.warning("שים/י לב: פעולה זו תמחק את כל ההגרלה הקיימת!")
                confirm_pw = st.text_input("הקלידי שוב סיסמה לאישור:", type="password")
                if confirm_pw == "פורים2026":
                    if st.button("🔥 הפעל הגרלה חדשה"):
                        df_copy = data.dropna(subset=['Name', 'ID']).copy()
                        names = df_copy['Name'].tolist()
                        shuffled = names.copy()
                        random.shuffle(shuffled)
                        while any(names[i] == shuffled[i] for i in range(len(names))): random.shuffle(shuffled)
                        df_copy['Target'] = shuffled
                        df_copy['Try'] = "0"
                        df_copy['Timestamp'] = ""
                        conn.update(data=df_copy)
                        st.success("הגרלה בוצעה!")
                        st.rerun()

            st.write("---")
            col1, col2 = st.columns(2)
            with col1:
                csv = data.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 הורדת CSV", data=csv, file_name="purim_report.csv")
            with col2:
                if st.button("🚪 יציאה"):
                    st.session_state['admin_logged_in'] = False
                    st.rerun()
            
            st.write("### 📊 דוח מעקב")
            # שינוי סדר העמודות: שם -> זמן -> צפיות -> גמד
            display_df = data[['Name', 'Timestamp', 'Try', 'Target']].copy()
            display_df['Timestamp'] = display_df['Timestamp'].replace('', 'טרם')
            
            st.dataframe(
                display_df.rename(columns={'Name': 'שם', 'Timestamp': 'זמן הגרלה', 'Try': 'צפיות', 'Target': 'גמד'}),
                column_config={
                    "זמן הגרלה": st.column_config.TextColumn("זמן הגרלה", width="medium"),
                    "שם": st.column_config.TextColumn("שם", width="small"),
                },
                use_container_width=True,
                hide_index=True
            )

# --- מסך עובדים ---
else:
    st.markdown("<h1 style='text-align: center;'>🎈 פורים 2026: מי הגמד שלי?</h1>", unsafe_allow_html=True)
    if 'logged_in_user_id' not in st.session_state:
        with st.form("login_form"):
            emp_id_input = st.text_input("הזינו מספר עובד:")
            if st.form_submit_button("כניסה למערכת"):
                data = load_and_clean_data()
                if data is not None:
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

            try_val = int(float(user_data.get('Try', '0')))
            if try_val > 0:
                st.warning("המערכת מזהה שכבר הגרלת גמד בעבר.")
                st.info(f"בוצע בתאריך: {user_data.get('Timestamp', 'לא ידוע')}")
                st.error("מטעמי אבטחה, לא ניתן לצפות בשם שוב.")
                st.markdown("### 📞 שכחת מי הגמד? פנה למשאבי אנוש.")
            else:
                if st.button("🎡 הפעל רולטה!"):
                    play_roulette_sound()
                    target_name = user_data['Target']
                    now = get_israel_time()
                    data.at[user_idx, 'Try'] = "1"
                    data.at[user_idx, 'Timestamp'] = now
                    conn.update(data=data)
                    
                    placeholder = st.empty()
                    names = data['Name'].tolist()
                    # רולטה 5 שניות
                    for _ in range(40):
                        placeholder.markdown(f"<h2 style='text-align: center; color: gray;'>{random.choice(names)}</h2>", unsafe_allow_html=True)
                        time.sleep(0.05)
                    for i in range(10):
                        placeholder.markdown(f"<h2 style='text-align: center; color: #FF4B4B;'>{random.choice(names)}</h2>", unsafe_allow_html=True)
                        time.sleep(0.15)
                    for i in range(3):
                        placeholder.markdown(f"<h2 style='text-align: center; color: #FF4B4B; font-weight: bold;'>{random.choice(names)}</h2>", unsafe_allow_html=True)
                        time.sleep(0.5)
                    
                    placeholder.markdown(f"<h1 style='text-align: center; color: #00CC00; font-size: 40px;'>✨ {target_name} ✨</h1>", unsafe_allow_html=True)
                    st.balloons()
                    st.success(f"חג שמח! הגמד שלך הוא/היא: {target_name}")

        if st.button("🚪 יציאה"):
            del st.session_state['logged_in_user_id']
            del st.session_state['logged_in_name']
            st.rerun()
