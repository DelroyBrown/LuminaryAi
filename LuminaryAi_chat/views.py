# LuminaryAi_chat\views.py
import openai
import json
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


def home(request):
    return render(request, "chat/chat.html")


# Initialize a session variable for conversation history
def initialize_conversation_history():
    return [
        {"role": "system", "content": "You are a helpful assistant."}
    ]  # Optional system prompt


@csrf_exempt
def get_gpt_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            prompt = data.get("prompt")

            # Check for session conversation history
            if "conversation" not in request.session:
                request.session["conversation"] = initialize_conversation_history()

            # Append the user's new message to the conversation
            request.session["conversation"].append({"role": "user", "content": prompt})

            # Send the conversation history to the GPT model
            response = client.chat.completions.create(
                model="gpt-4",  # Or use "gpt-4o-mini" if available
                messages=request.session[
                    "conversation"
                ],  # Include the full conversation
                max_tokens=2000,
                temperature=0.7,
            )

            # Get the assistant's reply
            gpt_response = response.choices[0].message.content

            # Add the assistant's reply to the conversation history
            request.session["conversation"].append(
                {"role": "assistant", "content": gpt_response}
            )

            # Return the GPT response to the frontend
            return JsonResponse({"response": gpt_response})

        except Exception as e:
            # Log the error for debugging
            print(f"Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
