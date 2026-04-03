import streamlit as st, pandas as pd, os, datetime

st.set_page_config(page_title="N M Wadia Tata-Wadia High School Nargol Hub", layout="wide")

# --- AUTOMATION 1: AUTO-BACKUP ENGINE ---
if not os.path.exists("backups"): os.makedirs("backups")

def save_and_backup(dataframe, filename):
    dataframe.to_excel(filename, index=False)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dataframe.to_excel(f"backups/auto_{ts}_{filename}", index=False)

# --- UNIVERSAL FILE MANAGER ---
st.sidebar.title("📁 File Manager")
all_files = [f for f in os.listdir() if f.endswith('.xlsx')]
if "db.xlsx" not in all_files: all_files.append("db.xlsx")

new_f = st.sidebar.text_input("Create new file (e.g. data.xlsx):")
F = new_f if new_f else st.sidebar.selectbox("Active Database:", all_files)

# UPDATED COLUMN NAMES
C = ["Sr No", "Name", "Class", "Division", "Aadhar No", "DOB", "DOB Words"]
if not os.path.exists(F): pd.DataFrame(columns=C).to_excel(F, index=False)

def gb(d):
 n=str.maketrans('0123456789','૦૧૨૩૪૫૬૭૮૯')
 m=["","જાન્યુઆરી","ફેબ્રુઆરી","માર્ચ","એપ્રિલ","મે","જૂન","જુલાઈ","ઓગસ્ટ","સપ્ટેમ્બર","ઓક્ટોબર","નવેમ્બર","ડિસેમ્બર"]
 return f"{str(d.day).translate(n)} {m[d.month]} {str(d.year).translate(n)}"

df = pd.read_excel(F)

# Sidebar: Stats & Admin Controls
st.sidebar.markdown("---")
st.sidebar.title("⚙️ Admin Controls")
st.sidebar.metric("Total Records", len(df))
st.sidebar.success("🤖 Automations: Active") 

# --- AUTO-DUPLICATE SCANNER (Updated for Aadhar No) ---
if "Aadhar No" in df.columns and not df.empty:
    dupes = df[df.duplicated(subset=['Aadhar No'], keep=False)]
    if not dupes.empty:
        st.sidebar.warning(f"⚠️ Warning: {len(dupes)} duplicate Aadhar entries detected!")

st.sidebar.markdown("---")
st.sidebar.subheader("🗑️ Delete Record")

if "Aadhar No" in df.columns:
    del_val = st.sidebar.text_input("Enter Aadhar No to delete:")
    if st.sidebar.button("Delete") and del_val in df["Aadhar No"].astype(str).values:
        df = df[df["Aadhar No"].astype(str) != del_val]
        save_and_backup(df, F)
        st.rerun()
else:
    st.sidebar.info("Aadhar deletion is not applicable for this file.")

st.title(f"🎓 Student Hub - [{F}]")

# Organized Tabs
t1, t2, t3, t4, t5 = st.tabs(["📝 Manual Entry", "📥 Bulk Import", "🔍 Search & Export", "📊 Analytics", "✏️ Live Edit"])

# TAB 1: Manual Entry (Updated Columns)
with t1:
    if all(col in df.columns for col in C):
        with st.form("f", clear_on_submit=True):
            col1, col2 = st.columns(2)
            s, n = col1.number_input("Sr No", min_value=1), col2.text_input("Name")
            c, d = col1.selectbox("Class", ["11", "12"]), col2.selectbox("Division", ["A", "B", "C"])
            a, db = col1.text_input("Aadhar No (12 num)", max_chars=12), col2.date_input("DOB")
            if st.form_submit_button("Save Record"):
                n_clean = n.strip().title() if n else n
                if n_clean and len(a)==12 and a not in df["Aadhar No"].astype(str).values:
                    df.loc[len(df)] = [s,n_clean,c,d,a,db,gb(db)]
                    save_and_backup(df, F)
                    st.success("Saved!")
                    st.rerun()
                else: st.error("Invalid entry or Aadhar No already exists.")
    else:
        st.warning(f"Manual Entry disabled. '{F}' missing standard columns.")

# TAB 2: Bulk Import
with t2:
    st.subheader(f"Import Data into {F}")
    uploaded_file = st.file_uploader("Upload File", type=['csv', 'xlsx'])
    if uploaded_file and st.button("Import Data"):
        try:
            new_data = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            if "Name" in new_data.columns:
                new_data["Name"] = new_data["Name"].astype(str).str.strip().str.title()
            if "Aadhar No" in df.columns and "Aadhar No" in new_data.columns:
                existing_aadhars = df["Aadhar No"].astype(str).tolist()
                new_data = new_data[~new_data["Aadhar No"].astype(str).isin(existing_aadhars)]
            if not new_data.empty:
                df = pd.concat([df, new_data])
                save_and_backup(df, F)
                st.success(f"Imported {len(new_data)} records!")
                st.rerun()
            else: st.warning("No new records added.")
        except: st.error("Error reading file.")

# TAB 3: Search & Export (Updated for DOB)
with t3:
    q = st.text_input("🔍 Search Database:")
    if q:
        mask = df.astype(str).apply(lambda col: col.str.contains(q, case=False)).any(axis=1)
        v = df[mask]
    else:
        v = df.copy() 
        
    if "DOB" in v.columns and st.checkbox("🤖 Auto-Calculate Current Age"):
        v['DOB'] = pd.to_datetime(v['DOB'], errors='coerce')
        today = pd.to_datetime(datetime.datetime.now())
        v['Auto-Age'] = v['DOB'].apply(lambda x: today.year - x.year - ((today.month, today.day) < (x.month, x.day)) if pd.notnull(x) else None)
        
    st.dataframe(v, use_container_width=True, hide_index=True)
    st.download_button("📥 Export CSV", v.to_csv(index=False).encode('utf-8-sig'), f"export_{F}.csv")

# TAB 4: Visual Analytics (Updated for Division)
with t4:
    st.subheader("Distribution")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1: 
            if "Class" in df.columns: st.write("**By Class**"); st.bar_chart(df["Class"].value_counts())
        with c2: 
            if "Division" in df.columns: st.write("**By Division**"); st.bar_chart(df["Division"].value_counts())
    else: st.write("No data available yet.")

# TAB 5: Live Edit Feature
with t5:
    st.subheader(f"Live Editing: {F}")
    e_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("Save All Edits"):
        save_and_backup(e_df, F)
        st.success(f"Edits to {F} saved successfully!")
        st.rerun()
