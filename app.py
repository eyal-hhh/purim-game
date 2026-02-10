import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

st.set_page_config(page_title="הגמד והענק - פורים", layout="centered")

# ניסיון חיבור
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"שגיאה בהגדרת החיבור: {e}")

def perform_lottery(df):
    names = df['Name'].dropna().tolist()
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
        if st.button("בצע הגרלה"):
            try:
                df = conn.read(ttl=0)
                df_results = perform_lottery(df)
                conn.update(data=df_results)
                st.success("ההגרלה הסתיימה בהצלחה!")
            except Exception as e:
                st.error(f"תקלה בניהול: {e}")

elif menu == "כניסת עובדים":
    st.title("🎈 משחק הגמד והענק")
    try:
        data = conn.read(ttl=0)
        if 'Target' not in data.columns:
            st.warning("ההגרלה טרם בוצעה.")
        else:
            names = sorted(data['Name'].dropna().tolist())
            user = st.selectbox("בחר/י שם:", [""] + names)
            if user:
                pwd = st.text_input("מספר עובד:", type="password")
                if st.button("גלה/י מי הענק שלי"):
                    row = data[data['Name'] == user].iloc[0]
                    if str(pwd) == str(row['ID']):
                        st.balloons()
                        st.markdown(f"### הענק שלך: **{row['Target']}**")
                    else:
                        st.error("מספר עובד לא תקין.")
    except Exception as e:
        st.error(f"שגיאה בגישה לנתונים: {e}")
