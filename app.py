import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

st.set_page_config(page_title="הגמד והענק - פורים", layout="centered")

# הגדרת חיבור לגוגל שיטס - משתמש ב-Secrets שהגדרת
conn = st.connection("gsheets", type=GSheetsConnection)

def perform_lottery(df):
    names = df['Name'].tolist()
    shuffled = names.copy()
    # וידוא שאף אחד לא מגריל את עצמו
    while any(names[i] == shuffled[i] for i in range(len(names))):
        random.shuffle(shuffled)
    df['Target'] = shuffled
    return df

menu = st.sidebar.selectbox("תפריט", ["כניסת עובדים", "ניהול (HR)"])

if menu == "ניהול (HR)":
    st.title("ניהול משאבי אנוש 🎭")
    admin_pw = st.text_input("הזיני סיסמת מנהלת", type="password")
    
    if admin_pw == "פורים2026":
        st.info("כאן מפעילים את ההגרלה פעם אחת בלבד עבור כל העובדים.")
        if st.button("בצע הגרלה ושמור תוצאות בגיליון"):
            try:
                # קריאת הנתונים מהגיליון
                df = conn.read(ttl=0)
                if 'Name' in df.columns and 'ID' in df.columns:
                    df_results = perform_lottery(df)
                    # עדכון הגיליון עם התוצאות
                    conn.update(data=df_results)
                    st.success("ההגרלה הסתיימה בהצלחה! התוצאות נשמרו בגיליון.")
                else:
                    st.error("שגיאת מבנה: וודאו שיש עמודות בשם 'Name' ו-'ID' בגיליון.")
            except Exception as e:
                st.error(f"שגיאה טכנית בניהול: {str(e)}")

elif menu == "כניסת עובדים":
    st.title("🎈 משחק הגמד והענק")
    
    try:
        # ניסיון לקרוא את הנתונים
        data = conn.read(ttl=0)
        
        # בדיקה אם כבר בוצעה הגרלה (אם עמודת Target קיימת ומלאה)
        if 'Target' not in data.columns or data['Target'].isnull().all():
            st.warning("ההגרלה טרם בוצעה. נא לפנות למשאבי אנוש.")
        else:
            names_list = sorted(data['Name'].tolist())
            selected_user = st.selectbox("בחר/י את שמך מהרשימה:", [""] + names_list)
            
            if selected_user:
                emp_id = st.text_input("הזינו מספר עובד לזיהוי:", type="password")
                
                if st.button("גלה/י מי הענק שלי! 🎡"):
                    # שליפת ה-ID האמיתי מהגיליון לצורך השוואה
                    user_row = data[data['Name'] == selected_user]
                    actual_id = str(user_row['ID'].values[0])
                    
                    if str(emp_id) == actual_id:
                        with st.spinner("בודק ברשימות..."):
                            time.sleep(1)
                        target = user_row['Target'].values[0]
                        st.balloons()
                        st.markdown(f"### הענק שלך הוא/היא: **{target}**")
                        st.info("זכרו: הסוד נשמר אצל הגמד!")
                    else:
                        st.error("מספר העובד אינו תואם לשם שנבחר.")
    except Exception as e:
        # כאן תפסנו את השגיאה שראית קודם - עכשיו נראה את הסיבה האמיתית
        st.error(f"לא הצלחנו להתחבר לנתונים. וודאו שה-Secrets תקינים והגיליון משותף.")
        st.write(f"פרטי תקלה למפתחים: {str(e)}")
