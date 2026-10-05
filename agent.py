import json
import mimetypes
import os
from PIL import Image
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
    base_url="https://router.requesty.ai/v1",
    timeout=60.0
)

MODEL_NAME ="gemma-4-31b-it"


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

    converted_path = "plantnet_image.jpg"

    try:

        # =========================
        # Convert Image to JPEG
        # =========================

        image = Image.open(image_path)

        # اگر تصویر شفافیت داشته باشد،
        # آن را به RGB تبدیل می‌کنیم
        if image.mode != "RGB":
            image = image.convert("RGB")

        image.save(
            converted_path,
            format="JPEG",
            quality=95
        )

        image.close()

        # =========================
        # Send Image to PlantNet
        # =========================

        with open(
            converted_path,
            "rb"
        ) as image_file:

            files = [
                (
                    "images",
                    (
                        "plant.jpg",
                        image_file,
                        "image/jpeg"
                    )
                )
            ]

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

        # =========================
        # Check Response
        # =========================

        if response.status_code != 200:

            return {
                "error": (
                    f"PlantNet Error "
                    f"{response.status_code}\n"
                    f"{response.text}"
                )
            }

        result = response.json()

    except FileNotFoundError:

        return {
            "error": "فایل تصویر پیدا نشد."
        }

    except Exception as error:

        return {
            "error": (
                f"خطا در پردازش تصویر:\n"
                f"{error}"
            )
        }

    # =========================
    # Extract Results
    # =========================

    plants = []

    for item in result.get(
        "results",
        []
    ):

        species = item.get(
            "species",
            {}
        )

        plants.append({
            "scientific_name": species.get(
                "scientificNameWithoutAuthor"
            ),

            "common_names": species.get(
                "commonNames",
                []
            ),

            "confidence": item.get(
                "score"
            )
        })

    return {
        "best_match": result.get(
            "bestMatch"
        ),

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
            "content": """
تو یک دستیار پژوهشی درباره گیاهان دارویی هستی.

وظیفه تو ارائه اطلاعات علمی، آموزشی و پژوهشی درباره گیاهان است.

قوانین:
- پاسخ را به زبان فارسی بده.
- برای اطلاعات علمی درباره گیاهان، در صورت نیاز از ابزار search_plant استفاده کن.
- اطلاعات منابع علمی را خلاصه و قابل فهم بیان کن.
- درباره درمان قطعی بیماری‌ها ادعا نکن.
- تشخیص پزشکی یا تجویز دارو انجام نده.
- اگر شواهد علمی کافی نیست، صریحاً اعلام کن.
- بین کاربرد سنتی و شواهد علمی تفاوت بگذار.
- میزان اطمینان و محدودیت اطلاعات را بیان کن.
"""
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

        # =========================
        # No tool call
        # =========================

        if not message.tool_calls:

            return message.content

        # =========================
        # Tool calls
        # =========================

        messages.append(message)

        for tool_call in message.tool_calls:

            if tool_call.function.name == "search_plant":

                arguments = json.loads(
                    tool_call.function.arguments
                )

                plant_name = arguments.get(
                    "plant_name"
                )

                search_result = search_plant(
                    plant_name
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(
                            search_result,
                            ensure_ascii=False
                        )
                    }
                )

    return (
        "نتوانستم در محدوده درخواست‌های "
        "مجاز، گزارش پژوهشی را کامل کنم."
    )


def research_identified_plant(plant_result):

    if "error" in plant_result:
        return plant_result["error"]

    best_match = plant_result.get(
        "best_match"
    )

    if not best_match:

        return (
            "گیاه با اطمینان کافی شناسایی نشد."
        )

    question = f"""
یک تصویر گیاه توسط سیستم شناسایی گیاه بررسی شده است.

نام علمی پیشنهادی سیستم:

{best_match}

لطفاً درباره همین گیاه یک گزارش پژوهشی کوتاه تهیه کن.

حتماً ابتدا با استفاده از ابزار search_plant
منابع علمی مرتبط با این نام علمی را جستجو کن.

گزارش نهایی به فارسی باشد و شامل:

1. نام علمی
2. نام‌های رایج در صورت وجود
3. معرفی کوتاه گیاه
4. ترکیبات یا ویژگی‌های مهم در صورت وجود شواهد
5. کاربردهای سنتی
6. کاربردهایی که در مطالعات علمی بررسی شده‌اند
7. خلاصه شواهد علمی
8. هشدارها و محدودیت‌ها
9. میزان اطمینان به شناسایی تصویر

توجه:

این گزارش صرفاً پژوهشی و آموزشی است.

تشخیص پزشکی، تجویز دارو و توصیه درمانی ارائه نکن.

اگر شواهد علمی کافی نیست، آن را صریحاً بیان کن.

بین «کاربرد سنتی» و «شواهد علمی» تفاوت واضح بگذار.

اطلاعات را بر اساس منابعی که از Europe PMC دریافت می‌کنی تهیه کن.
"""

    return run_agent(question)