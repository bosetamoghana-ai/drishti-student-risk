import streamlit as st
import pandas as pd

# =========================
# Page Config
# =========================
st.set_page_config(page_title="Project Drishti", layout="wide")

# =========================
# Custom Styling (small)
# =========================
st.markdown("""
    <style>
    .reportview-container {
        background: #f9f9f9;
    }
    .sidebar .sidebar-content {
        background: #004080;
        color: white;
    }
    h1, h2, h3 {
        color: #004080;
    }
    table {
        border-collapse: collapse;
        width: 100%;
    }
    th, td {
        padding: 6px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# Sidebar
# =========================
try:
    st.sidebar.image("logo.png", width=120)  # if logo.png not present, this won't crash
except Exception:
    st.sidebar.write("")  # ignore

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Upload Data", "About"])

# =========================
# App Title & Intro
# =========================
st.title("📊 Project Drishti – Student Success Early Warning System")
st.markdown("Helping educators move from **reactive** to **proactive** mentoring")

# =========================
# Upload Page
# =========================
if page == "Upload Data":
    st.header("Upload Student Data")
    uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx","xls","csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(("xlsx","xls")):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)

            st.success(f"Loaded file with {df.shape[0]} rows and {df.shape[1]} columns.")
            st.write("Here is a sample of your data:")
            st.dataframe(df.head())
            st.session_state["data"] = df  # store for other pages

        except Exception as e:
            st.error(f"Error reading file: {e}")

# =========================
# Dashboard Page
# =========================
elif page == "Dashboard":
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first from the sidebar.")
    else:
        df = st.session_state["data"].copy()

        required_cols = ["StudentID","Attendance","Marks","FeesDue"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Missing columns: {missing}. Please upload correct file.")
        else:
            # === Calculate Risk Score (simple, transparent) ===
            df["FeesDeduction"] = df["FeesDue"] * 20
            df["RiskScore"] = 100 - (0.4*df["Attendance"] + 0.4*df["Marks"] + df["FeesDeduction"])
            df["RiskScore"] = df["RiskScore"].clip(lower=0).round(1)

            # === Create colored badge HTML for risk ===
            def risk_badge_html(score):
                if score >= 75:
                    color = "#d9534f"  # red
                    text = "HIGH"
                elif score >= 50:
                    color = "#f0ad4e"  # orange
                    text = "MEDIUM"
                else:
                    color = "#5cb85c"  # green
                    text = "LOW"
                return f'<div style="background:{color};color:white;padding:6px;border-radius:6px;text-align:center;font-weight:bold;">{text} ({score})</div>'

            df_display = df[["StudentID","Attendance","Marks","FeesDue","RiskScore"]].copy()
            df_display["Risk"] = df_display["RiskScore"].apply(lambda s: risk_badge_html(s))

            # === Convert to HTML table so colored badges render ===
            html_table = df_display.to_html(escape=False, index=False)
            st.subheader("📋 Student Risk Scores")
            st.markdown(html_table, unsafe_allow_html=True)

            # === Risk distribution (bar chart using streamlit, no extra libs) ===
            st.subheader("📊 Risk Distribution")
            high = int((df["RiskScore"] >= 75).sum())
            medium = int(((df["RiskScore"] >= 50) & (df["RiskScore"] < 75)).sum())
            low = int((df["RiskScore"] < 50).sum())

            counts = pd.DataFrame({
                "Risk": ["High Risk","Medium Risk","Low Risk"],
                "Count": [high, medium, low]
            }).set_index("Risk")

            st.bar_chart(counts)

# =========================
# About Page
# =========================
elif page == "About":
    st.header("ℹ️ About Project Drishti")
    st.markdown("""
    **Drishti** is an early warning system for schools/colleges.  
    It unifies student data and shows real-time **Student at Risk (StAR) scores**.

    - Shows **why** a student is at risk (attendance/marks/fees)
    - Easy file upload for non-tech users
    - No-cost stack: Streamlit + simple CSV/Excel files
    """)
