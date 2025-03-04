import json
import os
import textwrap
from dotenv import load_dotenv
load_dotenv()
from google import genai
from google.genai import types

from IPython.display import JSON
from IPython.display import display
from IPython.display import Markdown

Person = {
    
    "type": "OBJECT",
    "properties": {
        "character_name": {
            "type": "STRING",
            "description": "Character name",
        },
        "character_description": {
            "type": "STRING",
            "description": "Character description",
        }
    },
    "required": ["character_name", "character_description"]
}

Relationships = {
    "type": "OBJECT",
    "properties": {
        "first_character": {
            "type": "STRING",
            "description": "First character name",
        },
        "second_character": {
            "type": "STRING",
            "description": "Second character name",
        },
        "relationship": {
            "type": "STRING",
            "description": "Familiar elationship between first and second character",
        }
    },
    "required": ["first_character", "second_character", "relationship"]
}


Places = {
    "type": "OBJECT",
    "properties": {
        "place_name": {
            "type": "STRING",
            "description": "Place name",
        },
        "place_description": {
            "type": "STRING",
            "description": "Place description",
        }
    },
    "required": ["place_name", "place_description"]
}

Things = {
    "type": "OBJECT",
    "properties": {
        "thing_name": {
            "type": "STRING",
            "description": "Thing name",
        },
        "thing_description": {
            "type": "STRING",
            "description": "Thing description",
        }
    },
    "required": ["thing_name", "thing_description"]
}

get_people = types.FunctionDeclaration(
    name="get_people",
    description="Get information about characters",
    parameters=Person,
)

get_relationships = types.FunctionDeclaration(
    name="get_relationships",
    description="Get information about relationships between people",
    parameters=Relationships
)

get_places = types.FunctionDeclaration(
    name="get_places",
    description="Get information about places",
    parameters=Places
)

get_things = types.FunctionDeclaration(
    name="get_things",
    description="Get information about things",
    parameters=Things
)

story_tools = types.Tool(
    function_declarations=[get_people, get_relationships, get_places, get_things],
)

MODEL_ID="gemini-1.5-flash"


client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """
Write a long story about a girl with magic backpack, her family, and at
least one other character. Make sure everyone has names. Don't forget to
describe the contents of the backpack, and where everyone and everything
starts and ends up.
"""

response = client.models.generate_content(
  model=MODEL_ID,
  contents=prompt,    
)
story = response.text

prompt = f"""
{story}

Please add the people, places, things, and relationships from this story to the database
"""



result = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[story_tools],
        temperature=0
        )
)


for part in result.candidates[0].content.parts:
  print(json.dumps(part.function_call.args, indent=4))