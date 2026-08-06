"""Gemini AI Service."""

import json
import logging

from google import genai

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Gemini AI integration."""

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY.get_secret_value(),
        )

    async def generate_career_report(
        self,
        career_goal: str,
        full_name: str,
        education_stage: str,
        date_of_birth: str,
    ) -> dict:
        """Generate a career report using Gemini."""

        prompt = f"""
You are an expert career counsellor.

Student Details

Career Goal:
{career_goal}

Full Name:
{full_name}

Education:
{education_stage}

Date of Birth:
{date_of_birth}

Generate a personalized career report.

IMPORTANT RULES

1. Return ONLY valid JSON.
2. Do NOT use markdown.
3. Do NOT wrap the response inside ```json.
4. Do NOT explain anything.
5. Confidence score must be between 1 and 100.
6. Generate exactly 5 roadmap phases.

Return this exact JSON format:

{{
  "career_persona": "",
  "confidence_score": 95,
  "recommended_stream": "",
  "primary_skill": "",
  "career_overview": "",
  "next_step": "",
  "target_exams": "",
  "roadmap": [
    {{
      "phase_number": 1,
      "phase_title": "",
      "duration": "",
      "description": ""
    }},
    {{
      "phase_number": 2,
      "phase_title": "",
      "duration": "",
      "description": ""
    }},
    {{
      "phase_number": 3,
      "phase_title": "",
      "duration": "",
      "description": ""
    }},
    {{
      "phase_number": 4,
      "phase_title": "",
      "duration": "",
      "description": ""
    }},
    {{
      "phase_number": 5,
      "phase_title": "",
      "duration": "",
      "description": ""
    }}
  ]
}}
"""

        logger.info(
            "Generating career report using Gemini."
        )

        response = self.client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        )

        text = response.text.strip()

        logger.info(
            "Gemini Raw Response: %s",
            text,
        )

        # Remove markdown if Gemini returns it
        if text.startswith("```json"):
            text = text.replace(
                "```json",
                "",
                1,
            )

        if text.startswith("```"):
            text = text.replace(
                "```",
                "",
                1,
            )

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        try:
            return json.loads(text)

        except json.JSONDecodeError as ex:
            logger.exception(
                "Failed to parse Gemini response."
            )

            raise ValueError(
                f"Invalid JSON returned by Gemini:\n{text}"
            ) from ex


gemini_service = GeminiService()