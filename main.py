import json
import os

import requests
from dotenv import load_dotenv
from openai import OpenAI


# =========================
# Environment
# =========================

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
plantNet_api_key = os.getenv("PLANTNET_API_KEY")


# =========================
# AI Client
# =========================

client = OpenAI(
    api_key=api_key,
    base_url="https://router.requesty.ai/v1"
)

MODEL_NAME = "gemma-4-31b-it"


# =========================
# System Prompt
# =========================

system_prompt = """
تو یک دستیار پژوهشی گیاهان دارویی هستی.

وظیفه تو ارائه اطلاعات علمی و پژوهشی درباره گیاهان دارویی است.
در مورد اینکه برای چه بیماری هایی خوب است هم توضیح بده
و اگر کاربر برای یک بیماری، گیاه دارویی خواست، چند گیاه
را با درنظر گرفتن قوانین به او معرفی کن.

قوانین:
- تشخیص پزشکی نده.
- ادعای درمان قطعی نکن.
- فقط کاربردهایی را گزارش کن که برای آن‌ها شواهد علمی وجود دارد.
- کیفیت یا میزان شواهد را در بخش مدارک علمی توضیح بده.
- هشدارها، محدودیت‌های مصرف و خطرات احتمالی را ذکر کن.
- همیشه به زبان فارسی پاسخ بده.
"""


# =========================
# PlantNet
# =========================

def identify_plant(image_path):

    url = "https://my-api.plantnet.org/v2/identify/all"

    params = {
        "api-key": plantNet_api_key,
        "lang": "en",
        "nb-results": 3
    }

    try:

        with open(image_path, "rb") as image:

            files = {
                "images": image
            }

            data = {
                "organs": "auto"
            }

            response = requests.post(
                url,
                params=params,
                files=files,
                data=data,
                timeout=30
            )

        response.raise_for_status()

        result = response.json()

    except (requests.RequestException, FileNotFoundError) as error:

        return {
            "error": f"خطا در شناسایی گیاه: {error}"
        }

    plants = []

    for item in result.get("results", []):

        species = item.get("species", {})

        plants.append({
            "scientific_name": species.get(
                "scientificNameWithoutAuthor"
            ),
            "common_names": species.get(
                "commonNames", []
            ),
            "confidence": item.get("score")
        })

    return {
        "best_match": result.get("bestMatch"),
        "plants": plants
    }


# =========================
# Scientific Search
# =========================

def search_plant(plant_name):

    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    params = {
        "query": f'"{plant_name}" AND (medicinal OR herbal OR phytotherapy)',
        "format": "json",
        "resultType": "core",
        "pageSize": 3
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as error:

        return {
            "error": f"خطا در اتصال به منبع علمی: {error}"
        }

    articles = []

    for article in data["resultList"]["result"]:

        articles.append({
            "title": article.get("title"),
            "abstract": article.get("abstractText"),
            "year": article.get("pubYear"),
            "journal": article.get("journalTitle"),
            "doi": article.get("doi")
        })

    return {
        "plant_name": plant_name,
        "articles": articles
    }


# =========================
# Agent Tools
# =========================

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_plant",
            "description": "برای دریافت اطلاعات پژوهشی درباره یک گیاه دارویی استفاده می‌شود.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plant_name": {
                        "type": "string",
                        "description": "نام علمی یا نام گیاه دارویی"
                    }
                },
                "required": ["plant_name"]
            }
        }
    }
]


# =========================
# Agent
# =========================

def run_agent(user_question):

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    for _ in range(3):

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools
        )

        message = response.choices[0].message

        if not message.tool_calls:

            return message.content

        messages.append(message)

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print("\n🔧 Tool Called:", tool_name)

            if tool_name == "search_plant":

                plant_name = arguments["plant_name"]

                print("🌱 Plant:", plant_name)

                tool_result = search_plant(
                    plant_name
                )

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        tool_result,
                        ensure_ascii=False
                    )
                })

    return "Agent نتوانست پاسخ نهایی تولید کند."


# =========================
# Main
# =========================

def main():

    print("===================================")
    print("🌿 Medicinal Plants AI Agent")
    print("===================================")

    print("\n1. پرسش درباره گیاهان دارویی")
    print("2. شناسایی گیاه از روی عکس")

    choice = input("\nانتخاب شما: ")

    # -------------------------
    # Text Question
    # -------------------------

    if choice == "1":

        user_question = input(
            "\nسؤال خود را وارد کنید: "
        )

        answer = run_agent(user_question)

        print("\n==============================")
        print(" پاسخ Agent:")
        print("==============================")

        print(answer)

    # -------------------------
    # Image Identification
    # -------------------------

    elif choice == "2":

        image_path = input(
            "\nمسیر عکس گیاه را وارد کنید: "
        )

        result = identify_plant(image_path)

        if "error" in result:

            print("\n❌", result["error"])
            return

        print("\n==============================")
        print("🌱 نتایج شناسایی")
        print("==============================")

        for plant in result["plants"]:

            print(
                f"{plant['scientific_name']} "
                f"-> {plant['confidence']:.2%}"
            )

        best_match = result.get("best_match")

        if best_match:

            print(
                f"\n🔎 پیشنهاد اصلی Pl@ntNet: "
                f"{best_match}"
            )

        else:

            print(
                "\n⚠️ گیاه با اطمینان کافی شناسایی نشد."
            )

    else:

        print("\n❌ انتخاب نامعتبر است.")


# =========================
# Run
# =========================

if __name__ == "__main__":
    main()