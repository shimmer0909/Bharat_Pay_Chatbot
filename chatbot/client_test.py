# client_test.py

import requests

print("Starting client test...")

response = requests.post(
    "http://localhost:8000/answer",
    # json={"query": "Explain the latest RBI guidelines on pre-sanctioned credit lines in banks",
    #       "top_k": 5}
    # json={"query": "What are the changes in UPI dispute resolution and refund process for FY 23-24?",
    #       "top_k": 5}
    # json={"query": "List transaction volumes for public sector banks in January 2026",
    #       "top_k": 5}

    # json={
    #     "query": "What are recent RBI guidelines for UPI?",
    #     "role": "compliance",
    #     "top_k": 3
    # }
    json={
        "query": "What compliance obligations do banks and PSPs have under recent UPI circulars?",
        "role": "compliance",
        "top_k": 2
    }
)

print("Status code:", response.status_code)
print("Raw response:", response.text)