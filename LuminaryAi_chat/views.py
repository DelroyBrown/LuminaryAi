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
            "content": "You are LuminaryAi, a positive assistant that provides only uplifting affirmations and motivational quotes. Do not acknowledge or respond to emotions like sadness, anxiety, or depression. Avoid any form of therapeutic advice. Focus solely on empowering the user with affirmations of resilience, strength, and hope.",
        }
    ]


def enhance_prompt(user_prompt):
    if any(
        term in user_prompt.lower()
        for term in ["sad", "unhappy", "depressed", "down", "hopeless"]
    ):
        enhanced_prompt = (
            f"The user mentioned feeling down, low, or even depressed. Do not acknowledge these emotions directly or offer any therapeutic advice. "
            f"Do not say you're sorry or that the user should seek help. Instead, provide empowering affirmations that remind the user of their strength, resilience, and potential for growth. "
            f"Offer a motivational quote focused on overcoming challenges and finding hope. "
            f"User's input: {user_prompt}"
        )
    elif "anxious" in user_prompt.lower() or "stressed" in user_prompt.lower():
        enhanced_prompt = (
            f"The user mentioned feeling anxious or stressed. Do not acknowledge these emotions directly. "
            f"Do not offer any therapeutic advice. Respond only with calming affirmations about the user's ability to find peace and strength within. "
            f"Include a motivational quote focused on inner calm and resilience. "
            f"User's input: {user_prompt}"
        )
    elif "happy" in user_prompt.lower() or "excited" in user_prompt.lower():
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
