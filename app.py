import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# הגדרות עמוד
st.set_page_config(page_title="הגמד והענק - פורים 2026", layout="centered", page_icon="🎭")

# חיבור לגוגל שיטס (משתמש ב-Secrets שהגדרת)
conn = st.connection("gsheets", type=GSheetsConnection)

def perform_lottery(df):
    """מבצע הגרלה מוודא שאף אחד לא מגריל את עצמו"""
    # ניקוי שורות ריקות אם יש
    df = df.dropna(subset=['Name', 'ID']).copy()
    names = df['Name'].tolist()
    shuffled = names.copy()
    
    # הגרלה עד שאף אחד לא מקבל את עצמו
    attempts = 0
    while any(names[i] == shuffled[i] for i in range(len(names))) and attempts < 100:
        random.shuffle(shuffled)
        attempts += 1
        
    df['Target'] = shuffled
    return df

# תפריט ניווט בצד
menu = st.sidebar.selectbox("לאן תרצה ללכת?", ["כניסת עובדים", "ניהול (HR)"])

if menu == "ניהול (HR)":
    st.title("ניהול משאבי אנוש 🎭")
    st.write("כאן מבצעים את ההגרלה הגדולה של פורים.")
    
    admin_pw = st.text_input("הזיני סיסמת מנהלת", type="password")
    
    if admin_pw == "פורים2026":
        st.success("גישה אושרה.")
        if st.button("🎰 בצע הגרלה ושמור תוצאות בגיליון"):
            try:
                with st.spinner("מבצע הגרלה ל-100 עובדים..."):
                    df = conn.read(ttl=0)
                    if 'Name' in df.columns and 'ID' in df.columns:
                        df_results = perform_lottery(df)
                        conn.update(data=df_results)
                        st.success("ההגרלה הסתיימה בהצלחה! כל העובדים שובצו.")
                    else:
                        st.error("שגיאה במבנה הגיליון: וודאו שיש עמודות Name ו-ID.")
            except Exception as e:
                st.error(f"תקלה בניהול: {e}")
    elif admin_pw:
        st.error("סיסמה שגויה.")

elif menu == "כניסת עובדים":
    st.title("🎈 משחק הגמד והענק - פורים")
    
    try:
        # קריאת הנתונים מהגיליון
        data = conn.read(ttl=0)
        
        # בדיקה אם ההגרלה כבר בוצעה (אם יש נתונים בעמודת Target)
        if 'Target' not in data.columns or data['Target'].isnull().all():
            st.warning("ההגרלה טרם בוצעה על ידי משאבי אנוש. נא להמתין לעדכון.")
        else:
            # רשימת שמות העובדים לבחירה
            names_list = sorted(data['Name'].dropna().unique().tolist())
            selected_user = st.selectbox("בחר/י את שמך מהרשימה:", [""] + names_list)
            
            if selected_user:
                emp_id = st.text_input("הזינו מספר עובד (הסיסמה האישית):", type="password")
                
                if st.button("🎡 גלה/י מי הענק שלי!"):
                    # שליפת השורה של העובד
                    user_row = data[data['Name'] == selected_user].iloc[0]
                    actual_id = str(user_row['ID'])
                    
                    # בדיקת סיסמה
                    if str(emp_id) == actual_id:
                        with st.spinner("בודק במגילות הפורים..."):
                            time.sleep(1.5)
                        
                        target = user_row['Target']
                        st.balloons()
                        st.markdown(f"### הגמד/ה היקר/ה!")
                        st.markdown(f"## הענק שלך הוא/היא: **{target}**")
                        st.info("זכרו: שמרו על הסוד עד לחג! 🤫")
                    else:
                        st.error("מספר עובד לא תקין. נסו שוב.")
                        
    except Exception as e:
        st.error("חלה שגיאה בטעינת הנתונים.")
        st.write(f"פרטים טכניים: {e}")
