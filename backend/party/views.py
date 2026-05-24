from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from groq import Groq
from .mock_swiggy import get_mock_restaurants

client = Groq(api_key=settings.GROQ_API_KEY)

@api_view(['POST'])
def plan_party(request):
    data = request.data
    guests = data.get('guests', [])
    budget = data.get('budget', 0)
    party_time = data.get('time', '')

    
    restaurants = get_mock_restaurants("party food", guests)

    # Step 2: Groq sab kuch karega - filtering + planning + message
    prompt = (
        "You are a smart party planning assistant.\n\n"
        f"Guests and their dietary needs:\n{guests}\n\n"
        f"Total Budget: Rs.{budget}\n"
        f"Party Time: {party_time}\n\n"
        f"Available Swiggy restaurants and menu:\n{restaurants['data']}\n\n"
        "Your tasks:\n"
        "1. Filter items that are SAFE for ALL guests simultaneously\n"
        "   - Jain guests: only isJainCompatible=true items\n"
        "   - Veg guests: only isVeg=true items\n"
        "   - Diabetic guests: only isDiabeticFriendly=true items\n"
        "   - Non-veg guests: any item is fine\n"
        "2. Pick best restaurant within budget\n"
        "3. Assign items per guest\n"
        "4. Calculate per-person bill split\n"
        "5. Return WhatsApp-ready party plan with emojis\n\n"
        "Output: WhatsApp message only."
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    return Response({
        "plan": response.choices[0].message.content,
        "guests": guests
    })