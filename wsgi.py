"""
WSGI entry point for production deployment
"""

from app import create_app
from config import get_config

config = get_config()
app = create_app(config)

if __name__ == '__main__':
    app.run()
