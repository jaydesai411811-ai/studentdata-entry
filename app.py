import streamlit as st, pandas as pd, os
st.set_page_config(layout="wide")
F, C = "db.xlsx", ["Sr","Name","Class","Div","Aadhar","DOB","Words"]
if not os.path.exists(F): pd.DataFrame(columns=C).to_excel(F, index=False)

def gb(d):
 n=str.maketrans('0123456789','૦૧૨૩૪૫૬૭૮૯')
 m=["","જાન્યુઆરી","ફેબ્રુઆરી","માર્ચ","એપ્રિલ","મે","જૂન","જુલાઈ","ઓગસ્ટ","સપ્ટેમ્બર","ઓક્ટોબર","નવેમ્બર","ડિસેમ્બર"]
 return f"{str(d.day).translate(n)} {m[d.month]} {str(d.year).translate(n)}"

df=pd.read_excel(F)

# Sidebar (Stats & Delete)
st.sidebar.metric("Total Students", len(df))
x=st.sidebar.text_input("🗑️ Delete by Aadhar:")
if st.sidebar.button("Delete") and x in df["Aadhar"].astype(str).values:
 df=df[df["Aadhar"].astype(str)!=x]; df.to_excel(F, index=False); st.rerun()

st.title("🎓 Student Hub")
c1, c2 = st.columns([1, 2])

# Left Side (Data Entry + Validation)
with c1.container(border=True):
 with st.form("f", clear_on_submit=True):
  s, n = st.number_input("Sr", 1), st.text_input("Name")
  c, d = st.selectbox("Class",["11","12"]), st.selectbox("Div",["A","B"])
  a, db = st.text_input("Aadhar (12 num)", max_chars=12), st.date_input("DOB")
  
  if st.form_submit_button("Save"):
   if n and len(a)==12 and a not in df["Aadhar"].astype(str).values:
    df.loc[len(df)]=[s,n,c,d,a,db,gb(db)]; df.to_excel(F, index=False); st.rerun()
   else: st.error("Name required & Aadhar must be 12 unique digits!")

# Right Side (Search & Download)
with c2.container(border=True):
 q=st.text_input("🔍 Search Name:")
 v=df[df["Name"].astype(str).str.contains(q, case=False)] if q else df
 st.dataframe(v, use_container_width=True, hide_index=True)
 st.download_button("📥 Export CSV", v.to_csv(index=False).encode('utf-8-sig'), "data.csv")
