# models/llm.py

import ollama

def generate_response(prompt: str):

    response = ollama.chat(
        # model="mistral",  # Responds in ~75 secs
        # model="llama3.2:3b",  # Responds in ~85 secs
        model="phi3:mini",  # Response in ~70 secs
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "num_predict": 150
        },
        stream=True
    )

    return response["message"]["content"]


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


# from transformers import pipeline

# # load once at startup
# generator = pipeline(
#     "text2text-generation",
#     model="google/flan-t5-base",
#     max_length=512
# )

# def generate_response(prompt: str):
#     result = generator(
#         prompt,
#         max_new_tokens=200,
#         do_sample=True,
#         temperature=0.3
#     )
#     return result[0]["generated_text"]

