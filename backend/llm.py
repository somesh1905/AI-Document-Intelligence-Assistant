
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def generate_response(prompt):
    """
    Send a prompt to Groq and return the generated answer.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set."
        )

    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        groq_api_key=api_key
    )

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":
    print("Testing Groq LLM...")

    answer = generate_response(
        "What is artificial intelligence?"
    )

    print("\nLLM Response:")
    print(answer)

    print("\nGroq LLM test completed successfully!")
