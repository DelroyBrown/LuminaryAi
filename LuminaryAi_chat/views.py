import openai
import json
import os
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


def home(request):
    return render(request, "chat/chat.html")


def load_words_from_json(filename):
    filepath = os.path.join(settings.BASE_DIR, filename)
    with open(filepath, "r") as file:
        data = json.load(file)
    return data["words"]


positive_words = load_words_from_json("LuminaryAi_chat/data/positive_words.json")
negative_words = load_words_from_json("LuminaryAi_chat/data/negative_words.json")


def initialize_conversation_history():
    return [
        {
            "role": "system",
            "content": "You are LuminaryAi, a positive assistant that provides only uplifting affirmations and motivational quotes. Do not acknowledge or respond to emotions like sadness, anxiety, or depression. Avoid any form of therapeutic advice. Focus solely on empowering the user with affirmations of resilience, strength, and hope.",
        }
    ]


def enhance_prompt(user_prompt):
    if any(term in user_prompt.lower() for term in negative_words):
        enhanced_prompt = (
            f"The user mentioned feeling down, low, or even depressed. Do not acknowledge these emotions directly or offer any therapeutic advice. "
            f"Do not say you're sorry or that the user should seek help. Instead, provide empowering affirmations that remind the user of their strength, resilience, and potential for growth. "
            f"Offer a motivational quote focused on overcoming challenges and finding hope. "
            f"User's input: {user_prompt}"
        )
    elif any(term in user_prompt.lower() for term in positive_words):
        enhanced_prompt = (
            f"The user is feeling happy or excited. Reinforce their positive mood with affirmations that celebrate joy and personal fulfillment. "
            f"Include an uplifting quote about embracing happiness and growth. "
            f"User's input: {user_prompt}"
        )
    else:
        # Default enhancement for general feelings
        enhanced_prompt = (
            f"The user shared how they are feeling. Provide positive affirmations that focus on resilience, personal growth, and self-awareness. "
            f"Include a motivational quote that encourages strength and confidence. "
            f"User's input: {user_prompt}"
        )

    return enhanced_prompt


@csrf_exempt
def get_gpt_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_prompt = data.get("prompt")

            if not user_prompt:
                return JsonResponse({"error": "Prompt is required"}, status=400)

            enhanced_prompt = enhance_prompt(user_prompt)

            if "conversation" not in request.session:
                request.session["conversation"] = initialize_conversation_history()

            request.session["conversation"].append(
                {"role": "user", "content": enhanced_prompt}
            )

            response = client.chat.completions.create(
                model="gpt-4",
                messages=request.session["conversation"],
                max_tokens=2000,
                temperature=0.7,
            )

            gpt_response = response.choices[0].message.content

            request.session["conversation"].append(
                {"role": "assistant", "content": gpt_response}
            )

            return JsonResponse({"response": gpt_response})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
