import streamlit as st, pandas as pd, os

st.set_page_config(page_title="Valsad Hub", layout="wide")
F, C = "db.xlsx", ["Sr","Name","Class","Div","Aadhar","DOB","Words"]
if not os.path.exists(F): pd.DataFrame(columns=C).to_excel(F, index=False)

def gb(d):
 n=str.maketrans('0123456789','૦૧૨૩૪૫૬૭૮૯')
 m=["","જાન્યુઆરી","ફેબ્રુઆરી","માર્ચ","એપ્રિલ","મે","જૂન","જુલાઈ","ઓગસ્ટ","સપ્ટેમ્બર","ઓક્ટોબર","નવેમ્બર","ડિસેમ્બર"]
 return f"{str(d.day).translate(n)} {m[d.month]} {str(d.year).translate(n)}"

df = pd.read_excel(F)

# Sidebar: Stats & Admin Controls
st.sidebar.title("⚙️ Admin Controls")
st.sidebar.metric("Total Students", len(df))
st.sidebar.markdown("---")
st.sidebar.subheader("🗑️ Delete Record")
del_val = st.sidebar.text_input("Enter Aadhar to delete:")
if st.sidebar.button("Delete") and del_val in df["Aadhar"].astype(str).values:
    df = df[df["Aadhar"].astype(str) != del_val]; df.to_excel(F, index=False); st.rerun()

st.title("🎓 Student Hub - Pro Version")

# Organized Tabs
# Organized Tabs
t1, t2, t3, t4, t5 = st.tabs(["📝 Manual Entry", "📥 Bulk Import", "🔍 Search & Export", "📊 Analytics", "✏️ Live Edit"])
# TAB 1: Manual Entry
with t1:
    with st.form("f", clear_on_submit=True):
        col1, col2 = st.columns(2)
        s, n = col1.number_input("Sr", min_value=1), col2.text_input("Name")
        c, d = col1.selectbox("Class", ["11", "12"]), col2.selectbox("Div", ["A", "B", "C"])
        a, db = col1.text_input("Aadhar (12 num)", max_chars=12), col2.date_input("DOB")
        if st.form_submit_button("Save Record"):
            if n and len(a)==12 and a not in df["Aadhar"].astype(str).values:
                df.loc[len(df)] = [s,n,c,d,a,db,gb(db)]; df.to_excel(F, index=False); st.success("Saved!"); st.rerun()
            else: st.error("Invalid entry or Aadhar already exists.")

# TAB 2: Bulk Import Feature
with t2:
    st.subheader("Import Excel or CSV")
    st.info(f"⚠️ Your file must have these exact column names: {', '.join(C)}")
    uploaded_file = st.file_uploader("Upload File", type=['csv', 'xlsx'])
    if uploaded_file and st.button("Import Data"):
        try:
            new_data = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            existing_aadhars = df["Aadhar"].astype(str).tolist()
            new_data = new_data[~new_data["Aadhar"].astype(str).isin(existing_aadhars)] # Prevent duplicates
            if not new_data.empty:
                df = pd.concat([df, new_data]); df.to_excel(F, index=False); st.success(f"Imported {len(new_data)} records!"); st.rerun()
            else: st.warning("No new records added. All Aadhars might already exist.")
        except: st.error("Error reading file. Ensure column names match exactly!")

# TAB 3: Search & Export
with t3:
    q = st.text_input("🔍 Search by Name or Aadhar:")
    v = df[df["Name"].astype(str).str.contains(q, case=False) | df["Aadhar"].astype(str).str.contains(q)] if q else df
    st.dataframe(v, use_container_width=True, hide_index=True)
    st.download_button("📥 Export View to CSV", v.to_csv(index=False).encode('utf-8-sig'), "export.csv")

# TAB 4: Visual Analytics
with t4:
    st.subheader("Student Distribution")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1: st.write("**By Class**"); st.bar_chart(df["Class"].value_counts())
        with c2: st.write("**By Division**"); st.bar_chart(df["Div"].value_counts())
    else: st.write("No data available yet.")

# TAB 5: Live Edit Feature
with t5:
    st.subheader("Edit Data Directly")
    e_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("Save All Edits"):
        e_df.to_excel(F, index=False)
        st.success("Edits saved successfully!")
        st.rerun()
