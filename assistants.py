import openai
import os
from openai import OpenAI
from dotenv import load_dotenv, dotenv_values 
import time
# loading variables from .env file
load_dotenv() 


client = OpenAI(api_key=os.getenv("API_KEY"))

assistant_prop_id = "asst_ufufmyqiucnAgWcq6nks0Jf8"
assistant_ww1exp_id = "asst_z3kMZJUvk2KKaShwgG6pijSP"


# Function to send messages and get responses
def chat_with_assistant(user_message, assistant_id, thread_id):
    # Add user message to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

    # Run the assistant on this thread (using the full context)
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Wait for the response
    while run.status not in ["completed", "failed"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    # Get all messages in the thread
    messages = client.beta.threads.messages.list(thread_id=thread_id)

    # Extract and return the latest assistant message
    for message in messages.data:  # Reverse to get the latest message first
        if message.role == "assistant":
            return message.content[0].text.value  # Extract text response

    return "No response from the assistant."


