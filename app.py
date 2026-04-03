import streamlit as st,pandas as pd,os
F,C="d.xlsx",["Sr","Name","Class","Div","Aadhar","DOB","W"]
if not os.path.exists(F):pd.DataFrame(columns=C).to_excel(F,index=False)
def gb(d):
 n=str.maketrans('0123456789','૦૧૨૩૪૫૬૭૮૯')
 m=" જાન્યુઆરી ફેબ્રુઆરી માર્ચ એપ્રિલ મે જૂન જુલાઈ ઓગસ્ટ સપ્ટેમ્બર ઓક્ટોબર નવેમ્બર ડિસેમ્બર".split()
 return f"{str(d.day).translate(n)} {m[d.month]} {str(d.year).translate(n)}"
df=pd.read_excel(F)
st.sidebar.metric("Total",len(df))
t1,t2,t3=st.tabs(["Add","Import","Edit"])
with t1:
 with st.form("f"):
  s,n=st.number_input("Sr",1),st.text_input("Name")
  c,d=st.selectbox("Class",[11,12]),st.selectbox("Div",["A","B"])
  a,db=st.text_input("Aadhar"),st.date_input("DOB")
  if st.form_submit_button("Save"):df.loc[len(df)]=[s,n,c,d,a,db,gb(db)];df.to_excel(F,index=False);st.rerun()
with t2:
 u=st.file_uploader("File",type=['csv','xlsx'])
 if u and st.button("Load"):pd.concat([df,pd.read_csv(u) if '.csv' in u.name else pd.read_excel(u)]).drop_duplicates("Aadhar").to_excel(F,index=False);st.rerun()
with t3:
 e=st.data_editor(df,num_rows="dynamic")
 if st.button("Save Edits"):e.to_excel(F,index=False);st.rerun()
