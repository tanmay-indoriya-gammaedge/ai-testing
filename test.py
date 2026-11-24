from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

messages = [{
            "role": "system",
            "content": "you are a racehorse expert. check everything on the internet before answering"
        }]

token_usage = None


def regular_resp():
    while True:
        user = input("user> ")

        if user.lower() in ["quit", "exit"]:
            print(f"you have used {token_usage} tokens for this chat.")
            break

        messages.append({
            "role":"user",
            "content":user
        })


        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages
        )

        assistant_reply = response.choices[0].message.content

        print(f"AI> {assistant_reply}")

        token_usage = response.usage.total_tokens

        messages.append({
            "role":"assistant",
            "content": assistant_reply
        })

def streamed_resp():
    while True:
        user = input("user> ")

        if user.lower() in ["quit", "exit"]:
            # print(f"you have used {token_usage} tokens for this chat.")
            break

        messages.append({
            "role":"user",
            "content":user
        })

        stream = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            stream=True
        )

        assistant_reply = ""

        print("AI> ", end="", flush=True)

        for chunk in stream:
            if chunk.choices:
                content = chunk.choices[0].delta.content

                if content:
                    print(content, end="", flush=True)
                    assistant_reply += content

        print(end="\n", flush=True)

        messages.append({
            "role":"assistant",
            "content": assistant_reply
        })
