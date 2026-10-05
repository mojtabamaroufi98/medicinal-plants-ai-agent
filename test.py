from dotenv import load_dotenv
import os
import requests


load_dotenv()


def identify_plant(image_path):

    api_key1 = os.getenv("PLANTNET_API_KEY")

    url = "https://my-api.plantnet.org/v2/identify/all"

    params = {
        "api-key": api_key1,
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

        return response.json()

    except (requests.RequestException, FileNotFoundError) as error:

        return {
            "error": f"خطا در شناسایی گیاه: {error}"
        }


# =========================
# Test
# =========================

result = identify_plant("photo.jpg")

print(result)