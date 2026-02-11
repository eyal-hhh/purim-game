import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
from datetime import datetime, timedelta

# הגדרות עמוד ועיצוב RTL
st.set_page_config(page_title="הגמד והענק - פורים 2026", layout="centered", page_icon="🎭")

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
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_israel_time():
    return (datetime.utcnow() + timedelta(hours=2)).strftime("%d/%m/%Y %H:%M:%S")

if 'failed_attempts' not in st.session_state:
    st.session_state['failed_attempts'] = 0

menu = st.sidebar.selectbox("תפריט ניווט", ["כניסת עובדים", "ניהול (HR)"])

# --- מסך ניהול ---
if menu == "ניהול (HR)":
    st.markdown("<h1 style='text-align: center;'>ניהול משאבי אנוש 🎭</h1>", unsafe_allow_html=True)
    if 'admin_logged_in' not in st.session_state: st.session_state['admin_logged_in'] = False

    if not st.session_state['admin_logged_in']:
        with st.form("admin_login"):
            pw = st.text_input("סיסמת מנהלת (Enter לכניסה):")
            if st.form_submit_button("כניסה"):
                if pw == "פורים2026":
                    st.session_state['admin_logged_in'] = True
                    st.rerun()
                else: st.error("סיסמה שגויה")
    else:
        try:
            current_data = conn.read(ttl=0)
            st.write("### 📊 דוח מעקב")
            st.dataframe(current_data[['Name', 'Try', 'Timestamp', 'Target']].rename(
                columns={'Name': 'שם', 'Try': 'צפיות', 'Timestamp': 'זמן', 'Target': 'גמד'}), use_container_width=True)
            
            csv = current_data.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 הורדת דוח CSV", data=csv, file_name="purim_report.csv")
            if st.sidebar.button("יציאת מנהלת"):
                st.session_state['admin_logged_in'] = False
                st.rerun()
        except: st.error("שגיאה בטעינה")

# --- מסך עובדים (חזרה למספר עובד ישיר) ---
elif menu == "כניסת עובדים":
    st.markdown("<h1 style='text-align: center;'>🎈 פורים 2026: מי הגמד שלי?</h1>", unsafe_allow_html=True)
    
    # בדיקת חסימת ניסיונות בדפדפן
    if st.session_state['failed_attempts'] >= 3:
        st.error("❌ הגישה נחסמה עקב ריבוי ניסיונות שגויים.")
        st.info("יש לפנות למשאבי אנוש כדי לקבל את פרטי הגמד שלך.")
    
    elif 'logged_in_user_id' not in st.session_state:
        with st.form("login_form"):
            emp_id_input = st.text_input("הזינו מספר עובד (ולחצו Enter):")
            if st.form_submit_button("כניסה למערכת"):
                try:
                    data = conn.read(ttl=0)
                    data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
                    user_match = data[data['ID'] == emp_id_input.strip()]
                    
                    if not user_match.empty:
                        st.session_state['logged_in_user_id'] = emp_id_input.strip()
                        st.session_state['failed_attempts'] = 0 # איפוס כשלונות בכניסה מוצלחת
                        st.rerun()
                    else:
                        st.session_state['failed_attempts'] += 1
                        st.error(f"מספר עובד לא נמצא. נותרו עוד {3 - st.session_state['failed_attempts']} ניסיונות.")
                except:
                    st.error("תקלה בחיבור לנתונים.")
    
    else:
        # עובד מחובר
        try:
            data = conn.read(ttl=0)
            data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
            user_idx = data[data['ID'] == st.session_state['logged_in_user_id']].index[0]
            user_data = data.loc[user_idx]
            
            st.markdown(f'<div class="welcome-msg"><h3>שלום, {user_data["Name"]}! 👋</h3></div>', unsafe_allow_html=True)

            if pd.to_numeric(user_data.get('Try', 0), errors='coerce') > 0:
                # כניסה חוזרת - הצגת הודעת אבטחה
                st.warning("המערכת מזהה שכבר הגרלת גמד בעבר.")
                st.info(f"הפעולה בוצעה בתאריך: {user_data.get('Timestamp', 'לא ידוע')}")
                st.error("מטעמי אבטחה, לא ניתן לצפות בשם הגמד פעם נוספת.")
                st.markdown("---")
                st.markdown("### 📞 שכחת מי הגמד שלך?")
                st.markdown("ניתן לפנות למשאבי אנוש (HR) כדי לוודא את הפרטים.")
            else:
                if st.button("🎡 הפעל רולטה וגלה מי הגמד שלי"):
                    target_name = user_data['Target']
                    now = get_israel_time()
                    
                    # עדכון נתונים
                    data.at[user_idx, 'Try'] = 1
                    data.at[user_idx, 'Timestamp'] = now
                    conn.update(data=data)
                    
                    # רולטה
                    placeholder = st.empty()
                    names_list = data['Name'].tolist()
                    for _ in range(15):
                        placeholder.markdown(f"<h2 style='text-align: center; color: gray;'>{random.choice(names_list)}</h2>", unsafe_allow_html=True)
                        time.sleep(0.06)
                    
                    placeholder.markdown(f"<h1 style='text-align: center; color: #00CC00; font-size: 50px;'>✨ {target_name} ✨</h1>", unsafe_allow_html=True)
                    st.balloons()
                    st.success(f"חג שמח! הגמד שלך הוא/היא: {target_name}")
        except: st.error("שגיאה בטעינת הנתונים")

    if 'logged_in_user_id' in st.session_state:
        if st.sidebar.button("יציאת עובד"):
            del st.session_state['logged_in_user_id']
            st.rerun()
