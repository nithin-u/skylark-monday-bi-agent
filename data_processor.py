import pandas as pd


def extract_items_to_dataframe(board_json):
    items = board_json["data"]["boards"][0]["items_page"]["items"]

    records = []

    for item in items:
        record = {"Deal Name": item["name"]}

        for col in item["column_values"]:
            record[col["id"]] = col["text"]

        records.append(record)

    df = pd.DataFrame(records)
    return df


def calculate_pipeline_summary(df):
    # Clean numeric column
    if "masked_deal_value" in df.columns:
        df["masked_deal_value"] = pd.to_numeric(
            df["masked_deal_value"], errors="coerce"
        )

    total_pipeline_value = df["masked_deal_value"].sum()

    stage_distribution = df["deal_stage"].value_counts()

    return {
        "total_pipeline_value": total_pipeline_value,
        "stage_distribution": stage_distribution.to_dict(),
    }
