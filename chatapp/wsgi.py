"""
WSGI config for chatapp project.
"""

import os
from django.core.wsgi import get_wsgi_application
from pathlib import Path

# Load environment variables for Vercel
try:
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parent.parent
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatapp.settings')

application = get_wsgi_application()

# Vercel requires 'app' as the handler
app = application
