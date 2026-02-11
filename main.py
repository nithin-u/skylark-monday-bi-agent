from fastapi import FastAPI
from pydantic import BaseModel
from monday_client import get_deals_data
from data_processor import extract_items_to_dataframe
from ai_agent import generate_pipeline_insight
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
import datetime

app = FastAPI()

# Serve static frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/app")
def serve_frontend():
    return FileResponse("static/index.html")


class Question(BaseModel):
    query: str


@app.get("/")
def root():
    return {"message": "Monday BI Agent Running"}


def prepare_dataframe():
    deals_json = get_deals_data()
    df = extract_items_to_dataframe(deals_json)

    df = df.rename(columns={
        "numeric_mm0ftv1c": "deal_value",
        "color_mm0fs0mg": "deal_stage",
        "color_mm0fc1sr": "deal_status",
        "color_mm0ftdf7": "sector",
        "date_mm0fck9a": "tentative_close_date"
    })

    df["deal_value"] = pd.to_numeric(df["deal_value"], errors="coerce")
    df["tentative_close_date"] = pd.to_datetime(
        df["tentative_close_date"], errors="coerce"
    )

    return df


@app.post("/ask")
def ask_question(question: Question):

    df = prepare_dataframe()
    query = question.query.lower()

    # ---------------------------
    # Sector filtering
    # ---------------------------
    for sector in df["sector"].dropna().unique():
        if sector.lower() in query:
            df = df[df["sector"].str.lower() == sector.lower()]
            break

    # ---------------------------
    # Quarter filtering
    # ---------------------------
    if "this quarter" in query:
        now = datetime.datetime.now()
        current_quarter = (now.month - 1) // 3 + 1
        start_month = 3 * (current_quarter - 1) + 1
        start_date = datetime.datetime(now.year, start_month, 1)
        end_date = start_date + datetime.timedelta(days=90)

        df = df[
            (df["tentative_close_date"] >= start_date) &
            (df["tentative_close_date"] <= end_date)
        ]

    # ---------------------------
    # If no data after filtering
    # ---------------------------
    if df.empty:
        return {
            "message": "No deals match your query filters."
        }

    # ---------------------------
    # Advanced Business Metrics
    # ---------------------------
    total_value = df["deal_value"].sum()

    won_df = df[df["deal_stage"].str.contains("Won", na=False)]
    lost_df = df[df["deal_stage"].str.contains("Lost", na=False)]
    on_hold_df = df[df["deal_stage"].str.contains("Hold", na=False)]

    won_value = won_df["deal_value"].sum()
    lost_value = lost_df["deal_value"].sum()

    total_deals = df.shape[0]
    won_count = won_df.shape[0]

    win_rate = (won_count / total_deals * 100) if total_deals > 0 else 0
    on_hold_count = on_hold_df.shape[0]

    summary = {
        "total_pipeline_value": total_value,
        "won_value": won_value,
        "lost_value": lost_value,
        "win_rate_percent": round(win_rate, 2),
        "on_hold_deals": on_hold_count,
        "stage_distribution": df["deal_stage"].value_counts().to_dict(),
        "sector_distribution": df["sector"].value_counts().to_dict()
    }

    insight = generate_pipeline_insight(summary)

    return {
        "filtered_summary": summary,
        "executive_insight": insight
    }


# ---------------------------
# Required for Render
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
