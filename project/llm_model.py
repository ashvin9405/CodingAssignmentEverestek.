import openai
import os

API_KEY = os.getenv("API_KEY")

# Function to Get Name Origin from OpenAI
client = openai.OpenAI(api_key=API_KEY)

def get_name_origin(name):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": f"What is the origin of the name {name}?"}]
        )
        return response.choices[0].message.content  
    except Exception as e:
        return "LLM service unavailable."
