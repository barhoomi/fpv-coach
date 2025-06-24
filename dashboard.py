# %%
import csv
import streamlit as st


# %%
timestamps = []    

with open('log.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
            timestamps.append(row['timestamp'])

# %%
st.write("""
# My first app
Hello *world!*
""")
 
st.line_chart(timestamps)


