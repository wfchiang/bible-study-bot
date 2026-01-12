#!/bin/bash

# 1. Source the environment setup script
# Note: Using 'setup_env.sh' as seen in your file list (not 'setup.sh').
source setup_env.sh

# 2. Start Nginx in the background
service nginx start

# 3. Create a process to run mcp_server.py in the background
# The '&' at the end pushes the process to the background so the script continues.
python py/mcp_server.py &

# 4. Run the Streamlit GUI
# Note: Streamlit typically runs .py files. Assuming 'py/gui.sh' was a typo for 'py/gui.py'.
# We add --server.baseUrlPath=/ui so Streamlit knows it is being served under /ui.
# This command blocks, keeping the Docker container alive.
streamlit run py/gui.py --server.baseUrlPath=/ui