import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
from datetime import datetime, timedelta

# הגדרות עמוד - layout="centered" הוא הטוב ביותר למובייל
st.set_page_config(page_title="הגמד והענק 2026", layout="centered", page_icon="🎭")

# עיצוב CSS מותאם אישית למובייל ולעברית
st.markdown("""
    <style>
    /* הגדרות כלליות לימין לשמאל */
    .main { direction: rtl; }
    h1, h2, h3, p, div { text-align: right; direction: rtl; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* התאמת כפתורים למובייל - גדולים ונוחים ללחיצה */
    div.stButton > button, div.stForm submit_button > button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        background-color: #FF4B4B; 
        color: white; 
        font-weight: bold; 
        font-size: 18px;
        margin-top: 10px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    
    /* עיצוב הודעת השלום */
    .welcome-msg { 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 15px; 
        border-right: 8px solid #FF4B4B; 
        margin-bottom: 20px; 
        color: #202124;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    
    /* התאמת שדות קלט למובייל */
    .stTextInput input {
        font-size: 16px !important; /* מונע זום אוטומטי מעצבן באייפון */
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

# תפריט ניווט
menu = st.sidebar.selectbox("בחר מסך:", ["כניסת עובדים", "ניהול (HR)"])

# --- מסך ניהול ---
if menu == "ניהול (HR)":
    st.markdown("<h1 style='text-align: center;'>ניהול משאבי אנוש 🎭</h1>", unsafe_allow_html=True)
    
    if 'admin_logged_in' not in st.session_state: st.session_state['admin_logged_in'] = False

    if not st.session_state['admin_logged_in']:
        with st.form("admin_login"):
            pw = st.text_input("סיסמת מנהלת:", help="הקלידי ולחצי Enter")
            if st.form_submit_button("כניסה למערכת"):
                if pw == "פורים2026":
                    st.session_state['admin_logged_in'] = True
                    st.rerun()
                else: st.error("סיסמה שגויה")
    else:
        try:
            current_data = conn.read(ttl=0)
            
            # כפתור הגרלה בולט
            if st.button("🎰 הפעל הגרלה כללית"):
                with st.spinner("מבצע הגרלה..."):
                    df_results = perform_lottery(current_data)
                    conn.update(data=df_results)
                    st.success("ההגרלה הסתיימה!")
                    time.sleep(1)
                    st.rerun()

            st.write("### 📊 מעקב עובדים")
            # הטבלה מותאמת לרוחב הנייד עם אפשרות גלילה
            st.dataframe(current_data[['Name', 'Try', 'Timestamp', 'Target']].rename(
                columns={'Name': 'שם', 'Try': 'צפיות', 'Timestamp': 'זמן', 'Target': 'גמד'}), 
                use_container_width=True)
            
            csv = current_data.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 הורדת דוח CSV", data=csv, file_name="purim_report.csv")
            
            if st.sidebar.button("יציאת מנהלת"):
                st.session_state['admin_logged_in'] = False
                st.rerun()
        except: st.error("שגיאה בטעינה")

# --- מסך עובדים ---
elif menu == "כניסת עובדים":
    st.markdown("<h1 style='text-align: center;'>🎈 פורים 2026: מי הגמד שלי?</h1>", unsafe_allow_html=True)
    
    if 'logged_in_user' not in st.session_state:
        with st.form("login_form"):
            st.write("ברוכים הבאים למשחק!")
            emp_id_input = st.text_input("הזינו מספר עובד:")
            if st.form_submit_button("כניסה"):
                try:
                    data = conn.read(ttl=0)
                    data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
                    user_match = data[data['ID'] == emp_id_input.strip()]
                    if not user_match.empty:
                        st.session_state['logged_in_user'] = user_match.iloc[0]['Name']
                        st.session_state['user_id'] = emp_id_input.strip()
                        st.rerun()
                    else: st.error("מספר עובד לא נמצא.")
                except: st.error("שגיאה בחיבור")
    
    else:
        try:
            data = conn.read(ttl=0)
            data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
            user_idx = data[data['ID'] == st.session_state['user_id']].index[0]
            user_data = data.loc[user_idx]
            
            st.markdown(f'<div class="welcome-msg"><h3>שלום, {st.session_state["logged_in_user"]}! 👋</h3></div>', unsafe_allow_html=True)

            tries = pd.to_numeric(user_data.get('Try', 0), errors='coerce')
            
            if tries > 0:
                st.warning("המערכת מזהה שכבר הגרלת גמד בעבר.")
                st.info(f"בוצע בתאריך: {user_data.get('Timestamp', 'לא ידוע')}")
                st.error("מטעמי אבטחה, לא ניתן לצפות בשם שוב.")
                st.markdown("---")
                st.markdown("### 📞 שכחת מי הגמד?")
                st.markdown("ניתן לפנות למשאבי אנוש (HR) לווידוי השם.")
            else:
                if st.button("🎡 הפעל רולטה!"):
                    target_name = user_data['Target']
                    now = get_israel_time()
                    
                    data.at[user_idx, 'Try'] = 1
                    data.at[user_idx, 'Timestamp'] = now
                    conn.update(data=data)
                    
                    # רולטה מותאמת למהירות נייד
                    placeholder = st.empty()
                    names = data['Name'].tolist()
                    for _ in range(12):
                        placeholder.markdown(f"<h2 style='text-align: center; color: gray;'>{random.choice(names)}</h2>", unsafe_allow_html=True)
                        time.sleep(0.08)
                    
                    placeholder.markdown(f"<h1 style='text-align: center; color: #00CC00; font-size: 40px;'>✨ {target_name} ✨</h1>", unsafe_allow_html=True)
                    st.balloons()
                    st.success(f"חג שמח! הגמד שלך הוא/היא: {target_name}")
        except: st.error("שגיאה בטעינת הנתונים")

    if 'logged_in_user' in st.session_state:
        if st.sidebar.button("יציאת עובד"):
            del st.session_state['logged_in_user']
            del st.session_state['user_id']
            st.rerun()
