import groq
import json
import os

class LLMIntegration:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.environ.get("GROQ_API_KEY")
        if api_key is None:
            raise ValueError("GROQ API key not provided and not found in environment variables")
        self.client = groq.Groq(api_key=api_key)

    def analyze_contract(self, contract_text):
        prompt = f"""
        Analyze the following contract for compliance with Indian laws including the Companies Act, 2013, the Code of Wages, 2019, Occupational Safety, Health and Working Conditions Code, 2020, the Code on Social Security, 2020, and the Industrial Relations Code, 2020. 

        Highlight any sections that may not comply with these laws and provide a structured response in JSON format:

        Contract text:
        {contract_text[:4000]}

        Please provide the analysis in the following JSON structure:
        {{
            "summary": "A brief summary of the entire contract",
            "balance_score": A number between 0 and 100 representing how balanced the contract is (0 = heavily favors one party, 100 = perfectly balanced),
            "compliance_check": {{
                "Companies_Act_2013": {{
                    "compliant": true/false,
                    "issues": ["List of compliance issues with sections of the Companies Act, 2013"]
                }},
                "Code_of_Wages_2019": {{
                    "compliant": true/false,
                    "issues": ["List of compliance issues with sections of the Code of Wages, 2019"]
                }},
                "OSH_Code_2020": {{
                    "compliant": true/false,
                    "issues": ["List of compliance issues with the Occupational Safety, Health and Working Conditions Code, 2020"]
                }},
                "Social_Security_Code_2020": {{
                    "compliant": true/false,
                    "issues": ["List of compliance issues with the Code on Social Security, 2020"]
                }},
                "Industrial_Relations_Code_2020": {{
                    "compliant": true/false,
                    "issues": ["List of compliance issues with the Industrial Relations Code, 2020"]
                }}
            }},
            "key_clauses": [
                {{
                    "type": "The type of clause",
                    "content": "The text of the clause",
                    "analysis": "A brief analysis of the clause, including any potential issues or risks",
                    "issues": ["List of specific issues or problematic phrases in this clause"]
                }}
            ],
            "overall_assessment": "An overall assessment of the contract, including major strengths and weaknesses"
        }}
        """

        response = self.client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[
                {"role": "system", "content": "You are an AI legal assistant specialized in contract analysis and compliance with Indian laws."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4000,
        )
        
        # Check and log the response before attempting to parse it
        try:
            response_content = response.choices[0].message.content
            print("API Response:", response_content)  # Debugging: Log the response content
            parsed_response = json.loads(response_content)  # Attempt to parse the response
            return parsed_response  # Return the parsed response if successful
        except (AttributeError, KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing response: {e}")  # Log any errors encountered
            print("Raw API Response:", response)   # Log the raw response for further debugging
            return None  # Return None or handle the error as needed

    def get_followup_analysis(self, question, context):
        prompt = f"""
        Based on the following contract analysis, answer this question:
        {question}

        Contract analysis context:
        {context}

        Please provide your response in the following JSON format:
        {{
            "answer": "Your answer to the question",
            "explanation": "An explanation or justification for your answer",
            "law_references": [
                {{
                    "law": "The specific law referenced",
                    "section": "The relevant section number",
                    "compliance_status": "Compliant/Non-Compliant",
                    "details": "Detailed explanation of compliance or non-compliance"
                }}
            ]
        }}
        """

        response = self.client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an AI legal assistant specialized in contract analysis and compliance with Indian laws."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000,
        )
        
        # Check and log the response before attempting to parse it
        try:
            response_content = response.choices[0].message.content
            print("API Response:", response_content)  # Debugging: Log the response content
            return json.loads(response_content)  # Attempt to parse the response
        except (AttributeError, KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing response: {e}")  # Log any errors encountered
            print("Raw API Response:", response)   # Log the raw response for further debugging
            return None  # Return None or handle the error as needed
