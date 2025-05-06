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
    return df

df = load_data()

# Transform to long format for plotting
df_long = df.melt(id_vars="week", 
                  value_vars=["MRSA_%", "VRSA_%", "Other_%", "Wild_%"],
                  var_name="Phenotype", value_name="Percentage")

# Plot
fig = px.line(df_long, x="week", y="Percentage", color="Phenotype",
              markers=True, range_y=[0, 100],
              labels={"week": "Week", "Percentage": "% of Cases"},
              title="Percentage Distribution of Phenotypes per Week")

fig.update_traces(mode="lines+markers",
                  hovertemplate="%{y:.1f}%<br>Week: %{x|%Y-%m-%d}<br>Phenotype: %{fullData.name}")

# Show plot
st.plotly_chart(fig, use_container_width=True)

# Optional: show raw data
toggle = st.checkbox("Show raw data")
if toggle:
    st.dataframe(df)
