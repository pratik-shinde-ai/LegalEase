import streamlit as st
import sys
import os

# Add the drafting directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'drafting'))

# Import the main function from the drafting app
from app import main as drafting_main

if __name__ == "__main__":
    drafting_main()
