import ollama

def ask_model(question):
    response = ollama.chat(
        model="llama3.1:8b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI Delivery Copilot. "
                    "Give clear and concise project-management advice."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    return response["message"]["content"]

question = "What information should a project RAID log contain?"
answer = ask_model(question)

print("\nQUESTION:")
print(question)

print("\nANSWER:")
print(answer)