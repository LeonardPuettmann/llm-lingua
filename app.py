from flask import Flask, request, jsonify
from flask_cors import CORS
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
import json

# Load available tools
with open('./mistral/tools.json') as f:
    tools = json.load(f)

# Settings for the Mistral LLM
api_key = os.environ["MISTRAL_API_KEY"]
if not api_key:
    api_key = input("Please input your Mistral AI key: ")
client = MistralClient(api_key=api_key)

model = "mistral-large-latest"
temperature = 0.0
top_p = 1
max_tokens = 1024

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data['question']
    messages = [ChatMessage(role="user", content=question)]

    model_params = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "tools": tools,
        "tool_choice": "auto"
    }

    response_messages = []

    for response in client.chat_stream(**model_params):
        # If the response is not a tool call, add it to the response_messages list
        if response.choices[0].delta.tool_calls is None:
            response_messages.append(response.choices[0].delta.content)

    return jsonify({"answer": "\n".join(response_messages)})

if __name__ == '__main__':
    app.run(host='localhost', port=8765)
