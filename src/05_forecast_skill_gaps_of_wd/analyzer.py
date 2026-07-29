"""
===============================================================================
File: future_skills_analyzer.py

Purpose:
    Provides the core Large Language Model (LLM) analysis engine used to
    evaluate business process updates and forecast future workforce skill
    requirements.

Classes:
    FutureSkillsAnalyzer
        Encapsulates LLM interactions for competency forecasting and
        business process impact analysis.

Methods:
    __init__(system_prompt)
        Initializes the analyzer with a predefined system prompt and
        creates an Assistant instance for LLM communication.

    analyze_update(update_element)
        Submits a business process update to the LLM for analysis and
        returns the model's response in JSON format.

Author:
    Souroosh Memarian

Created:
    2026-07-21

Last Modified:
    2026-07-21

Version:
    1.0.0

Dependencies:
    - assistant.Assistant
    - assistant.persistent_send

Notes:
    - Implements the core AI-driven analysis workflow for the application.
    - Uses a persistent messaging mechanism to improve reliability when
      communicating with the LLM.
    - Requires a fully constructed system prompt containing organizational
      context, work description details, and forecasting instructions.
    - Expects responses to be returned as valid JSON for downstream
      processing and storage.
    - Designed to support future skills forecasting, competency gap
      identification, workforce planning, and business transformation
      initiatives.

Workflow:
    1. Initialize the analyzer with a system prompt.
    2. Submit a business process update element.
    3. Send the request to the LLM.
    4. Receive a structured JSON response.
    5. Return the response for parsing and persistence.

===============================================================================
"""

from assistant import Assistant
from assistant import persistent_send


class FutureSkillsAnalyzer:

    def __init__(self, system_prompt):

        self.assistant = Assistant(
            system_prompt=system_prompt
        )

    def analyze_update(
        self,
        update_element
    ):

        prompt = f"""
        Analyze the following GSBPM update element.

        Apply the task instructions and JSON schema
        provided in the system prompt.

        GSBPM UPDATE ELEMENT

        ```json 
        {update_element}


        Return valid JSON only. """

        return persistent_send(
            self.assistant.send_message,
            prompt
        )