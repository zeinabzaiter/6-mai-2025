import streamlit as st
import pandas as pd
import plotly.express as px

# Title
st.title("Weekly % Distribution of Staphylococcus aureus Phenotypes (2024)")
st.write("Hover over the graph to see exact values. All percentages are calculated per week (0–100%).")

# Load data (you can replace the URL below with the raw GitHub link if hosted)
@st.cache_data

def load_data():
    df = pd.read_csv("staph_aureus_pheno_weekly.csv")
    df["week"] = pd.to_datetime(df["week"])
    df["Total"] = df[["MRSA", "VRSA", "Other", "Wild"]].sum(axis=1)
    for col in ["MRSA", "VRSA", "Other", "Wild"]:
        df[f"{col}_%"] = round((df[col] / df["Total"] * 100), 2)

    # Calculate Tukey thresholds
    def tukey_threshold(series):
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        return q3 + 1.5 * iqr

    mrsa_thresh = tukey_threshold(df["MRSA"])
    other_thresh = tukey_threshold(df["Other"])

    # Add alert columns
    df["MRSA_alert"] = df["MRSA"] > mrsa_thresh
    df["Other_alert"] = df["Other"] > other_thresh
    df["VRSA_alert"] = df["VRSA"] >= 1

    return df

df = load_data()

# Transform to long format for plotting with case counts
case_melted = df.melt(id_vars=["week"], value_vars=["MRSA", "VRSA", "Other", "Wild"],
                      var_name="Phenotype_Count", value_name="Count")
percent_melted = df.melt(id_vars=["week"], value_vars=["MRSA_%", "VRSA_%", "Other_%", "Wild_%"],
                         var_name="Phenotype", value_name="Percentage")

df_long = percent_melted.copy()
df_long["Count"] = case_melted["Count"]

# Define custom dark colors
color_map = {
    "VRSA_%": "#8B0000",   # Dark red
    "MRSA_%": "#FF8C00",   # Dark orange
    "Other_%": "#00008B",  # Dark blue
    "Wild_%": "#006400"     # Dark green
}

# Plot
fig = px.line(df_long, x="week", y="Percentage", color="Phenotype",
              markers=True, range_y=[0, 100],
              labels={"week": "Week", "Percentage": "% of Cases"},
              title="Percentage Distribution of Phenotypes per Week",
              color_discrete_map=color_map)

fig.update_traces(mode="lines+markers",
                  hovertemplate="%{y:.1f}%<br>Week: %{x|%Y-%m-%d}<br>Phenotype: %{fullData.name}<br>Count: %{customdata[0]}",
                  customdata=df_long[["Count"]].values)

# Show plot
st.plotly_chart(fig, use_container_width=True)

# Optional: show raw data
toggle = st.checkbox("Show raw data")
if toggle:
    st.dataframe(df)

# Alert summary table
st.subheader("🔔 Weekly Alert Status (Tukey Method)")
alert_df = df[["week", "MRSA_alert", "Other_alert", "VRSA_alert"]].copy()
alert_df.columns = ["Week", "MRSA Alert", "Other Alert", "VRSA Alert"]
alert_df["Alert"] = alert_df[["MRSA Alert", "Other Alert", "VRSA Alert"]].any(axis=1)
alert_weeks = alert_df[alert_df["Alert"] == True]
st.dataframe(alert_weeks.drop(columns=["Alert"]))
