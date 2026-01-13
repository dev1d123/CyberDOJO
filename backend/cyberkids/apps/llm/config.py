
from django.conf import settings

def get_openrouter_url():
    return getattr(settings, 'OPENROUTER_URL', 'https://openrouter.ai/api/v1/chat/completions')

def get_openrouter_api_key():
    return getattr(settings, 'OPENROUTER_API_KEY', '')
