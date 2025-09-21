import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Page Config
# =========================
st.set_page_config(page_title="Project Drishti", layout="wide")

# =========================
# Custom Styling
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
    </style>
""", unsafe_allow_html=True)

# =========================
# Sidebar
# =========================
st.sidebar.image("logo.png", width=120)  # upload logo.png to your repo
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
        df = st.session_state["data"]

        required_cols = ["StudentID","Attendance","Marks","FeesDue"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Missing columns: {missing}. Please upload correct file.")
        else:
            # Calculate Risk Score
            df["FeesDeduction"] = df["FeesDue"] * 20
            df["RiskScore"] = 100 - (0.4*df["Attendance"] + 0.4*df["Marks"] + df["FeesDeduction"])
            df["RiskScore"] = df["RiskScore"].clip(lower=0).round(1)

            st.subheader("📋 Student Risk Scores")

            def color_risk(val):
                if val >= 75:
                    return "background-color: red; color: white; font-weight: bold;"
                elif val >= 50:
                    return "background-color: orange; color: black; font-weight: bold;"
                else:
                    return "background-color: green; color: white; font-weight: bold;"

            styled = df[["StudentID","Attendance","Marks","FeesDue","RiskScore"]].style.applymap(color_risk, subset=["RiskScore"])
            st.dataframe(styled, use_container_width=True)

            # =========================
            # Chart: Risk Distribution
            # =========================
            st.subheader("📊 Risk Distribution")

            high = (df["RiskScore"] >= 75).sum()
            medium = ((df["RiskScore"] >= 50) & (df["RiskScore"] < 75)).sum()
            low = (df["RiskScore"] < 50).sum()

            fig, ax = plt.subplots()
            ax.bar(["High Risk", "Medium Risk", "Low Risk"], [high, medium, low], color=["red", "orange", "green"])
            ax.set_title("Risk Distribution of Students")
            ax.set_ylabel("Number of Students")
            st.pyplot(fig)

# =========================
# About Page
# =========================
elif page == "About":
    st.header("ℹ️ About Project Drishti")
    st.markdown("""
    **Drishti** is an AI-powered early warning system for schools and colleges.  
    It unifies student data and generates a real-time **Student at Risk (StAR) score**.  

    ✅ Moves intervention from **reactive** → **proactive**  
    ✅ Provides a **single source of truth** for student data  
    ✅ Built on **open-source** (zero-cost for institutions)  
    ✅ Includes **Explainable AI** (transparent scoring logic)  
    """)
