import os
import sys
import json
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import functools
from mistral.tools import get_definition, get_random_word
from colorama import Fore, Style

# Settings for the Mistral LLM
api_key = os.environ["MISTRAL_API_KEY"]
if not api_key:
    api_key = input(Fore.YELLOW + "Please input your Mistral AI key: " + Style.RESET_ALL)
client = MistralClient(api_key=api_key)

model = "mistral-large-latest"
temperature = 0.0
top_p = 1
max_tokens = 1024

messages = [
    ChatMessage(role="system", content="You are an AI assistant by Mistral AI. ")
]

# Load available tools
with open('./mistral/tools.json') as f:
    tools = json.load(f)

names_to_functions = {
    "get_definition": functools.partial(get_definition),
    "get_random_word": functools.partial(get_random_word)
}

def send_message(message):
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

    for response in client.chat_stream(**model_params):

        # If the response is not a tool call, print out the response
        if response.choices[0].delta.tool_calls is None:
            print(response.choices[0].delta.content, end="")
            sys.stdout.flush()

        # If response is a tool call, apply tool call and add to message
        elif response.choices[0].delta.tool_calls:
            tool_call = response.choices[0].delta.tool_calls[0]
            print(tool_call)
            function_name = tool_call.function.name
            function_params = json.loads(tool_call.function.arguments)

            # Execute the function
            function_result = names_to_functions[function_name](**function_params)
            print(function_result)

            # Create a new user message with the function result
            new_message = ChatMessage(role="user", content=function_result)
            messages.append(new_message)
            print(messages)

            # Send the new message back to the Mistral model
            for response in client.chat_stream(model=model, messages=messages):
                print(response.choices[0].delta.content, end="")
                sys.stdout.flush()

def main():
    print(Fore.YELLOW + "Welcome to the terminal chatbot! Type your message and press enter." + Style.RESET_ALL)
    while True:
        try:
            user_input = input("\n" + Fore.YELLOW + "\n You: " + Style.RESET_ALL)
            send_message(user_input)
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)

if __name__ == "__main__":
    main()