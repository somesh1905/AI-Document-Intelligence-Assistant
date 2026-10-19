import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set in the .env file."
    )


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    groq_api_key=GROQ_API_KEY
)


def generate_response(prompt):
    """
    Send the prompt to the Groq LLM
    and return the generated answer.
    """

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":

    print("Testing Groq LLM...")
    print("--------------------------------")

    test_prompt = "What is artificial intelligence?"

    answer = generate_response(
        test_prompt
    )

    print("\nLLM Response:")
    print("--------------------------------")
    print(answer)

    print("\nGroq LLM test completed successfully!")