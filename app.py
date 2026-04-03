import streamlit as st, pandas as pd, os, datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Valsad Hub Pro", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS FOR BETTER GUI ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; border: none; }
    .stButton>button:hover { background-color: #0056b3; color: white; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; }
    [data-testid="stSidebar"] { background-color: #f1f3f5; border-right: 1px solid #dee2e6; }
    div[data-testid="stExpander"] { border: 1px solid #dee2e6; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- AUTOMATIONS ---
if not os.path.exists("backups"): os.makedirs("backups")

def save_and_backup(dataframe, filename):
    dataframe.to_excel(filename, index=False)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dataframe.to_excel(f"backups/auto_{ts}_{filename}", index=False)

# --- SIDEBAR: NAVIGATION & FILE MANAGER ---
with st.sidebar:
    st.title("⚙️ Admin Hub")
    
    st.subheader("📁 Database Selection")
    all_files = [f for f in os.listdir() if f.endswith('.xlsx')]
    if "db.xlsx" not in all_files: all_files.append("db.xlsx")
    
    selected_f = st.selectbox("Switch Active File:", all_files)
    new_f = st.text_input("✨ Create New (.xlsx):", placeholder="e.g. class10.xlsx")
    F = new_f if new_f else selected_f

    st.markdown("---")
    st.subheader("📊 System Status")
    try:
        df = pd.read_excel(F)
    except:
        df = pd.DataFrame(columns=["Sr No", "Name", "Class", "Division", "Aadhar No", "DOB", "DOB Words"])
    
    st.metric("Total Records", len(df))
    st.success("🤖 Auto-Backup: Active")
    st.success("🧼 Auto-Clean: Active")

    # --- DUPLICATE SCANNER ---
    if "Aadhar No" in df.columns and not df.empty:
        dupes = df[df.duplicated(subset=['Aadhar No'], keep=False)]
        if not dupes.empty:
            st.warning(f"🚨 {len(dupes)} Duplicates Found!")

    st.markdown("---")
    if "Aadhar No" in df.columns:
        st.subheader("🗑️ Fast Delete")
        del_val = st.text_input("Enter Aadhar No:")
        if st.button("Confirm Delete"):
            if del_val in df["Aadhar No"].astype(str).values:
                df = df[df["Aadhar No"].astype(str) != del_val]
                save_and_backup(df, F)
                st.rerun()

# --- MAIN GUI ---
st.title(f"🏫 Valsad Student Hub")
st.caption(f"Currently managing: **{F}**")

C = ["Sr No", "Name", "Class", "Division", "Aadhar No", "DOB", "DOB Words"]
if not os.path.exists(F): pd.DataFrame(columns=C).to_excel(F, index=False)

def gb(d):
    n=str.maketrans('0123456789','૦૧૨૩૪૫૬૭૮૯')
    m=["","જાન્યુઆરી","ફેબ્રુઆરી","માર્ચ","એપ્રિલ","મે","જૂન","જુલાઈ","ઓગસ્ટ","સપ્ટેમ્બર","ઓક્ટોબર","નવેમ્બર","ડિસેમ્બર"]
    return f"{str(d.day).translate(n)} {m[d.month]} {str(d.year).translate(n)}"

# --- TABS ---
t1, t2, t3, t4, t5 = st.tabs(["📝 Add Student", "📂 Bulk Import", "🔎 Quick Search", "📊 Analytics", "🛠️ Advanced Edit"])

with t1:
    st.subheader("Student Registration Form")
    if all(col in df.columns for col in C):
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                s = st.number_input("Serial Number", min_value=1)
                n = st.text_input("Full Name (Auto-Formatting)")
                c = st.selectbox("Current Class", ["૧", "૨","૩","૪","૫","૬","૭","૮","૯","૧૦","૧૧","૧૨","Other"])
            with col2:
                a = st.text_input("Aadhar Card No", max_chars=12)
                d = st.selectbox("Division/Section", ["અ ", "બ " ])
                db = st.date_input("Date of Birth", min_value=datetime.date(2000,1,1))
            
            if st.button("📥 Save to Database"):
                n_clean = n.strip().title()
                if n_clean and len(a)==12 and a not in df["Aadhar No"].astype(str).values:
                    df.loc[len(df)] = [s, n_clean, c, d, a, db, gb(db)]
                    save_and_backup(df, F)
                    st.success(f"Successfully added {n_clean}!")
                    st.rerun()
                else: st.error("Check Name, Aadhar length (12), or Duplicates.")
    else: st.error("Standard columns missing in this file.")

with t2:
    st.subheader("Data Migration Tool")
    u = st.file_uploader("Upload CSV or Excel", type=['csv', 'xlsx'])
    if u and st.button(" Process Bulk Upload"):
        try:
            nd = pd.read_csv(u) if u.name.endswith('.csv') else pd.read_excel(u)
            if "Name" in nd.columns: nd["Name"] = nd["Name"].astype(str).str.title()
            df = pd.concat([df, nd]).drop_duplicates(subset=["Aadhar No"] if "Aadhar No" in nd.columns else None)
            save_and_backup(df, F)
            st.success("Bulk Data Imported!")
            st.rerun()
        except: st.error("Import failed.")

with t3:
    st.subheader("Global Search Engine")
    q = st.text_input("Type anything to filter...")
    v = df[df.astype(str).apply(lambda x: x.str.contains(q, case=False)).any(axis=1)] if q else df
    
    if "DOB" in v.columns and st.toggle("Show Age Column"):
        v['DOB'] = pd.to_datetime(v['DOB'], errors='coerce')
        tdy = pd.to_datetime(datetime.datetime.now())
        v['Age'] = v['DOB'].apply(lambda x: tdy.year - x.year - ((tdy.month, tdy.day) < (x.month, x.day)) if pd.notnull(x) else None)
    
    st.dataframe(v, use_container_width=True, hide_index=True)
    st.download_button("📂 Export Results (CSV)", v.to_csv(index=False).encode('utf-8-sig'), f"export_{F}.csv")

with t4:
    st.subheader("Data Insights")
    if not df.empty:
        col_a, col_b = st.columns(2)
        if "Class" in df.columns: col_a.bar_chart(df["Class"].value_counts())
        if "Division" in df.columns: col_b.bar_chart(df["Division"].value_counts())
    else: st.info("No data available.")

with t5:
    st.subheader("Live Grid Editor")
    e_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("✅ Apply All Changes"):
        save_and_backup(e_df, F)
        st.success("Database Updated!")
        st.rerun()
