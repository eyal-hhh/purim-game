import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# הגדרות עמוד ו-CSS (נשאר כפי שהיה)
st.set_page_config(page_title="הגמד והענק - פורים 2026", layout="centered", page_icon="🎭")
st.markdown("""<style>h1, h2, h3, p { direction: rtl; text-align: right; }</style>""", unsafe_allow_html=True)

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
    return df

menu = st.sidebar.selectbox("תפריט ניווט", ["כניסת עובדים", "ניהול (HR)"])

if menu == "ניהול (HR)":
    st.markdown("<h1 style='text-align: center;'>ניהול משאבי אנוש 🎭</h1>", unsafe_allow_html=True)
    admin_pw = st.text_input("הזיני סיסמת מנהלת", type="password")
    
    if admin_pw == "פורים2026":
        st.success("גישה אושרה")
        
        # כפתור ביצוע הגרלה
        if st.button("🎰 בצע הגרלה כללית"):
            try:
                df = conn.read(ttl=0)
                df_results = perform_lottery(df)
                conn.update(data=df_results)
                st.success("ההגרלה הסתיימה בהצלחה!")
            except Exception as e:
                st.error(f"שגיאה: {e}")

        st.write("---")
        st.write("### אפשרויות הורדה וגיבוי")
        
        try:
            # קריאת הנתונים העדכניים להורדה
            df_to_download = conn.read(ttl=0)
            
            if 'Target' in df_to_download.columns and not df_to_download['Target'].isnull().all():
                # אפשרות 1: הורדה ל-Excel/CSV (הכי בטוח לעברית)
                # utf-8-sig מבטיח שהעברית תיפתח טוב באקסל
                csv = df_to_download.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 הורדת תוצאות ל-Excel (מומלץ לעברית)",
                    data=csv,
                    file_name="purim_2026_results.csv",
                    mime="text/csv",
                )
                
                # אפשרות 2: הורדה ל-PDF
                # הערה: כדי שזה יעבוד עם עברית, מומלץ להשתמש בפורמט ה-CSV ולהדפיס ל-PDF מהאקסל.
                # אם בכל זאת תרצה PDF ישיר מהקוד, נדרשת ספריית fpdf2 וגופן TTF.
                st.info("טיפ: להדפסת PDF יפה, מומלץ להוריד את קובץ ה-Excel ולשמור אותו כ-PDF.")
                
            else:
                st.warning("עדיין אין תוצאות להורדה. יש לבצע הגרלה קודם.")
        except:
            st.error("לא ניתן לטעון נתונים להורדה.")

# --- חלק העובדים (נשאר ללא שינוי) ---
elif menu == "כניסת עובדים":
    st.markdown("<h1 style='text-align: center;'>🎈 פורים 2026: מי הגמד שלי?</h1>", unsafe_allow_html=True)
    # ... (שאר הקוד של העובדים)
