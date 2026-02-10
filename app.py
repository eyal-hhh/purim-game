import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

st.set_page_config(page_title="הגמד והענק - פורים", layout="centered")

# חיבור לגוגל שיטס (חובה להגדיר Secrets כפי שהסברתי קודם)
conn = st.connection("gsheets", type=GSheetsConnection)

def perform_lottery(df):
    names = df['Name'].tolist()
    shuffled = names.copy()
    # אלגוריתם שמוודא שאף אחד לא מגריל את עצמו
    while any(names[i] == shuffled[i] for i in range(len(names))):
        random.shuffle(shuffled)
    df['Target'] = shuffled
    return df

menu = st.sidebar.selectbox("תפריט", ["כניסת עובדים", "ניהול (HR)"])

if menu == "ניהול (HR)":
    st.title("ניהול משאבי אנוש 🎭")
    admin_pw = st.text_input("הזיני סיסמת מנהלת", type="password")
    
    if admin_pw == "פורים2026": # שנה לסיסמה שתבחר
        st.write("כאן תוכלי להפעיל את ההגרלה לכל 100 העובדים בלחיצת כפתור.")
        if st.button("בצע הגרלה ושמור תוצאות"):
            try:
                # קריאת נתונים (שמות ומספרי עובד)
                df = conn.read(ttl=0)
                if 'Name' in df.columns and 'ID' in df.columns:
                    df_results = perform_lottery(df)
                    # עדכון הגיליון עם התוצאות בעמודת Target
                    conn.update(data=df_results)
                    st.success("ההגרלה בוצעה! התוצאות נשמרו בגיליון בצורה מאובטחת.")
                else:
                    st.error("שגיאה: וודאי שיש עמודות בשם 'Name' ו-'ID' בגיליון.")
            except Exception as e:
                st.error(f"שגיאה טכנית: {e}")

elif menu == "כניסת עובדים":
    st.title("🎈 משחק הגמד והענק")
    
    try:
        # טעינת נתונים טריים מהגיליון
        data = conn.read(ttl=0)
        
        if 'Target' not in data.columns or data['Target'].isnull().all():
            st.warning("ההגרלה טרם בוצעה. הודעה תישלח לכולם כשהמשחק יתחיל!")
        else:
            # 1. בחירת שם מרשימה
            names_list = sorted(data['Name'].tolist())
            selected_user = st.selectbox("בחר/י את שמך מהרשימה:", [""] + names_list)
            
            if selected_user:
                # 2. הזנת מספר עובד (סיסמה)
                emp_id = st.text_input("הזינו מספר עובד לזיהוי:", type="password")
                
                if st.button("סובב את הגלגל! 🎡"):
                    # בדיקה האם ה-ID תואם לשם בגיליון
                    actual_id = str(data[data['Name'] == selected_user]['ID'].values[0])
                    
                    if str(emp_id) == actual_id:
                        # אנימציית הגרלה
                        with st.empty():
                            for _ in range(12):
                                st.write(f"🎰 מחפש את הענק שלך... {random.choice(names_list)}")
                                time.sleep(0.1)
                        
                        # חשיפת התוצאה
                        target = data[data['Name'] == selected_user]['Target'].values[0]
                        st.balloons()
                        st.markdown(f"### הענק שלך הוא/היא: **{target}**")
                        st.info("זכור/י: לשמור על סודיות מוחלטת! 🤫")
                    else:
                        st.error("מספר עובד שגוי. אנא נסו שוב או פנו ל-HR.")
  except Exception as e:
        st.error(f"שגיאה טכנית: {e}")
