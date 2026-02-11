import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
from datetime import datetime

# הגדרות עמוד ועיצוב RTL
st.set_page_config(page_title="הגמד והענק - פורים 2026", layout="centered", page_icon="🎭")

st.markdown("""
    <style>
    .main { direction: rtl; }
    h1, h2, h3, p, div { text-align: right; direction: rtl; }
    div.stButton > button { width: 100%; border-radius: 10px; height: 3em; background-color: #FF4B4B; color: white; }
    .welcome-msg { background-color: #f0f2f6; padding: 20px; border-radius: 15px; border-right: 5px solid #FF4B4B; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# חיבור לנתונים
conn = st.connection("gsheets", type=GSheetsConnection)

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
    admin_pw = st.text_input("הזיני סיסמת מנהלת", type="password")
    
    if admin_pw == "פורים2026":
        st.success("גישה אושרה")
        try:
            current_data = conn.read(ttl=0)
            
            if st.button("🎰 בצע הגרלה (זהירות: מאפס הכל)"):
                df_results = perform_lottery(current_data)
                conn.update(data=df_results)
                st.success("הגרלה בוצעה והנתונים אופסו!")
                st.rerun()

            st.write("### 📊 דוח מעקב")
            if 'Try' in current_data.columns:
                st.dataframe(current_data[['Name', 'Try', 'Timestamp', 'Target']].rename(
                    columns={'Name': 'שם העובד', 'Try': 'ניסיונות', 'Timestamp': 'זמן הגרלה', 'Target': 'הגמד'}), 
                    use_container_width=True)
        except Exception as e:
            st.error(f"שגיאה: {e}")

# --- מסך עובדים (הזרימה החדשה) ---
elif menu == "כניסת עובדים":
    st.markdown("<h1 style='text-align: center;'>🎈 פורים 2026: מי הגמד שלי?</h1>", unsafe_allow_html=True)
    
    # שלב 1: כניסה עם קוד (מספר עובד)
    if 'logged_in_user' not in st.session_state:
        emp_id_input = st.text_input("להתחלת המשחק, הזינו מספר עובד:", type="password")
        if st.button("כניסה למערכת"):
            try:
                data = conn.read(ttl=0)
                data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
                
                user_match = data[data['ID'] == emp_id_input.strip()]
                
                if not user_match.empty:
                    st.session_state['logged_in_user'] = user_match.iloc[0]['Name']
                    st.session_state['user_id'] = emp_id_input.strip()
                    st.rerun()
                else:
                    st.error("מספר עובד לא נמצא במערכת. פנה למשאבי אנוש.")
            except Exception as e:
                st.error(f"שגיאה בחיבור: {e}")
    
    # שלב 2: העובד מזוהה
    else:
        try:
            data = conn.read(ttl=0)
            data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
            user_data = data[data['ID'] == st.session_state['user_id']].iloc[0]
            user_idx = data[data['ID'] == st.session_state['user_id']].index[0]
            
            st.markdown(f"""
                <div class="welcome-msg">
                    <h3>שלום, {st.session_state['logged_in_user']}! 👋</h3>
                    <p>הגעת למערכת הגמד והענק של פורים 2026.</p>
                </div>
            """, unsafe_allow_html=True)

            # בדיקה אם כבר הגריל
            has_played = pd.to_numeric(user_data.get('Try', 0), errors='coerce') > 0
            
            if has_played:
                st.warning("שימו לב: כבר הגרלתם גמד בעבר!")
                st.info(f"תאריך ושעה: {user_data.get('Timestamp', 'לא ידוע')}")
                st.markdown(f"### הגמד שקיבלת: **{user_data['Target']}**")
                st.write("---")
                st.write("לעובד הבא: נא לרענן את הדף (F5)")
            
            else:
                if st.button("🎡 הפעל רולטה וגלה מי הגמד שלי"):
                    # עדכון נתונים
                    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    data.at[user_idx, 'Try'] = 1
                    data.at[user_idx, 'Timestamp'] = now
                    conn.update(data=data)
                    
                    # אפקט רולטה
                    target_name = user_data['Target']
                    placeholder = st.empty()
                    all_names = data['Name'].tolist()
                    for _ in range(15):
                        placeholder.markdown(f"<h2 style='text-align: center; color: gray;'>{random.choice(all_names)}</h2>", unsafe_allow_html=True)
                        time.sleep(0.06)
                    
                    placeholder.markdown(f"<h1 style='text-align: center; color: #00CC00; font-size: 50px;'>✨ {target_name} ✨</h1>", unsafe_allow_html=True)
                    st.balloons()
                    st.success(f"חג שמח! הגמד שלך הוא/היא: {target_name}")
                    st.write(f"הפעולה נרשמה במערכת בתאריך: {now}")
                    
        except Exception as e:
            st.error(f"תקלה בטעינת הנתונים: {e}")

    # כפתור יציאה (אופציונלי במקום רענון)
    if 'logged_in_user' in st.session_state:
        if st.sidebar.button("יציאה מהמערכת (לעובד הבא)"):
            del st.session_state['logged_in_user']
            del st.session_state['user_id']
            st.rerun()
