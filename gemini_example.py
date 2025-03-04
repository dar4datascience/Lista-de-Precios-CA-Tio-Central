import json
import os
import textwrap
from dotenv import load_dotenv

from google import genai
from google.genai import types

from IPython.display import JSON
from IPython.display import display
from IPython.display import Markdown

load_dotenv()

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


MODEL_ID="gemini-1.5-flash"
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

print(story)