"""
Database and extensions initialization
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import markdown
import bleach

db = SQLAlchemy()
login_manager = LoginManager()

def markdown_to_html(text):
    """Convert markdown text to safe HTML"""
    if not text:
        return ''
    
    # Convert markdown to HTML
    html = markdown.markdown(text, extensions=['nl2br', 'tables'])
    
    # Sanitize HTML to prevent XSS
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img',
        'table', 'thead', 'tbody', 'tr', 'th', 'td', 'hr'
    ]
    allowed_attributes = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title']
    }
    
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes, strip=True)

