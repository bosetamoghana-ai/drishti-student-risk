import streamlit as st
import pandas as pd

st.set_page_config(page_title="Drishti Student Risk App", layout="wide")

st.title("Drishti – Student Risk Dashboard")

# Upload section
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
        st.write("---")

        # Simple risk scoring: attendance, marks, fees must have these column names
        # For demo: assume your file has columns: "Attendance", "Marks", "FeesDue"
        # If not, app will ask you
        required_cols = ["StudentID","Attendance","Marks","FeesDue"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.warning(f"Missing columns: {missing}. Please ensure these are present or rename columns.")
        else:
            # calculate simple risk score
            # attendance out of 100, marks out of 100, fees due yes/no
            df["AttendanceNorm"] = df["Attendance"]
            df["MarksNorm"] = df["Marks"]
            # let's say FeesDue is 0 or 1
            df["FeesDeduction"] = df["FeesDue"] * 20  # if fee due, subtract 20 points

            # risk = 100 - weighted sum
            df["RiskScore"] = 100 - (0.4 * df["AttendanceNorm"] + 0.4 * df["MarksNorm"] + df["FeesDeduction"])
            df["RiskScore"] = df["RiskScore"].clip(lower=0).round(1)

            st.header("Student Risk Scores")
            st.dataframe(df[["StudentID","Attendance","Marks","FeesDue","RiskScore"]])

            # highlight high risk
            def color_risk(val):
                if val >= 75:
                    return 'background-color: red; color: white'
                elif val >= 50:
                    return 'background-color: yellow; color: black'
                else:
                    return 'background-color: green; color: white'

            styled = df[["StudentID","RiskScore"]].style.applymap(color_risk, subset=["RiskScore"])
            st.write("### Risk Levels")
            st.dataframe(styled)

    except Exception as e:
        st.error(f"Error reading file: {e}")
