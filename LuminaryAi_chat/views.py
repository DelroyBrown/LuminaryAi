# LuminaryAi_chat\views.py
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
            "content": "You are LuminaryAi, a supportive assistant. When the user expresses sadness or negative emotions, respond with empathy first, acknowledging their feelings before providing uplifting affirmations. Do not offer therapeutic advice or say you're glad when a user is feeling sad. When the user is happy, celebrate their joy and offer affirmations to reinforce it. Always include a motivational quote based on the user's mood.",
        }
    ]


def enhance_prompt(user_prompt):
    if any(term in user_prompt.lower() for term in negative_words):
        enhanced_prompt = (
            f"The user mentioned feeling sad, down, or unhappy. Start the response by acknowledging their feelings with empathy, "
            f"such as 'I'm sorry you're feeling this way' or 'It's okay to feel like this sometimes.' "
            f"Then, provide an uplifting message focusing on resilience, strength, and hope. "
            f"Include a motivational quote between ##quote_start## and ##quote_end## about overcoming challenges. "
            f"User's input: {user_prompt}"
        )
    elif any(term in user_prompt.lower() for term in positive_words):
        enhanced_prompt = (
            f"The user is feeling happy or excited. Start the response by celebrating their positive mood, such as 'That's wonderful to hear!' or 'I'm so glad you're feeling this way!' "
            f"Then, continue with affirmations about embracing joy and personal fulfillment. "
            f"Include a motivational quote between ##quote_start## and ##quote_end## about embracing happiness and growth. "
            f"User's input: {user_prompt}"
        )
    else:
        # Default enhancement for general feelings
        enhanced_prompt = (
            f"The user shared how they are feeling. Start by acknowledging their feelings in a neutral and empathetic tone, "
            f"such as 'I hear you' or 'It's okay to feel that way.' "
            f"Then, provide affirmations focusing on positivity, resilience, and personal growth. "
            f"Include a motivational quote between ##quote_start## and ##quote_end## that encourages strength and confidence. "
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
