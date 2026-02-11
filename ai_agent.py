import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_pipeline_insight(summary_data):

    try:
        prompt = f"""
        You are a business intelligence assistant for founders.

        Here is pipeline summary data:

        Total Pipeline Value: {summary_data['total_pipeline_value']}

        Stage Distribution: {summary_data['stage_distribution']}

        Sector Distribution: {summary_data['sector_distribution']}

        Provide:
        - Executive summary
        - Key risks
        - Opportunities
        - Observations about sector performance
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception:
        # Fallback summary if OpenAI fails
        return generate_rule_based_summary(summary_data)


def generate_rule_based_summary(summary_data):

    total = summary_data["total_pipeline_value"]
    top_sector = max(summary_data["sector_distribution"], key=summary_data["sector_distribution"].get)

    return f"""
    Executive Summary:
    The total pipeline value stands at {total:.2f}. 
    The dominant sector in the pipeline is {top_sector}. 

    Key Observations:
    - Strong concentration in top sector.
    - Significant deal volume across multiple stages.
    - Potential risk if conversion from early stages is low.

    Recommendation:
    Focus on accelerating mid-stage deals and monitor sector concentration risk.
    """
