import streamlit as st
import sys
import os

# Add the summary directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'summary'))

# Import the main function from the summary app
from app import main as summary_main

if __name__ == "__main__":
    summary_main()
