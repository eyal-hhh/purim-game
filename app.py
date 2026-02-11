import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# הגדרות עמוד ועיצוב RTL
st.set_page_config(page_title="הגמד והענק - פורים 2026", layout="centered", page_icon="🎭")

st.markdown("""
    <style>
    .main { direction: rtl; }
    h1, h2, h3, p, div { text-align: right; direction: rtl; }
    div.stButton > button { width: 100%; border-radius: 10px; height: 3em; background-color: #FF4B4B; color: white; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# חיבור לנתונים
conn = st.connection("gsheets", type=GSheetsConnection)

def perform_lottery(df):
    """מבצע הגרלה ומאפס ניסיונות"""
    df = df.dropna(subset=['Name', 'ID']).copy()
    names = df['Name'].tolist()
    shuffled = names.copy()
    attempts = 0
    while any(names[i] == shuffled[i] for i in range(len(names))) and attempts < 100:
        random.shuffle(shuffled)
        attempts += 1
    df['Target'] = shuffled
    df['Try'] = 0
    return df

menu = st.sidebar.selectbox("תפריט ניווט", ["כניסת עובדים", "ניהול (HR)"])

# --- מסך ניהול ---
if menu == "ניהול (HR)":
    st.markdown("<h1 style='text-align: center;'>ניהול משאבי אנוש 🎭</h1>", unsafe_allow_html=True)
    admin_pw = st.text_input("הזיני סיסמת מנהלת", type="password")
    
    if admin_pw == "פורים2026":
        st.success("גישה אושרה")
        
        # קריאת נתונים עדכניים לצורך הצגת הטבלה
        try:
            current_data = conn.read(ttl=0)
            
            # --- לוח בקרה (Stats) ---
            if 'Try' in current_data.columns:
                current_data['Try'] = pd.to_numeric(current_data['Try'], errors='coerce').fillna(0).astype(int)
                total_emps = len(current_data)
                played = len(current_data[current_data['Try'] > 0])
                
                col1, col2 = st.columns(2)
                col1.metric("סה\"כ עובדים", total_emps)
                col2.metric("גילו את הגמד", f"{played} ({int(played/total_emps*100) if total_emps > 0 else 0}%)")
                
                st.write("### 📊 טבלת מעקב חיה")
                # הצגת טבלה מסודרת למנהלת
                st.dataframe(
                    current_data[['Name', 'Try', 'Target']].rename(columns={'Name': 'שם העובד', 'Try': 'ניסיונות', 'Target': 'הגמד שנבחר'}),
                    use_container_width=True
                )
            
            st.write("---")
            
            # כפתורי פעולה
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🎰 הגרלה חדשה (זהירות: מאפס הכל)"):
                    df_results = perform_lottery(current_data)
                    conn.update(data=df_results)
                    st.success("הגרלה בוצעה בהצלחה!")
                    st.rerun()
            
            with col_b:
                csv = current_data.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 הורדת דוח אקסל", data=csv, file_name="purim_report.csv", mime="text/csv")
                
        except Exception as e:
            st.error(f"שגיאה בטעינת נתוני מעקב: {e}")

# --- מסך עובדים ---
elif menu == "כניסת עובדים":
    st.markdown("<h1 style='text-align: center;'>🎈 פורים 2026: מי הגמד שלי?</h1>", unsafe_allow_html=True)
    
    try:
        data = conn.read(ttl=0)
        data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
        
        if 'Target' not in data.columns or data['Target'].isnull().all():
            st.warning("ההגרלה טרם בוצעה על ידי משאבי אנוש.")
        else:
            names_list = sorted(data['Name'].dropna().unique().tolist())
            selected_user = st.selectbox("בחר/י את שמך (את/ה הענק):", [""] + names_list)
            
            if selected_user:
                emp_id = st.text_input("הזינו מספר עובד לזיהוי:", type="password")
                
                if st.button("🎡 הפעל רולטה"):
                    user_idx = data[data['Name'] == selected_user].index[0]
                    if str(emp_id).strip() == str(data.at[user_idx, 'ID']):
                        
                        # עדכון מונה בגיליון
                        current_tries = pd.to_numeric(data.at[user_idx, 'Try'], errors='coerce')
                        data.at[user_idx, 'Try'] = (0 if pd.isna(current_tries) else current_tries) + 1
                        conn.update(data=data)
                        
                        # רולטה
                        target_name = data.at[user_idx, 'Target']
                        placeholder = st.empty()
                        all_names = data['Name'].tolist()
                        for _ in range(15):
                            placeholder.markdown(f"<h2 style='text-align: center; color: gray;'>{random.choice(all_names)}</h2>", unsafe_allow_html=True)
                            time.sleep(0.06)
                        
                        placeholder.markdown(f"<h1 style='text-align: center; color: #00CC00; font-size: 50px;'>✨ {target_name} ✨</h1>", unsafe_allow_html=True)
                        st.balloons()
                        st.markdown(f"<h3 style='text-align: center;'>חג שמח! הגמד שלך הוא/היא: {target_name}</h3>", unsafe_allow_html=True)
                    else:
                        st.error("מספר עובד לא תקין.")
    except Exception as e:
        st.error(f"שגיאה: {e}")
