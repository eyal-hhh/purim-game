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
    df['Failed'] = 0  # איפוס ניסיונות כושלים
    df['Timestamp'] = ""
    return df

menu = st.sidebar.selectbox("תפריט ניווט", ["כניסת עובדים", "ניהול (HR)"])

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
        try:
            current_data = conn.read(ttl=0)
            st.write("### 📊 דוח מעקב ובקרה")
            
            # הצגת הטבלה עם סימון אדום למי שחסום
            display_df = current_data[['Name', 'Failed', 'Try', 'Timestamp', 'Target']].copy()
            st.dataframe(display_df.rename(
                columns={'Name': 'שם', 'Failed': 'נכשלו', 'Try': 'צפיות', 'Timestamp': 'זמן', 'Target': 'גמד'}), 
                use_container_width=True)
            
            if st.button("🎰 בצע הגרלה חדשה (מאפס הכל!)"):
                df_res = perform_lottery(current_data)
                conn.update(data=df_res)
                st.success("הגרלה בוצעה!")
                st.rerun()
                
            if st.button("🔓 שחרר את כל החסימות (אפס כשלונות)"):
                current_data['Failed'] = 0
                conn.update(data=current_data)
                st.success("כל החסימות שוחררו.")
                st.rerun()

            if st.button("יציאה"):
                st.session_state['admin_logged_in'] = False
                st.rerun()
        except: st.error("שגיאה בטעינה")

# --- מסך עובדים ---
elif menu == "כניסת עובדים":
    st.markdown("<h1 style='text-align: center;'>🎈 פורים 2026: מי הגמד שלי?</h1>", unsafe_allow_html=True)
    
    try:
        data = conn.read(ttl=0)
        data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
        
        # שלב 1: בחירת שם (כדי שנדע את מי לחסום אם יטעה)
        names_list = sorted(data['Name'].dropna().unique().tolist())
        selected_user = st.selectbox("בחר/י את שמך מהרשימה:", [""] + names_list)
        
        if selected_user:
            user_idx = data[data['Name'] == selected_user].index[0]
            failed_count = pd.to_numeric(data.at[user_idx, 'Failed'], errors='coerce')
            failed_count = 0 if pd.isna(failed_count) else int(failed_count)

            # בדיקה אם המשתמש חסום
            if failed_count >= 3:
                st.error("❌ הגישה נחסמה עקב 3 ניסיונות כושלים.")
                st.warning("יש לפנות למשאבי אנוש (HR) כדי לשחרר את החסימה.")
            else:
                with st.form("login_form"):
                    emp_id_input = st.text_input(f"שלום {selected_user}, הזינו מספר עובד לזיהוי:")
                    if st.form_submit_button("כניסה למערכת"):
                        actual_id = str(data.at[user_idx, 'ID'])
                        
                        if emp_id_input.strip() == actual_id:
                            # הצלחה - איפוס כשלונות אם היו
                            data.at[user_idx, 'Failed'] = 0
                            
                            # בדיקה אם כבר צפה
                            if pd.to_numeric(data.at[user_idx, 'Try'], errors='coerce') > 0:
                                st.warning("המערכת מזהה שכבר הגרלת גמד בעבר.")
                                st.info(f"הפעולה בוצעה בתאריך: {data.at[user_idx, 'Timestamp']}")
                                st.error("מטעמי אבטחה, לא ניתן לצפות בשם שוב. יש לפנות למשאבי אנוש.")
                                conn.update(data=data)
                            else:
                                # הגרלה ראשונה
                                target_name = data.at[user_idx, 'Target']
                                now = get_israel_time()
                                data.at[user_idx, 'Try'] = 1
                                data.at[user_idx, 'Timestamp'] = now
                                conn.update(data=data)
                                
                                # רולטה
                                placeholder = st.empty()
                                for _ in range(15):
                                    placeholder.markdown(f"<h2 style='text-align: center; color: gray;'>{random.choice(names_list)}</h2>", unsafe_allow_html=True)
                                    time.sleep(0.06)
                                
                                placeholder.markdown(f"<h1 style='text-align: center; color: #00CC00; font-size: 50px;'>✨ {target_name} ✨</h1>", unsafe_allow_html=True)
                                st.balloons()
                                st.success(f"חג שמח! הגמד שלך הוא/היא: {target_name}")
                        else:
                            # כישלון - עדכון מונה
                            data.at[user_idx, 'Failed'] = failed_count + 1
                            conn.update(data=data)
                            st.error(f"מספר עובד שגוי. נותרו לך {3 - (failed_count + 1)} ניסיונות עד לחסימה.")
                            if (failed_count + 1) >= 3: st.rerun()

    except Exception as e: st.error(f"שגיאה: {e}")
