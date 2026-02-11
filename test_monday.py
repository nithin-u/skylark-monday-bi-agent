import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")

url = "https://api.monday.com/v2"

# GraphQL query to fetch items from your board
query = """
{
  boards(ids: 5026563433) {
    id
    name
    items_page(limit: 5) {
      items {
        id
        name
        column_values {
          id
          text
          value
        }
      }
    }
  }
}
"""

headers = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

response = requests.post(
    url,
    json={"query": query},
    headers=headers
)

print(response.json())
