import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
from datetime import datetime, timedelta

# הגדרות עמוד ועיצוב RTL
st.set_page_config(page_title="הגמד והענק - פורים 2026", layout="centered", page_icon="🎭")

# עיצוב CSS משופר
st.markdown("""
    <style>
    .main { direction: rtl; }
    h1, h2, h3, p, div { text-align: right; direction: rtl; }
    div.stButton > button, div.stForm submit_button > button { 
        width: 100%; border-radius: 10px; height: 3em; 
        background-color: #FF4B4B; color: white; font-weight: bold; 
    }
    .welcome-msg { 
        background-color: #f1f3f4; padding: 20px; border-radius: 15px; 
        border-right: 8px solid #FF4B4B; margin-bottom: 20px; color: #202124; 
    }
    .welcome-msg h3 { color: #000000; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# חיבור לנתונים
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

menu = st.sidebar.selectbox("תפריט ניווט", ["כניסת עובדים", "ניהול (HR)"])

# --- מסך ניהול ---
if menu == "ניהול (HR)":
    st.markdown("<h1 style='text-align: center;'>ניהול משאבי אנוש 🎭</h1>", unsafe_allow_html=True)
    
    # שימוש ב-session_state לשמירת מצב התחברות של המנהלת
    if 'admin_logged_in' not in st.session_state:
        st.session_state['admin_logged_in'] = False

    if not st.session_state['admin_logged_in']:
        with st.form("admin_login_form"):
            admin_pw_input = st.text_input("הזיני סיסמת מנהלת (ללא כוכביות, תומך ב-Enter):")
            admin_submit = st.form_submit_button("כניסה למערכת הניהול")
            
            if admin_submit:
                if admin_pw_input == "פורים2026":
                    st.session_state['admin_logged_in'] = True
                    st.rerun()
                else:
                    st.error("סיסמה שגויה")
    else:
        # תוכן מסך הניהול לאחר התחברות
        st.success("גישה אושרה")
        if st.sidebar.button("יציאת מנהלת"):
            st.session_state['admin_logged_in'] = False
            st.rerun()

        try:
            current_data = conn.read(ttl=0)
            if st.button("🎰 בצע הגרלה (זהירות: מאפס הכל)"):
                df_results = perform_lottery(current_data)
                conn.update(data=df_results)
                st.success("הגרלה בוצעה בהצלחה!")
                st.rerun()
            
            st.write("### 📊 דוח מעקב")
            st.dataframe(current_data[['Name', 'Try', 'Timestamp', 'Target']].rename(
                columns={'Name': 'שם', 'Try': 'ניסיונות', 'Timestamp': 'זמן', 'Target': 'גמד'}), use_container_width=True)
        except Exception as e:
            st.error(f"שגיאה: {e}")

# --- מסך עובדים ---
elif menu == "כניסת עובדים":
    st.markdown("<h1 style='text-align: center;'>🎈 פורים 2026: מי הגמד שלי?</h1>", unsafe_allow_html=True)
    
    if 'logged_in_user' not in st.session_state:
        with st.form("login_form"):
            emp_id_input = st.text_input("להתחלת המשחק, הזינו מספר עובד:")
            submit_button = st.form_submit_button("כניסה למערכת")
            
            if submit_button:
                try:
                    data = conn.read(ttl=0)
                    data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
                    user_match = data[data['ID'] == emp_id_input.strip()]
                    
                    if not user_match.empty:
                        st.session_state['logged_in_user'] = user_match.iloc[0]['Name']
                        st.session_state['user_id'] = emp_id_input.strip()
                        st.rerun()
                    else:
                        st.error("מספר עובד לא נמצא במערכת.")
                except Exception as e:
                    st.error(f"שגיאה בחיבור: {e}")
    
    else:
        try:
            data = conn.read(ttl=0)
            data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
            user_data = data[data['ID'] == st.session_state['user_id']].iloc[0]
            user_idx = data[data['ID'] == st.session_state['user_id']].index[0]
            
            st.markdown(f"""
                <div class="welcome-msg">
                    <h3>שלום, {st.session_state['logged_in_user']}! 👋</h3>
                    <p>הגעת למערכת הגמד והענק של פורים.</p>
                </div>
            """, unsafe_allow_html=True)

            has_played = pd.to_numeric(user_data.get('Try', 0), errors='coerce') > 0
            
            if has_played:
                st.warning("כבר הגרלת גמד בעבר!")
                st.info(f"הגרלת בתאריך: {user_data.get('Timestamp', 'לא ידוע')}")
                st.markdown(f"<h2 style='text-align: center; color: #00CC00;'>הגמד שלך הוא/היא: {user_data['Target']}</h2>", unsafe_allow_html=True)
            else:
                if st.button("🎡 הפעל רולטה וגלה מי הגמד שלי"):
                    now_israel = get_israel_time()
                    data.at[user_idx, 'Try'] = 1
                    data.at[user_idx, 'Timestamp'] = now_israel
                    conn.update(data=data)
                    
                    target_name = user_data['Target']
                    placeholder = st.empty()
                    all_names = data['Name'].tolist()
                    for _ in range(15):
                        placeholder.markdown(f"<h2 style='text-align: center; color: gray;'>{random.choice(all_names)}</h2>", unsafe_allow_html=True)
                        time.sleep(0.06)
                    
                    placeholder.markdown(f"<h1 style='text-align: center; color: #00CC00; font-size: 50px;'>✨ {target_name} ✨</h1>", unsafe_allow_html=True)
                    st.balloons()
                    st.success(f"חג שמח! הגמד שלך הוא/היא: {target_name}")
                    
        except Exception as e:
            st.error(f"תקלה בטעינת הנתונים: {e}")

    if 'logged_in_user' in st.session_state:
        if st.sidebar.button("יציאה מהמערכת"):
            del st.session_state['logged_in_user']
            del st.session_state['user_id']
            st.rerun()
