import openai
import json
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


def home(request):
    return render(request, "chat/chat.html")


def initialize_conversation_history():
    return [
        {
            "role": "system",
            "content": "You are an affirming, positive assistant. You will provide uplifting affirmations and motivational quotes without offering therapeutic advice, regardless of the user's emotional state.",
        }
    ]


def enhance_prompt(user_prompt):
    if "sad" in user_prompt.lower() or "unhappy" in user_prompt.lower():
        enhanced_prompt = (
            f"The user mentioned feeling sad or unhappy. Do not offer any form of therapeutic advice or acknowledge sadness directly. "
            f"Instead, provide only positive, uplifting affirmations that boost the user's mood and a motivational quote to inspire them. "
            f"Make sure to keep the response cheerful and encouraging. "
            f"User's input: {user_prompt}"
        )
    elif "anxious" in user_prompt.lower() or "stressed" in user_prompt.lower():
        enhanced_prompt = (
            f"The user mentioned feeling anxious or stressed. Do not offer any therapeutic advice or acknowledge anxiety. "
            f"Provide calming and positive affirmations to help the user relax, and include an empowering quote. "
            f"Keep the tone light, soothing, and reassuring. "
            f"User's input: {user_prompt}"
        )
    elif "happy" in user_prompt.lower() or "excited" in user_prompt.lower():
        enhanced_prompt = (
            f"The user is feeling happy or excited. Reinforce their positive mood with encouraging affirmations and a cheerful, motivational quote. "
            f"Keep the response uplifting and inspiring. "
            f"User's input: {user_prompt}"
        )
    else:
        enhanced_prompt = (
            f"The user shared how they are feeling. Provide uplifting, encouraging affirmations and a motivational quote. "
            f"Keep the response light, positive, and cheerful. "
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
