import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

st.set_page_config(page_title="הגמד והענק - פורים", layout="centered")

# חיבור למערכת הנתונים
conn = st.connection("gsheets", type=GSheetsConnection)

def perform_lottery(df):
    names = df['Name'].dropna().tolist()
    shuffled = names.copy()
    # וידוא שאף אחד לא מגריל את עצמו
    while any(names[i] == shuffled[i] for i in range(len(names))):
        random.shuffle(shuffled)
    
    # יצירת מילוי לעמודת ה-Target
    mapping = dict(zip(names, shuffled))
    df['Target'] = df['Name'].map(mapping)
    return df

menu = st.sidebar.selectbox("תפריט", ["כניסת עובדים", "ניהול (HR)"])

if menu == "ניהול (HR)":
    st.title("ניהול משאבי אנוש 🎭")
    admin_pw = st.text_input("הזיני סיסמת מנהלת", type="password")
    
    if admin_pw == "פורים2026":
        st.info("כאן מפעילים את ההגרלה פעם אחת בלבד עבור כל 100 העובדים.")
        if st.button("בצע הגרלה ושמור תוצאות בגיליון"):
            try:
                df = conn.read(ttl=0)
                if 'Name' in df.columns and 'ID' in df.columns:
                    df_results = perform_lottery(df)
                    conn.update(data=df_results)
                    st.success("ההגרלה הסתיימה! התוצאות נשמרו בגיליון.")
                else:
                    st.error("וודאו שיש עמודות בשם 'Name' ו-'ID' בגיליון.")
            except Exception as e:
                st.error(f"שגיאה טכנית בניהול: {e}")

elif menu == "כניסת עובדים":
    st.title("🎈 משחק הגמד והענק")
    try:
        data = conn.read(ttl=0)
        if 'Target' not in data.columns or data['Target'].isnull().all():
            st.warning("ההגרלה טרם בוצעה על ידי משאבי אנוש.")
        else:
            names_list = sorted(data['Name'].dropna().unique().tolist())
            selected_user = st.selectbox("בחר/י את שמך מהרשימה:", [""] + names_list)
            
            if selected_user:
                emp_id = st.text_input("הזינו מספר עובד (סיסמה):", type="password")
                
                if st.button("גלה/י מי הענק שלי! 🎡"):
                    user_row = data[data['Name'] == selected_user]
                    actual_id = str(user_row['ID'].values[0])
                    
                    if str(emp_id) == actual_id:
                        with st.spinner("מגריל..."):
                            time.sleep(1.2)
                        target = user_row['Target'].values[0]
                        st.balloons()
                        st.markdown(f"### הענק שלך הוא/היא: **{target}**")
                    else:
                        st.error("מספר עובד לא תקין. נסה/י שוב.")
    except Exception as e:
        st.error("חלה שגיאה בחיבור לנתונים. וודאו שהשיתוף מוגדר כראוי.")
        st.write(f"פרטים: {e}")
