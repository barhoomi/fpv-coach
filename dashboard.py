import time  # to simulate a real time data, time loop
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
import plotly.express as px
import plotly.graph_objects as go
import os

refresh_rate = 1  # seconds
refresh_history = 30  # seconds

st.set_page_config(
    page_title="Real-Time Data Drone Dashboard",
    page_icon="🛩️",
    layout="wide",
)

# Function to load data from CSV
@st.cache_data(ttl=refresh_history) # Cache the data
def load_data(file_path='log.csv'):
    """Loads data from a CSV file."""
    return pd.read_csv(file_path)


# Function to filter data for the last 30 seconds
def filter_data(df, history_seconds=refresh_history):
    """Filters the DataFrame to include only the last 'history_seconds' seconds of data."""
    if 'timestamp' in df.columns:
        # Ensure 'timestamp' is a datetime column
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        # Filter the DataFrame for the last 'history_seconds' seconds
        current_time = pd.Timestamp.now()
        start_time = current_time - pd.Timedelta(seconds=history_seconds)
        return df[(df['timestamp'] >= start_time) & (df['timestamp'] <= current_time)]
    else:
        st.warning("'timestamp' column not found in data. Cannot filter by time.")
        return pd.DataFrame()  # Return an empty DataFrame if no timestamp column

df = load_data()
df_filtered = filter_data(df, refresh_history)

# Set 'timestamp' as the index for plotting on the filtered DataFrame
if not df_filtered.empty and 'timestamp' in df_filtered.columns:
    df_filtered = df_filtered.set_index('timestamp')
elif not df_filtered.empty:
    st.warning("'timestamp' column not found in filtered data. Plotting with default index.")


buttons = st.container()
# Create a container for the buttons
with buttons:
    st.write(f"# Drone Log Data Visualization (Last {refresh_history} Seconds)")
    st.write("---") # Add a separator

    button1, button2, button3 = st.columns(3)
    with button1:
        st.write("Start Logging Data")
        clicked = st.button("Start", key="start_button")  # Use a unique key to avoid conflicts with the stop button
        if clicked:
            st.success("Logging started. Data will be displayed in real-time.")
            os.system("python3 listener.py >> log.csv")  # Start tailing the log file in the background
        else:
            st.info("Click the button to start logging data. Ensure 'log.csv' is being updated in real-time.")
    
    with button2:
        st.write("stop logging data")
        stop_button = st.button("Stop", key="stop_button")  # Use a different key to avoid conflicts with the start button
        if stop_button:
            st.success("Logging stopped. Data will no longer be updated.")
            os.system("pkill -f listener.py") # Stop the listener script if it's running
        else:
            st.info("Click the button to stop logging data. Ensure 'log.csv' is being updated in real-time.")
            
    with button3:
        st.write("Clear Data")
        clear_button = st.button("Clear", key="clear_button")
        if clear_button:
            st.success("Data cleared. The log file will be reset.")
            if os.path.exists('log.csv'):
                #remove everything except the header
                header = pd.read_csv('log.csv', nrows=0)  # Read only the header
                #clear the file
                os.system("echo '' > log.csv")  # Clear the log file
                #write the header back to the file
                header.to_csv('log.csv', index=False)  # Write the header back to the file
            

st.write("---") # Add another separator

placeholder = st.empty()

while True:
    with placeholder.container():
        
        fig1, fig2 = st.columns(2)
        with fig1:
            st.write(f"### Raw Data (Last {refresh_history} Seconds)")

            if not df_filtered.empty:
                st.dataframe(df_filtered) # Display the filtered raw data in a table
            else:
                st.info(f"No data in the last {refresh_history} seconds to display. Please ensure 'log.csv' exists, is correctly formatted, and has recent entries.")
                
        with fig2:
            # Plot all numerical columns using st.line_chart from the filtered DataFrame
            st.write(f"### All Numerical Data Plots (Last {refresh_history} Seconds)")
            if not df_filtered.empty:
                # Select only numerical columns for plotting
                numerical_df_filtered = df_filtered.select_dtypes(include=['number'])
                if not numerical_df_filtered.empty:
                    st.line_chart(numerical_df_filtered)
                else:
                    st.warning("No numerical data found in the filtered CSV for plotting.")
            else:
                st.info(f"No data available in the last {refresh_history} seconds for plotting.")
            
        st.write("---") # Add another separator

        st.write(f"### Individual Column Plots (Last {refresh_history} Seconds)")
        
        fig3, fig4 = st.columns(2)
        # Example of plotting specific columns from the filtered DataFrame
        with fig3:
            if 'drone_position_x' in df_filtered.columns and 'drone_position_y' in df_filtered.columns and 'drone_position_z' in df_filtered.columns:
                #st.line_chart(df_filtered[['drone_position_x', 'drone_position_y', 'drone_position_z']])
                fig = go.Figure(data=[go.Scatter3d(
                    x=df['drone_position_x'],
                    y=df['drone_position_y'],
                    z=df['drone_position_z'],
                    mode='markers',
                    marker=dict(
                        size=1,
                        color="#ffffff",                # set color to an array/list of desired values
                        colorscale='Viridis',   # choose a colorscale
                        opacity=0.8
                    )
                )])
                fig.update_layout(
                    title='Drone Position in 3D Space',
                    scene=dict(
                        xaxis_title='X Position',
                        yaxis_title='Y Position',
                        zaxis_title='Z Position'
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
                st.write("Above: Drone Position (X, Y, Z)")
            else:
                st.info("Drone position columns not found in filtered data for individual plot example.")

        with fig4:
            if 'battery_percentage' in df_filtered.columns:
                st.line_chart(df_filtered['battery_percentage'])
                st.write("Above: Battery Percentage")
            else:
                st.info("Battery percentage column not found in filtered data for individual plot example.")

        st.markdown("### Detailed Data View")
        st.dataframe(df)
        df = load_data()  # Reload the data to simulate real-time updates
        df_filtered = filter_data(df, refresh_history)  # Filter the data for the last 30 seconds
        time.sleep(refresh_rate)