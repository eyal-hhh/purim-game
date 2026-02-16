import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
from datetime import datetime, timedelta

# הגדרות עמוד
st.set_page_config(page_title="הגמד והענק 2026", layout="centered", page_icon="🎭")

# עיצוב CSS ממוקד למובייל וצמצום רווחים
st.markdown("""
    <style>
    .main { direction: rtl; }
    h1, h2, h3, p, div, span { text-align: right; direction: rtl; font-family: 'Segoe UI', sans-serif; }
    
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    [data-testid="stSidebar"] { display: none; }

    div.stButton > button, div.stForm submit_button > button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background-color: #FF4B4B; color: white; font-weight: bold; font-size: 18px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1); border: none;
    }
    
    .welcome-msg { 
        background-color: #f1f3f4; padding: 15px; border-radius: 12px; 
        border-right: 8px solid #FF4B4B; margin-bottom: 10px; color: #202124;
    }
    
    .stTextInput input, .stSelectbox div[data-baseweb="select"] { font-size: 16px !important; }
    div[data-testid="stHorizontalBlock"] { background: #f8f9fa; padding: 5px; border-radius: 10px; }
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
menu = st.radio("", ["כניסת גמדים", "ניהול (HR)"], horizontal=True, label_visibility="collapsed")

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
                st.warning("שים/י לב: פעולה זו תמחק את כל שיבוצי הענקים הקיימים!")
                confirm_pw = st.text_input("הקלידי שוב סיסמה לאישור:", type="password", key="confirm_hr")
                if confirm_pw == "פורים2026":
                    if st.button("🔥 הפעל הגרלה חדשה (שבץ ענקים)"):
                        df_copy = data.dropna(subset=['Name', 'ID']).copy()
                        names = df_copy['Name'].tolist()
                        shuffled = names.copy()
                        random.shuffle(shuffled)
                        while any(names[i] == shuffled[i] for i in range(len(names))): random.shuffle(shuffled)
                        df_copy['Target'] = shuffled
                        df_copy['Try'] = "0"
                        df_copy['Timestamp'] = ""
                        conn.update(data=df_copy)
                        st.success("בוצע!")
                        st.rerun()

            col1, col2 = st.columns(2)
            with col1:
                csv = data.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 הורדת CSV", data=csv, file_name="purim_report.csv")
            with col2:
                if st.button("🚪 יציאה", key="admin_logout"):
                    st.session_state['admin_logged_in'] = False
                    st.rerun()
            
            st.dataframe(data[['Name', 'Timestamp', 'Try', 'Target']].rename(
                columns={'Name': 'הגמד', 'Timestamp': 'זמן', 'Try': 'צפיות', 'Target': 'הענק'}), 
                use_container_width=True, hide_index=True)

# --- מסך עובדים (גמדים) ---
else:
    st.markdown("<h3 style='text-align: center;'>🎈 פורים 2026: מי הענק שלי?</h3>", unsafe_allow_html=True)
    
    # טעינת נתונים ראשונית להצגת השמות
    data = load_and_clean_data()
    
    if data is not None and 'logged_in_user_id' not in st.session_state:
        # יצירת רשימת שמות ממוינת א'-ב'
        all_names = sorted(data['Name'].unique().tolist())
        
        with st.form("login_form"):
            selected_name = st.selectbox("בחר/י את שמך מהרשימה:", ["בחר/י שם..."] + all_names)
            emp_id_input = st.text_input("הזינו מספר עובד לזיהוי:")
            
            if st.form_submit_button("כניסה למערכת"):
                if selected_name == "בחר/י שם...":
                    st.error("חובה לבחור שם מהרשימה.")
                else:
                    # חיפוש השורה של השם שנבחר
                    user_row = data[data['Name'] == selected_name].iloc[0]
                    correct_id = str(user_row['ID']).strip()
                    
                    if emp_id_input.strip() == correct_id:
                        st.session_state['logged_in_user_id'] = correct_id
                        st.session_state['logged_in_name'] = selected_name
                        st.rerun()
                    else:
                        st.error("מספר עובד לא תואם לשם שנבחר.")
    
    elif data is not None:
        # המשתמש כבר מחובר
        user_idx = data[data['ID'] == st.session_state['logged_in_user_id']].index[0]
        user_data = data.loc[user_idx]
        
        st.markdown(f'<div class="welcome-msg"><b>שלום הגמד {st.session_state["logged_in_name"]}!</b></div>', unsafe_allow_html=True)

        result_placeholder = st.empty()

        try:
            try_val = int(float(user_data.get('Try', '0')))
        except:
            try_val = 0
        
        if try_val > 0:
            result_placeholder.warning("המערכת מזהה שכבר הגרלת ענק בעבר.")
            st.info(f"הפעולה בוצעה בתאריך: {user_data.get('Timestamp', 'לא ידוע')}")
            st.error("מטעמי אבטחה, לא ניתן לצפות בשם הענק פעם נוספת.")
            st.markdown("---")
            st.markdown("### 📞 שכחת מי הענק שלך? פנה למשאבי אנוש.")
        else:
            button_placeholder = st.empty()
            if button_placeholder.button("🎡 גלה מי הענק שלי!", key="play_btn"):
                button_placeholder.empty()
                play_roulette_sound()
                target_name = user_data['Target']
                now = get_israel_time()
                
                # עדכון נתונים
                data.at[user_idx, 'Try'] = "1"
                data.at[user_idx, 'Timestamp'] = now
                conn.update(data=data)
                
                # רולטה
                names = data['Name'].tolist()
                for _ in range(35):
                    result_placeholder.markdown(f"<h2 style='text-align: center; color: gray;'>{random.choice(names)}</h2>", unsafe_allow_html=True)
                    time.sleep(0.06)
                for _ in range(8):
                    result_placeholder.markdown(f"<h2 style='text-align: center; color: #FF4B4B;'>{random.choice(names)}</h2>", unsafe_allow_html=True)
                    time.sleep(0.18)
                for _ in range(3):
                    result_placeholder.markdown(f"<h2 style='text-align: center; color: #FF4B4B; font-weight: bold;'>{random.choice(names)}</h2>", unsafe_allow_html=True)
                    time.sleep(0.5)
                
                result_placeholder.markdown(f"""
                    <div style="text-align: center; background-color: #e8f5e9; padding: 20px; border-radius: 15px; border: 2px solid #4caf50;">
                        <h2 style="margin: 0;">הענק שלך הוא/היא:</h2>
                        <h1 style="color: #2e7d32; font-size: 45px; margin: 10px 0;">✨ {target_name} ✨</h1>
                    </div>
                """, unsafe_allow_html=True)
                st.balloons()

        if st.button("🚪 יציאה", key="user_logout"):
            del st.session_state['logged_in_user_id']
            del st.session_state['logged_in_name']
            st.rerun()
            
