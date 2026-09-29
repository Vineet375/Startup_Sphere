import os

views_path = r'e:\Projects\GLS SEM-7 Django Project\Startup_Sphere\startup_sphere\dashboard\views.py'

append_code = '''
from django.http import JsonResponse
import json
import random
import requests
import os
from django.views.decorators.csrf import csrf_exempt

@login_required
def settings_view(request):
    """
    User settings view for managing profile, theme preferences, and account details.
    """
    context = {
        'user': request.user,
    }
    return render(request, 'dashboard/settings.html', context)

def get_gemini_api_key():
    # Try to load from .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    keys = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY_'):
                    parts = line.strip().split('=')
                    if len(parts) == 2 and parts[1]:
                        keys.append(parts[1])
    
    if not keys:
        # Fallback to environment variables
        for i in range(1, 6):
            key = os.environ.get(f'GEMINI_API_KEY_{i}')
            if key:
                keys.append(key)
                
    if keys:
        return random.choice(keys)
    return None

@login_required
@csrf_exempt
def ai_chat(request):
    """
    Handles AI chatbot messages using rotating Gemini API keys.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
                
            api_key = get_gemini_api_key()
            if not api_key:
                return JsonResponse({'error': 'No API keys configured for the AI Assistant.'}, status=500)
                
            # Call Gemini API
            # model = gemini-1.5-flash (safe default)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": message}]
                }]
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                try:
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    return JsonResponse({'response': text_response})
                except (KeyError, IndexError):
                    return JsonResponse({'error': 'Unexpected response format from AI'}, status=500)
            else:
                return JsonResponse({'error': f'AI API error: {response.text}'}, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)
'''

with open(views_path, 'a') as f:
    f.write('\n' + append_code)
