import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

st.set_page_config(page_title="הגמד והענק - פורים 2026", layout="centered", page_icon="🎭")

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

menu = st.sidebar.selectbox("תפריט", ["כניסת עובדים", "ניהול (HR)"])

if menu == "ניהול (HR)":
    st.title("ניהול משאבי אנוש 🎭")
    admin_pw = st.text_input("הזיני סיסמת מנהלת", type="password")
    if admin_pw == "פורים2026":
        if st.button("🎰 בצע הגרלה"):
            try:
                df = conn.read(ttl=0)
                df_results = perform_lottery(df)
                conn.update(data=df_results)
                st.success("ההגרלה בוצעה והנתונים נשמרו!")
            except Exception as e:
                st.error(f"תקלה בניהול: {e}")

elif menu == "כניסת עובדים":
    st.title("🎈 משחק הגמד והענק")
    try:
        data = conn.read(ttl=0)
        # ניקוי נתונים: הופך הכל לטקסט ומוחק רווחים מסביב
        data['ID'] = data['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
        data['Name'] = data['Name'].astype(str).str.strip()

        if 'Target' not in data.columns or data['Target'].isnull().all():
            st.warning("ההגרלה טרם בוצעה.")
        else:
            names_list = sorted(data['Name'].tolist())
            selected_user = st.selectbox("בחר/י שם:", [""] + names_list)
            
            if selected_user:
                emp_id = st.text_input("מספר עובד:", type="password")
                if st.button("🎡 גלה/י מי הענק שלי!"):
                    # חיפוש העובד וניקוי הקלט שלו
                    user_row = data[data['Name'] == selected_user].iloc[0]
                    actual_id = user_row['ID']
                    
                    if emp_id.strip() == actual_id:
                        with st.spinner("בודק..."):
                            time.sleep(1)
                        st.balloons()
                        st.markdown(f"## הענק שלך הוא/היא: **{user_row['Target']}**")
                    else:
                        st.error("מספר עובד לא תקין.")
    except Exception as e:
        st.error(f"שגיאה: {e}")
