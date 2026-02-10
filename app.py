import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# הגדרות עמוד
st.set_page_config(page_title="הגמד והענק - פורים", layout="centered")

# חיבור לגוגל שיטס - מושך נתונים מה-Secrets שהגדרת ב-Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

def perform_lottery(df):
    """מבצע הגרלה מוודא שאף אחד לא מגריל את עצמו"""
    names = df['Name'].tolist()
    shuffled = names.copy()
    while any(names[i] == shuffled[i] for i in range(len(names))):
        random.shuffle(shuffled)
    df['Target'] = shuffled
    return df

# תפריט ניווט בצד
menu = st.sidebar.selectbox("תפריט", ["כניסת עובדים", "ניהול (HR)"])

if menu == "ניהול (HR)":
    st.title("ניהול משאבי אנוש 🎭")
    admin_pw = st.text_input("הזיני סיסמת מנהלת", type="password")
    
    # סיסמת הניהול שקבענו
    if admin_pw == "פורים2026":
        st.info("כאן מפעילים את ההגרלה פעם אחת בלבד.")
        if st.button("בצע הגרלה ושמור תוצאות בגיליון"):
            try:
                # קריאת הנתונים מהגיליון
                df = conn.read(ttl=0)
                if 'Name' in df.columns and 'ID' in df.columns:
                    df_results = perform_lottery(df)
                    # עדכון הגיליון עם עמודת ה-Target החדשה
                    conn.update(data=df_results)
                    st.success("ההגרלה הסתיימה בהצלחה! התוצאות נשמרו בגיליון.")
                    st.dataframe(df_results)
                else:
                    st.error("שגיאה: וודאו שיש עמודות בשם 'Name' ו-'ID' בגיליון.")
            except Exception as e:
                st.error(f"שגיאה טכנית בניהול: {str(e)}")
    elif admin_pw:
        st.error("סיסמה שגויה")

elif menu == "כניסת עובדים":
    st.title("🎈 משחק הגמד והענק")
    
    try:
        # טעינת הנתונים מהגיליון
        data = conn.read(ttl=0)
        
        # בדיקה אם ההגרלה כבר בוצעה
        if 'Target' not in data.columns or data['Target'].isnull().all():
            st.warning("ההגרלה טרם בוצעה על ידי משאבי אנוש. נא לחזור מאוחר יותר.")
        else:
            # יצירת רשימת שמות מסודרת
            names_list = sorted(data['Name'].dropna().unique().tolist())
            selected_user = st.selectbox("בחר/י את שמך מהרשימה:", [""] + names_list)
            
            if selected_user:
                emp_id = st.text_input("הזינו מספר עובד לזיהוי (סיסמה):", type="password")
                
                if st.button("גלה/י מי הענק שלי! 🎡"):
                    # שליפת השורה של העובד הנבחר
                    user_data = data[data['Name'] == selected_user].iloc[0]
                    actual_id = str(user_data['ID'])
                    
                    # בדיקת התאמה בין השם למספר העובד
                    if str(emp_id) == actual_id:
                        with st.spinner("מחפש ברשימות הגמדים..."):
                            time.sleep(1.5)
                        
                        target = user_data['Target']
                        st.balloons()
                        st.markdown(f"### הענק שלך הוא/היא: **{target}**")
                        st.success("חג פורים שמח! שמרו על הסוד.")
                    else:
                        st.error("מספר העובד אינו תואם לשם שנבחר. נסו שוב.")
                        
    except Exception as e:
        st.error("חלה שגיאה בחיבור לנתונים.")
        st.info("וודאו שהגיליון משותף עם המייל של ה-Service Account ושהקישור ב-Secrets תקין.")
        st.write(f"פרטים טכניים: {str(e)}")

