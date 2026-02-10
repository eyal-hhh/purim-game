import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

st.set_page_config(page_title="הגמד והענק - פורים", layout="centered")

# חיבור לגוגל שיטס
conn = st.connection("gsheets", type=GSheetsConnection)

def perform_lottery(df):
    names = df['Name'].tolist()
    shuffled = names.copy()
    while any(names[i] == shuffled[i] for i in range(len(names))):
        random.shuffle(shuffled)
    df['Target'] = shuffled
    return df

menu = st.sidebar.selectbox("תפריט", ["כניסת עובדים", "ניהול (HR)"])

if menu == "ניהול (HR)":
    st.title("ניהול משאבי אנוש 🎭")
    admin_pw = st.text_input("הזיני סיסמת מנהלת", type="password")
    
    if admin_pw == "פורים2026":
        st.info("כאן מפעילים את ההגרלה פעם אחת בלבד.")
        if st.button("בצע הגרלה ושמור תוצאות בגיליון"):
            try:
                df = conn.read(ttl=0)
                if 'Name' in df.columns and 'ID' in df.columns:
                    df_results = perform_lottery(df)
                    conn.update(data=df_results)
                    st.success("ההגרלה הסתיימה בהצלחה! התוצאות נשמרו.")
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
            names_list = sorted(data['Name'].tolist())
            selected_user = st.selectbox("בחר/י את שמך:", [""] + names_list)
            if selected_user:
                emp_id = st.text_input("הזינו מספר עובד (סיסמה):", type="password")
                if st.button("גלה/י מי הענק שלי! 🎡"):
                    actual_id = str(data[data['Name'] == selected_user]['ID'].values[0])
                    if str(emp_id) == actual_id:
                        with st.spinner("מגריל..."):
                            time.sleep(1.5)
                        target = data[data['Name'] == selected_user]['Target'].values[0]
                        st.balloons()
                        st.markdown(f"### הענק שלך הוא/היא: **{target}**")
                    else:
                        st.error("מספר עובד לא תקין. נסה/י שוב.")
    except Exception as e:
        st.error(f"שגיאה טכנית: {e}")
        st.write("פרטי תגובה מהשרת:", e)
