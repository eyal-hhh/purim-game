import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("בדיקת תשתית סופית 🔍")

try:
    # בדיקת קיום ה-Secrets
    st.write("1. בודק הגדרות סודיות (Secrets)...")
    conf = st.secrets["connections"]["gsheets"]
    st.write(f"✅ נמצא מפתח עבור: `{conf['client_email']}`")

    # ניסיון התחברות
    st.write("2. מנסה לפתוח את הצינור לגוגל...")
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # ניסיון קריאה
    st.write("3. מנסה לקרוא נתונים מהגיליון...")
    df = conn.read(ttl=0)
    
    st.success("✅ הצלחתי! החיבור תקין לגמרי.")
    st.write("הנה השורות הראשונות שמצאתי:")
    st.dataframe(df.head())

except Exception as e:
    st.error("❌ החיבור נכשל")
    st.markdown("### הנה השגיאה האמיתית שגוגל מחזירה:")
    st.code(str(e))
    
    if "PermissionError" in str(e) or "403" in str(e):
        st.warning("⚠️ אבחנה: גוגל מזהה את המפתח, אבל לא נותנת לו להיכנס לגיליון.")
    elif "SpreadsheetNotFound" in str(e) or "404" in str(e):
        st.warning("⚠️ אבחנה: הקישור (URL) ב-Secrets כנראה לא מוביל לשום מקום.")
