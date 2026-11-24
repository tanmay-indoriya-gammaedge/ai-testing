import os
import json
from groq import Groq
from dotenv import load_dotenv

from response_format import tools, TaskResponse

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"

messages = [
    {
        "role": "system",
        "content": "You are a playful AI assistant. Be weird."
    }
]

token_usage = 0


# Stubbed function
def get_user_profile(user_id):
    return {
        "user_id": user_id,
        "name": "Tanmay",
        "role": "Backend Developer"
    }


def streamed_resp():
    global token_usage

    while True:
        user = input("user> ")

        if user.lower() in ["quit", "exit"]:
            print(f"\nTotal tokens used: {token_usage}")
            break

        messages.append({
            "role": "user",
            "content": user
        })

        # Initial API request
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            stream=True
        )

        assistant_reply = ""
        tool_calls = {}
        usage = None

        print("AI> ", end="", flush=True)

        for chunk in resp:

            if chunk.usage:
                usage = chunk.usage
                token_usage += usage.total_tokens

            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # Stream normal text
            if delta.content:
                print(delta.content, end="", flush=True)
                assistant_reply += delta.content

            # Collect tool calls
            if delta.tool_calls:
                for tool_delta in delta.tool_calls:

                    index = tool_delta.index

                    if index not in tool_calls:
                        tool_calls[index] = {
                            "id": "",
                            "type": "function",
                            "function": {
                                "name": "",
                                "arguments": ""
                            }
                        }

                    current = tool_calls[index]

                    if tool_delta.id:
                        current["id"] += tool_delta.id

                    if tool_delta.function:
                        if tool_delta.function.name:
                            current["function"]["name"] += (
                                tool_delta.function.name
                            )

                        if tool_delta.function.arguments:
                            current["function"]["arguments"] += (
                                tool_delta.function.arguments
                            )

        print(flush=True)

        # No tool calls: save normal response
        if not tool_calls:
            messages.append({
                "role": "assistant",
                "content": assistant_reply
            })
            continue

        # Save assistant's tool request
        messages.append({
            "role": "assistant",
            "content": assistant_reply or None,
            "tool_calls": list(tool_calls.values())
        })

        # Execute tools
        for call in tool_calls.values():

            function_name = call["function"]["name"]

            args = json.loads(
                call["function"]["arguments"]
            )

            if function_name == "get_user_profile":
                result = get_user_profile(args["user_id"])

            else:
                raise ValueError(f"Unknown function: {function_name}")

            # Append tool result
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": json.dumps(result)
            })

        # Final response after tool execution
        final = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            stream=True
        )

        final_reply = ""

        for chunk in final:

            if chunk.usage:
                token_usage += chunk.usage.total_tokens

            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                print(content, end="", flush=True)
                final_reply += content

        print(flush=True)

        messages.append({
            "role": "assistant",
            "content": final_reply
        })