import websockets
import asyncio
import json
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import functools
import os
from threading import Thread
from mistral.tools import get_definition, get_random_word

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

names_to_functions = {
    "get_definition": functools.partial(get_definition),
    "get_random_word": functools.partial(get_random_word)
}

messages = []

async def send_message_to_mistral_ai(message):
    global messages
    messages.clear()
    messages.append(ChatMessage(role="user", content=message))

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

        # If response is a tool call, apply tool call and add it to the response_messages list
        elif response.choices[0].delta.tool_calls:
            tool_call = response.choices[0].delta.tool_calls[0]
            function_name = tool_call.function.name
            function_params = json.loads(tool_call.function.arguments)

            # Execute the function
            function_result = names_to_functions[function_name](**function_params)

            # Create a new user message with the function result
            new_message = ChatMessage(role="user", content=function_result)
            messages.append(new_message)

            # Send the new message back to the Mistral model
            for response in client.chat_stream(model=model, messages=messages):
                response_messages.append(response.choices[0].delta.content)

    return "\n".join(response_messages)

async def websocket_handler(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        question = data['question']
        response = await send_message_to_mistral_ai(question)
        await websocket.send(json.dumps({"answer": response}))

start_server = websockets.serve(websocket_handler, "localhost", 8765)

def run_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server)
    loop.run_forever()

if __name__ == '__main__':
    t = Thread(target=run_websocket_server)
    t.start()
    t.join()