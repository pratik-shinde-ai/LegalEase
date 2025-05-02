import groq
import json
import os
import re  # For extracting JSON

class LLMIntegration:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.environ.get("GROQ_API_KEY")
        if api_key is None:
            raise ValueError("GROQ API key not provided and not found in environment variables")
        self.client = groq.Groq(api_key=api_key)

    def _extract_json(self, text):
        """Extract JSON object from a string using regex."""
        try:
            json_match = re.search(r"\{(?:[^{}]|(?R))*\}", text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except json.JSONDecodeError as e:
            print("JSON extraction failed:", e)
        return None

    def analyze_contract(self, contract_text):
        prompt = f"""
        Analyze the following contract for compliance with Indian laws including the Companies Act, 2013, the Code of Wages, 2019, Occupational Safety, Health and Working Conditions Code, 2020, the Code on Social Security, 2020, and the Industrial Relations Code, 2020. 

        Highlight any sections that may not comply with these laws and provide a structured response in JSON format:

        Contract text:
        {contract_text[:4000]}

        Please provide the analysis in the following JSON structure:
        {{
            "summary": "A brief summary of the entire contract",
            "balance_score": 0-100,
            "compliance_check": {{
                "Companies_Act_2013": {{
                    "compliant": true/false,
                    "issues": ["..."]
                }},
                "Code_of_Wages_2019": {{
                    "compliant": true/false,
                    "issues": ["..."]
                }},
                "OSH_Code_2020": {{
                    "compliant": true/false,
                    "issues": ["..."]
                }},
                "Social_Security_Code_2020": {{
                    "compliant": true/false,
                    "issues": ["..."]
                }},
                "Industrial_Relations_Code_2020": {{
                    "compliant": true/false,
                    "issues": ["..."]
                }}
            }},
            "key_clauses": [
                {{
                    "type": "...",
                    "content": "...",
                    "analysis": "...",
                    "issues": ["..."]
                }}
            ],
            "overall_assessment": "..."
        }}
        Only return JSON without any extra explanation.
        """

        response = self.client.chat.completions.create(
            model="llama-guard-3-8b",
            messages=[
                {"role": "system", "content": "You are an AI legal assistant specialized in contract analysis and compliance with Indian laws."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4000,
        )

        try:
            response_content = response.choices[0].message.content
            print("\nRaw API Response:\n", response_content)  # Print full response
            parsed = self._extract_json(response_content)
            if parsed:
                return parsed
            else:
                return {
                    "error": "Failed to extract valid JSON.",
                    "raw_response": response_content
                }
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {
                "error": str(e),
                "raw_response": str(response)
            }

    def get_followup_analysis(self, question, context):
        prompt = f"""
        Based on the following contract analysis, answer this question:
        {question}

        Contract analysis context:
        {context}

        Please provide your response in the following JSON format:
        {{
            "answer": "...",
            "explanation": "...",
            "law_references": [
                {{
                    "law": "...",
                    "section": "...",
                    "compliance_status": "...",
                    "details": "..."
                }}
            ]
        }}
        Only return JSON. No extra explanations.
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

        try:
            response_content = response.choices[0].message.content
            print("\nRaw API Response:\n", response_content)  # Debug print
            parsed = self._extract_json(response_content)
            if parsed:
                return parsed
            else:
                return {
                    "error": "Failed to extract valid JSON.",
                    "raw_response": response_content
                }
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {
                "error": str(e),
                "raw_response": str(response)
            }

