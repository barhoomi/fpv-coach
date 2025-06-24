# %%
import streamlit as st
import pandas as pd
import os # Import os module to check for file existence
from streamlit_autorefresh import st_autorefresh # Import the autorefresh component

# %%
# Function to load data from CSV
@st.cache_data(ttl=1) # Cache the data for 1 second, matching the refresh rate
def load_data(file_path):
    """Loads data from a CSV file."""
    if not os.path.exists(file_path):
        st.error(f"Error: The file '{file_path}' was not found. Please ensure it's in the same directory.")
        return pd.DataFrame() # Return an empty DataFrame if file not found

    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return pd.DataFrame() # Return empty DataFrame on error

# Define the CSV file path
csv_file_path = 'log.csv'

# Automatically refresh the app every 1000 milliseconds (1 second)
# This will cause the entire script to rerun, reloading the data
st_autorefresh(interval=1000, key="data_refresher")

# Load the data
df = load_data(csv_file_path)

# Ensure 'timestamp' is a numerical column for filtering
if not df.empty and 'timestamp' in df.columns:
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
    df.dropna(subset=['timestamp'], inplace=True) # Remove rows where timestamp couldn't be converted

    # Filter data to show only the last 30 seconds
    if not df.empty:
        max_timestamp = df['timestamp'].max()
        time_threshold = max_timestamp - 30 # Calculate the timestamp 30 seconds ago
        df_filtered = df[df['timestamp'] >= time_threshold]
    else:
        df_filtered = pd.DataFrame() # No data to filter
else:
    df_filtered = pd.DataFrame() # No timestamp column or empty dataframe


# Set 'timestamp' as the index for plotting on the filtered DataFrame
if not df_filtered.empty and 'timestamp' in df_filtered.columns:
    df_filtered = df_filtered.set_index('timestamp')
elif not df_filtered.empty:
    st.warning("'timestamp' column not found in filtered data. Plotting with default index.")

# %%
st.write("""
# Drone Log Data Visualization (Last 30 Seconds)
Hello *world!*
""")

st.write("---") # Add a separator

st.write("### Raw Data (Last 30 Seconds)")
if not df_filtered.empty:
    st.dataframe(df_filtered) # Display the filtered raw data in a table
else:
    st.info("No data in the last 30 seconds to display. Please ensure 'log.csv' exists, is correctly formatted, and has recent entries.")


st.write("---") # Add another separator

st.write("### All Numerical Data Plots (Last 30 Seconds)")

# Plot all numerical columns using st.line_chart from the filtered DataFrame
if not df_filtered.empty:
    # Select only numerical columns for plotting
    numerical_df_filtered = df_filtered.select_dtypes(include=['number'])
    if not numerical_df_filtered.empty:
        st.line_chart(numerical_df_filtered)
    else:
        st.warning("No numerical data found in the filtered CSV for plotting.")
else:
    st.info("No data available in the last 30 seconds for plotting.")

st.write("---") # Add another separator

st.write("### Individual Column Plots (Last 30 Seconds, Optional)")
st.write("You can also plot individual columns if needed:")

# Example of plotting specific columns from the filtered DataFrame
if not df_filtered.empty:
    if 'drone_position_x' in df_filtered.columns and 'drone_position_y' in df_filtered.columns and 'drone_position_z' in df_filtered.columns:
        st.line_chart(df_filtered[['drone_position_x', 'drone_position_y', 'drone_position_z']])
        st.write("Above: Drone Position (X, Y, Z)")
    else:
        st.info("Drone position columns not found in filtered data for individual plot example.")

    if 'battery_percentage' in df_filtered.columns:
        st.line_chart(df_filtered['battery_percentage'])
        st.write("Above: Battery Percentage")
    else:
        st.info("Battery percentage column not found in filtered data for individual plot example.")

