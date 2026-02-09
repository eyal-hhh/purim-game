import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# הגדרות דף
st.set_page_config(page_title="הגמד והענק - פורים", layout="centered")

# חיבור לגוגל שיטס
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(worksheet="Sheet1")

def save_data(df):
    conn.update(worksheet="Sheet1", data=df)

# פונקציה לביצוע ההגרלה
def perform_lottery(names):
    shuffled = names.copy()
    while any(names[i] == shuffled[i] for i in range(len(names))):
        random.shuffle(shuffled)
    return dict(zip(names, shuffled))

# תפריט
menu = st.sidebar.selectbox("תפריט", ["דף הגרלה", "ניהול (HR)"])

if menu == "ניהול (HR)":
    st.title("ניהול משאבי אנוש 🎭")
    password = st.text_input("הזיני סיסמה", type="password")
    
    if password == "פורים2024":
        url = st.text_input("הדביקי כאן את לינק ה-Google Sheets שלך:")
        
        if st.button("טען רשימת עובדים ובצע הגרלה"):
            try:
                # קריאת הנתונים מהלינק
                df_names = conn.read(spreadsheet=url)
                names_list = df_names.iloc[:, 0].tolist()
                
                # ביצוע הגרלה
                assignments = perform_lottery(names_list)
                
                # יצירת טבלה חדשה לשמירה
                results_df = pd.DataFrame(list(assignments.items()), columns=["Gamad", "Anak"])
                
                # שמירה חזרה לגיליון
                conn.update(spreadsheet=url, data=results_df)
                st.success("ההגרלה בוצעה והנתונים נשמרו בגוגל שיטס!")
                st.dataframe(results_df)
            except Exception as e:
                st.error(f"שגיאה בחיבור לגיליון: {e}")
    else:
        st.warning("סיסמה שגויה")

elif menu == "דף הגרלה":
    st.title("🎈 משחק הגמד והענק - פורים")
    
    sheet_url = st.text_input("הזינו את קישור המשחק (יסופק ע''י HR):", type="password")
    
    if sheet_url:
        try:
            data = conn.read(spreadsheet=sheet_url)
            names_list = data["Gamad"].tolist()
            
            user_name = st.selectbox("מי את/ה?", ["בחר שם..."] + names_list)
            
            if user_name != "בחר שם...":
                if st.button("סובב את הגלגל! 🎡"):
                    with st.empty():
                        for i in range(10):
                            st.write(f"🎰 מגריל... {random.choice(names_list)}")
                            time.sleep(0.1)
                        
                        target = data[data["Gamad"] == user_name]["Anak"].values[0]
                        st.balloons()
                        st.success(f"הענק שלך הוא/היא: **{target}**")
                        st.info("אל תשכח/י - לשמור בסוד! 🤫")
        except:
            st.error("לא ניתן לטעון את נתוני ההגרלה. וודאו שהקישור תקין.")