from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from groq import Groq

client = Groq(api_key=settings.GROQ_API_KEY)

@api_view(['POST'])
def plan_party(request):
    data = request.data
    guests = data.get('guests', [])
    budget = data.get('budget', 0)
    time = data.get('time', '')

    guest_list ="\n".join([f"- {g['name']}: {g['diet']}" for g in guests])

    prompt = f"""
    You are a party planning assistant.
    
    Guests and dietary preferences:
    {guest_list}
    
    Total Budget: Rs.{budget}
    Party Time: {time}
    
    Using Swiggy Food:
    1. Suggest conflict-free food items for ALL guests
    2. Calculate per-person cost
    3. Return a WhatsApp-ready party plan message
    
    Format output as WhatsApp message only.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens =1000,
    )
    result = response.choices[0].message.content
    return Response({"plan" : result})