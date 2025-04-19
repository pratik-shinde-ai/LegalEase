import streamlit as st
import os
import sys
import json

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from compliance.llm_integration import LLMIntegration
from compliance.document_processor import process_document

# Set the GROQ API key
os.environ["GROQ_API_KEY"] = "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"

def main():
    st.title("Compliance Checker")
    
    uploaded_file = st.file_uploader("Upload a contract file", type=['pdf', 'docx'])

    if uploaded_file is not None:
        with st.spinner("Processing document..."):
            # Save the uploaded file temporarily
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                document_text = process_document(uploaded_file.name)
                st.success("Document processed successfully!")
            except Exception as e:
                st.error(f"Failed to process document: {e}")
                return

        if document_text:
            llm = LLMIntegration()
            
            with st.spinner("Analyzing the contract..."):
                analysis = llm.analyze_contract(document_text)

            if analysis:
                st.subheader("Contract Analysis")
                
                st.write("**Summary:**")
                st.write(analysis.get("summary", "No summary available."))
                
                st.write("**Balance Score:**")
                st.write(analysis.get("balance_score", "N/A"))
                
                st.write("**Compliance Check:**")
                compliance_check = analysis.get("compliance_check", {})
                for law, details in compliance_check.items():
                    st.write(f"- {law.replace('_', ' ')}: {'Compliant' if details['compliant'] else 'Non-compliant'}")
                    if details['issues']:
                        st.write("  Issues:")
                        for issue in details['issues']:
                            st.write(f"    • {issue}")
                
                st.write("**Key Clauses:**")
                key_clauses = analysis.get("key_clauses", [])
                for clause in key_clauses:
                    st.write(f"- {clause['type']}")
                    st.write(f"  Content: {clause['content']}")
                    st.write(f"  Analysis: {clause['analysis']}")
                    if clause['issues']:
                        st.write("  Issues:")
                        for issue in clause['issues']:
                            st.write(f"    • {issue}")
                
                st.write("**Overall Assessment:**")
                st.write(analysis.get("overall_assessment", "No overall assessment available."))

                # Add a section for follow-up questions
                st.subheader("Ask a Follow-up Question")
                question = st.text_input("Enter your question about the contract:")
                if st.button("Get Answer"):
                    with st.spinner("Analyzing..."):
                        followup_analysis = llm.get_followup_analysis(question, json.dumps(analysis))
                    if followup_analysis:
                        st.write("**Answer:**", followup_analysis.get("answer"))
                        st.write("**Explanation:**", followup_analysis.get("explanation"))
                        st.write("**Law References:**")
                        for ref in followup_analysis.get("law_references", []):
                            st.write(f"- {ref['law']}, Section {ref['section']}")
                            st.write(f"  Status: {ref['compliance_status']}")
                            st.write(f"  Details: {ref['details']}")
                    else:
                        st.error("Failed to get follow-up analysis. Please try again.")
            else:
                st.error("Failed to analyze the contract. Please try again.")

        # Clean up the temporary file
        os.remove(uploaded_file.name)

if __name__ == "__main__":
    main()
