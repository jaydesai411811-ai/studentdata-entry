import streamlit as st, pandas as pd, os

st.set_page_config(page_title="Valsad Hub", layout="wide")

# --- NEW: UNIVERSAL FILE MANAGER ---
st.sidebar.title("📁 File Manager")
all_files = [f for f in os.listdir() if f.endswith('.xlsx')]
if "db.xlsx" not in all_files: all_files.append("db.xlsx")

# Dropdown to select file, or text input to create a new one
new_f = st.sidebar.text_input("Create new file (e.g. data.xlsx):")
F = new_f if new_f else st.sidebar.selectbox("Active Database:", all_files)

C = ["Sr","Name","Class","Div","Aadhar","DOB","Words"]
if not os.path.exists(F): pd.DataFrame(columns=C).to_excel(F, index=False)
# -----------------------------------

def gb(d):
 n=str.maketrans('0123456789','૦૧૨૩૪૫૬૭૮૯')
 m=["","જાન્યુઆરી","ફેબ્રુઆરી","માર્ચ","એપ્રિલ","મે","જૂન","જુલાઈ","ઓગસ્ટ","સપ્ટેમ્બર","ઓક્ટોબર","નવેમ્બર","ડિસેમ્બર"]
 return f"{str(d.day).translate(n)} {m[d.month]} {str(d.year).translate(n)}"

df = pd.read_excel(F)

# Sidebar: Stats & Admin Controls
st.sidebar.markdown("---")
st.sidebar.title("⚙️ Admin Controls")
st.sidebar.metric("Total Records", len(df))
st.sidebar.markdown("---")
st.sidebar.subheader("🗑️ Delete Record")

# Adapts to whether the file actually has an Aadhar column
if "Aadhar" in df.columns:
    del_val = st.sidebar.text_input("Enter Aadhar to delete:")
    if st.sidebar.button("Delete") and del_val in df["Aadhar"].astype(str).values:
        df = df[df["Aadhar"].astype(str) != del_val]; df.to_excel(F, index=False); st.rerun()
else:
    st.sidebar.info("Aadhar deletion is not applicable for this file.")

st.title(f"🎓 Student Hub - [{F}]")

# Organized Tabs
t1, t2, t3, t4, t5 = st.tabs(["📝 Manual Entry", "📥 Bulk Import", "🔍 Search & Export", "📊 Analytics", "✏️ Live Edit"])

# TAB 1: Manual Entry
with t1:
    # Only allow form entry if it is the official student database format
    if all(col in df.columns for col in C):
        with st.form("f", clear_on_submit=True):
            col1, col2 = st.columns(2)
            s, n = col1.number_input("Sr", min_value=1), col2.text_input("Name")
            c, d = col1.selectbox("Class", ["11", "12"]), col2.selectbox("Div", ["A", "B", "C"])
            a, db = col1.text_input("Aadhar (12 num)", max_chars=12), col2.date_input("DOB")
            if st.form_submit_button("Save Record"):
                if n and len(a)==12 and a not in df["Aadhar"].astype(str).values:
                    df.loc[len(df)] = [s,n,c,d,a,db,gb(db)]; df.to_excel(F, index=False); st.success("Saved!"); st.rerun()
                else: st.error("Invalid entry or Aadhar already exists.")
    else:
        st.warning(f"Manual Entry disabled. '{F}' does not have the standard student columns. Use 'Live Edit' instead.")

# TAB 2: Bulk Import Feature
with t2:
    st.subheader(f"Import Data into {F}")
    uploaded_file = st.file_uploader("Upload File", type=['csv', 'xlsx'])
    if uploaded_file and st.button("Import Data"):
        try:
            new_data = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            if "Aadhar" in df.columns and "Aadhar" in new_data.columns:
                existing_aadhars = df["Aadhar"].astype(str).tolist()
                new_data = new_data[~new_data["Aadhar"].astype(str).isin(existing_aadhars)] # Prevent duplicates
            if not new_data.empty:
                df = pd.concat([df, new_data]); df.to_excel(F, index=False); st.success(f"Imported {len(new_data)} records!"); st.rerun()
            else: st.warning("No new records added.")
        except: st.error("Error reading file.")

# TAB 3: Search & Export
with t3:
    q = st.text_input("🔍 Search Database:")
    # Upgraded to search ALL columns dynamically based on the file loaded
    if q:
        mask = df.astype(str).apply(lambda col: col.str.contains(q, case=False)).any(axis=1)
        v = df[mask]
    else:
        v = df
    st.dataframe(v, use_container_width=True, hide_index=True)
    st.download_button("📥 Export View to CSV", v.to_csv(index=False).encode('utf-8-sig'), f"export_{F.replace('.xlsx', '.csv')}")

# TAB 4: Visual Analytics
with t4:
    st.subheader("Distribution")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1: 
            if "Class" in df.columns: st.write("**By Class**"); st.bar_chart(df["Class"].value_counts())
            else: st.write("No 'Class' data to analyze.")
        with c2: 
            if "Div" in df.columns: st.write("**By Division**"); st.bar_chart(df["Div"].value_counts())
            else: st.write("No 'Div' data to analyze.")
    else: st.write("No data available yet.")

# TAB 5: Live Edit Feature
with t5:
    st.subheader(f"Live Editing: {F}")
    e_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("Save All Edits"):
        e_df.to_excel(F, index=False)
        st.success(f"Edits to {F} saved successfully!")
        st.rerun()
