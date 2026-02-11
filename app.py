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
    # חישוב זמן ישראל (UTC+2)
    return (datetime.utcnow() + timedelta(hours=2)).strftime("%d/%m/%Y %H:%M:%S")

def perform_lottery(df):
    """פונקציה שמבצעת את ערבוב השמות"""
    df = df.dropna(subset=['Name', 'ID']).copy()
    names = df['Name'].tolist()
    shuffled = names.copy()
    
    attempts = 0
    # וידוא שאף אחד לא מקבל את עצמו
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
            # קריאת נתונים
            current_data = conn.read(ttl=0)
            
            # הכפתור שחזר מהגלות:
            if st.button("🎰 בצע הגרלה (זהירות: זה מערבב מחדש ומאפס הכל!)"):
                with st.spinner("מערבב את הגמדים..."):
                    df_results = perform_lottery(current_data)
                    conn.update(data=df_results)
                    st.success("ההגרלה הסתיימה בהצלחה! השמות שובצו בגיליון.")
                    time.sleep(1)
                    st.rerun()

            st.write("---")
            st.write("### 📊 דוח מעקב חסוי")
            
            st.dataframe(current_data[['Name', 'Try', 'Timestamp', 'Target']].rename(
                columns={'Name': 'שם', 'Try': 'צפיות', 'Timestamp': 'זמן צפייה', 'Target': 'הגמד'}), use_container_width=True)
            
            csv = current_data.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 הורדת דוח מלא (Excel/CSV)", data=csv, file_name="purim_report.csv")
            
            if st.sidebar.button("יציאת מנהלת"):
                st.session_state['admin_logged_in'] = False
                st.rerun()
        except Exception as e: 
            st.error(f"שגיאה בטעינת הנתונים: {e}")

# --- מסך עובדים ---
elif menu == "כניסת עובדים":
    st.markdown("<h1 style='text-align: center;'>🎈 פורים 2026: מי הגמד שלי?</h1>", unsafe_allow_html=True)
    
    if 'logged_in_user' not in st.session_state:
        with st.form("login_form"):
            emp_id_input = st.text_input("הזינו מספר עובד (ולחצו Enter):")
            if st.form_submit_button("כניסה למערכת"):
                data = conn.read(ttl=0)
                data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
                user_match = data[data['ID'] == emp_id_input.strip()]
                if not user_match.empty:
                    st.session_state['logged_in_user'] = user_match.iloc[0]['Name']
                    st.session_state['user_id'] = emp_id_input.strip()
                    st.rerun()
                else: st.error("מספר עובד לא נמצא.")
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
                st.info(f"הפעולה בוצעה בתאריך: {user_data.get('Timestamp', 'לא ידוע')}")
                st.error("מטעמי אבטחה, לא ניתן לצפות בשם הגמד פעם נוספת דרך המערכת.")
                st.markdown("---")
                st.markdown("### 📞 שכחת מי הגמד שלך?")
                st.markdown("אין בעיה! ניתן לפנות למשאבי אנוש (HR) כדי לוודא מי הגמד שקיבלת.")
            else:
                if st.button("🎡 הפעל רולטה וגלה מי הגמד שלי"):
                    target_name = user_data['Target']
                    now = get_israel_time()
                    
                    data.at[user_idx, 'Try'] = 1
                    data.at[user_idx, 'Timestamp'] = now
                    conn.update(data=data)
                    
                    placeholder = st.empty()
                    names = data['Name'].tolist()
                    for _ in range(15):
                        placeholder.markdown(f"<h2 style='text-align: center; color: gray;'>{random.choice(names)}</h2>", unsafe_allow_html=True)
                        time.sleep(0.06)
                    
                    placeholder.markdown(f"<h1 style='text-align: center; color: #00CC00; font-size: 50px;'>✨ {target_name} ✨</h1>", unsafe_allow_html=True)
                    st.balloons()
                    st.success(f"חג שמח! הגמד שלך הוא/היא: {target_name}")
        except Exception as e: 
            st.error(f"שגיאה: {e}")

    if 'logged_in_user' in st.session_state:
        if st.sidebar.button("יציאת עובד"):
            del st.session_state['logged_in_user']
            del st.session_state['user_id']
            st.rerun()
