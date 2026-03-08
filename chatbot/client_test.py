import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "Explain the latest RBI guidelines on pre-sanctioned credit lines in banks",
          "top_k": 5}
    # json={"query": "What are the changes in UPI dispute resolution and refund process for FY 23-24?",
    #       "top_k": 5}
    # json={"query": "List transaction volumes for public sector banks in January 2026",
    #       "top_k": 5}
)

print("Raw response:", response.text)