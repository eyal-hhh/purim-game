import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# הגדרות עמוד ועיצוב RTL לעברית
st.set_page_config(page_title="הגמד והענק - פורים 2026", layout="centered", page_icon="🎭")

st.markdown("""
    <style>
    .main { direction: rtl; }
    div.stButton > button { width: 100%; border-radius: 10px; height: 3em; background-color: #FF4B4B; color: white; }
    h1, h2, h3, p, div { text-align: right; direction: rtl; }
    .stSelectbox label { text-align: right; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# פונקציית הגרלה
def perform_lottery(df):
    df = df.dropna(subset=['Name', 'ID']).copy()
    names = df['Name'].tolist()
    shuffled = names.copy()
    attempts = 0
    while any(names[i] == shuffled[i] for i in range(len(names))) and attempts < 100:
        random.shuffle(shuffled)
        attempts += 1
    df['Target'] = shuffled
    return df

# חיבור לגוגל שיטס
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"שגיאה בחיבור הראשוני: {e}")

menu = st.sidebar.selectbox("תפריט ניווט", ["כניסת עובדים", "ניהול (HR)"])

# --- מסך ניהול ---
if menu == "ניהול (HR)":
    st.markdown("<h1 style='text-align: center;'>ניהול משאבי אנוש 🎭</h1>", unsafe_allow_html=True)
    admin_pw = st.text_input("הזיני סיסמת מנהלת", type="password")
    
    if admin_pw == "פורים2026":
        st.success("גישה אושרה")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎰 בצע הגרלה"):
                try:
                    with st.spinner("מבצע הגרלה..."):
                        df = conn.read(ttl=0)
                        df_results = perform_lottery(df)
                        conn.update(data=df_results)
                        st.success("ההגרלה הסתיימה בהצלחה!")
                except Exception as e:
                    st.error(f"תקלה בביצוע ההגרלה: {e}")

        with col2:
            try:
                data_to_export = conn.read(ttl=0)
                if 'Target' in data_to_export.columns:
                    # הורדה כ-CSV (הכי בטוח לעברית באקסל)
                    csv = data_to_export.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 הורדת קובץ לגיבוי (Excel/PDF)",
                        data=csv,
                        file_name="purim_lottery_2026.csv",
                        mime="text/csv",
                    )
            except:
                st.write("ממתין לנתונים...")

# --- מסך עובדים ---
elif menu == "כניסת עובדים":
    st.markdown("<h1 style='text-align: center;'>🎈 פורים 2026: מי הגמד שלי?</h1>", unsafe_allow_html=True)
    
    status_placeholder = st.empty()
    status_placeholder.info("טוען נתונים מהשרת, נא להמתין...")
    
    try:
        data = conn.read(ttl=0)
        status_placeholder.empty() # מסיר את הודעת הטעינה כשהנתונים הגיעו
        
        # ניקוי נתונים
        data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
        
        if 'Target' not in data.columns or data['Target'].isnull().all():
            st.warning("ההגרלה טרם בוצעה על ידי משאבי אנוש. נא לחזור מאוחר יותר.")
        else:
            names_list = sorted(data['Name'].dropna().unique().tolist())
            selected_user = st.selectbox("בחר/י את שמך (את/ה הענק):", [""] + names_list)
            
            if selected_user:
                emp_id = st.text_input("הזינו מספר עובד לזיהוי:", type="password")
                
                if st.button("🎡 גלה/י מי הגמד שלי!"):
                    user_row = data[data['Name'] == selected_user].iloc[0]
                    
                    if str(emp_id).strip() == str(user_row['ID']):
                        target_name = user_row['Target']
                        
                        # --- רולטה ---
                        st.write("---")
                        placeholder = st.empty()
                        all_names = data['Name'].tolist()
                        
                        for _ in range(15):
                            placeholder.markdown(f"<h2 style='text-align: center; color: gray;'>{random.choice(all_names)}</h2>", unsafe_allow_html=True)
                            time.sleep(0.05)
                        for i in range(1, 6):
                            placeholder.markdown(f"<h2 style='text-align: center; color: #FF4B4B;'>{random.choice(all_names)}</h2>", unsafe_allow_html=True)
                            time.sleep(0.1 * i)
                        
                        placeholder.markdown(f"<h1 style='text-align: center; color: #00CC00; font-size: 50px;'>✨ {target_name} ✨</h1>", unsafe_allow_html=True)
                        st.balloons()
                        st.markdown(f"<h3 style='text-align: center;'>חג שמח! הגמד שלך הוא/היא: {target_name}</h3>", unsafe_allow_html=True)
                    else:
                        st.error("מספר עובד לא תקין. נסו שוב.")
                        
    except Exception as e:
        status_placeholder.error(f"לא הצלחנו להתחבר לנתונים: {e}")
