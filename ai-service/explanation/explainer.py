# ai-service/explanation/explainer.py

from typing import Dict, Any

def generate_explanations(parsed_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Generates simple, rule-based explanations for how data was extracted.
    """
    explanations = {}
    for key, value in parsed_data.items():
        if value:
            # General explanation for successfully extracted fields
            explanations[key] = f"The value for '{key.replace('_', ' ').title()}' was identified and extracted from the document."
        else:
            # Explanation for fields that could not be found
            explanations[key] = f"No clear value for '{key.replace('_', ' ').title()}' was found in the document."

    # Provide more specific, custom explanations for complex fields
    if "skills" in parsed_data and parsed_data["skills"]:
        explanations["skills"] = "Skills were identified by cross-referencing keywords from the 'Skills' and 'Experience' sections against a predefined list of technologies."

    if "experience_years" in parsed_data and parsed_data["experience_years"]:
        explanations["experience_years"] = "Total years of experience were calculated by summarizing the durations listed in the work history section."

    return explanations