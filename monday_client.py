import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")
URL = "https://api.monday.com/v2"

HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

DEALS_BOARD_ID = 5026565737
WORK_ORDERS_BOARD_ID = 5026565760


def fetch_board_items(board_id):
    query = f"""
    {{
      boards(ids: {board_id}) {{
        id
        name
        items_page(limit: 500) {{
          items {{
            id
            name
            column_values {{
              id
              text
              value
            }}
          }}
        }}
      }}
    }}
    """

    response = requests.post(URL, json={"query": query}, headers=HEADERS)
    return response.json()


def get_deals_data():
    return fetch_board_items(DEALS_BOARD_ID)


def get_work_orders_data():
    return fetch_board_items(WORK_ORDERS_BOARD_ID)
