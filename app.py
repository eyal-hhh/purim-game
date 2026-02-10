import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("בדיקת חיבור לנתונים 🔍")

try:
    # שליפת המייל מה-Secrets כדי שנוכל לראות אותו
    email = st.secrets["connections"]["gsheets"]["client_email"]
    st.write(f"האפליקציה מנסה להתחבר עם המייל: `{email}`")
    st.info("וודא שהמייל הזה מופיע ב-'שיתוף' של הגיליון כ-Editor.")

    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
    st.success("החיבור הצליח! הנה הנתונים:")
    st.dataframe(df)

except Exception as e:
    st.error(f"עדיין יש תקלה: {e}")
