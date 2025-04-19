import streamlit as st
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Import the main function from the compliance app
from compliance.app import main as compliance_main

def main():
    compliance_main()

if __name__ == "__main__":
    main()
