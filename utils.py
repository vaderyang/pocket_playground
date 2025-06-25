from openai import OpenAI
import os

def call_llm(messages, stream=False):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"),
        base_url="http://localhost:1234/v1"
    )
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        stream=stream
    )
    
    if stream:
        return response
    else:
        return response.choices[0].message.content

if __name__ == "__main__":
    # Test the LLM call
    messages = [{"role": "user", "content": "In a few words, what's the meaning of life?"}]
    response = call_llm(messages)
    print(f"Prompt: {messages[0]['content']}")
    print(f"Response: {response}")
