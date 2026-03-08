# models/llm.py
# import openai
# import os

# openai.api_key = "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"  # os.getenv("OPENAI_API_KEY")

# def generate_answer(prompt: str, max_tokens: int = 300) -> str:
#     """
#     Generate answer from OpenAI GPT model using the new API (>=1.0)
#     """
#     response = openai.chat.completions.create(
#         model="gpt-4-o",
#         messages=[
#             {"role": "system", "content": "You are an expert assistant."},
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=max_tokens,
#         temperature=0
#     )

    # Extract assistant message
    # return response.choices[0].message.content.strip()


from llama_cpp import Llama
import os

# path to your downloaded model
LLAMA_MODEL_PATH = "./models/vicuna-7B-q4_0.bin"

llm = Llama(model_path=LLAMA_MODEL_PATH)

def generate_answer(prompt: str, max_tokens: int = 300) -> str:
    """
    Generate response from a local LLM using llama_cpp
    """
    response = llm(prompt, max_tokens=max_tokens)
    return response["choices"][0]["text"].strip()