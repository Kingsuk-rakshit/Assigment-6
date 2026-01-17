import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Groq Client Setup

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return Groq(api_key=api_key)



# Utility: Safe JSON Parsing

def parse_json(response_text: str):
    """
    Attempts to safely parse JSON from LLM output.
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON block if extra text exists
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start != -1 and end != -1:
            return json.loads(response_text[start:end])
        raise ValueError("LLM did not return valid JSON")



# Agent 1: Topic & Structure Extraction

def extract_structure(text: str) -> dict:
    """
    Extracts topics, subtopics, and key concepts.
    """
    client = get_groq_client()

    prompt = f"""
You are an educational content structuring AI.

From the content below:
1. Identify main topics
2. Identify subtopics under each topic
3. Identify key concepts under each subtopic

Return STRICT JSON in this format:
{{
  "topics": [
    {{
      "name": "Topic name",
      "subtopics": [
        {{
          "name": "Subtopic name",
          "concepts": ["concept1", "concept2"]
        }}
      ]
    }}
  ]
}}

CONTENT:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return parse_json(response.choices[0].message.content)



# Agent 2: Flashcard Generator

def generate_flashcards(text: str) -> list:
    """
    Generates educational flashcards.
    """
    client = get_groq_client()

    prompt = f"""
Generate high-quality study flashcards from the content below.

Rules:
- One concept per card
- Clear question
- Concise factual answer

Return STRICT JSON ARRAY:
[
  {{
    "topic": "Topic name",
    "question": "Question text",
    "answer": "Answer text"
  }}
]

CONTENT:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    return parse_json(response.choices[0].message.content)



# Agent 3: Summary Generator

def generate_summary(text: str) -> str:
    """
    Generates a structured markdown summary.
    """
    client = get_groq_client()

    prompt = f"""
Create a concise, structured learning summary in MARKDOWN.

Guidelines:
- Use headings and bullet points
- Focus on key ideas
- Educational tone

CONTENT:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return response.choices[0].message.content



# Agent 4: Concept Graph Generator

def generate_concept_graph(text: str) -> dict:
    """
    Generates a concept graph (nodes + edges).
    """
    client = get_groq_client()

    prompt = f"""
Extract a concept graph from the content below.

Return STRICT JSON:
{{
  "nodes": ["Concept A", "Concept B"],
  "edges": [
    ["Concept A", "Concept B"]
  ]
}}

Rules:
- Nodes must be meaningful concepts
- Edges show dependency or relationship

CONTENT:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return parse_json(response.choices[0].message.content)
