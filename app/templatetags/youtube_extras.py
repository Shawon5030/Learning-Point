from django import template
import re

register = template.Library()

@register.filter
def youtube_id(value):
    """
    Extract YouTube video ID from various URL formats.
    
    Supported formats:
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://www.youtube.com/live/VIDEO_ID
    - Just the VIDEO_ID (11 characters)
    """
    if not value:
        return ''
    
    # Trim whitespace
    value = value.strip()
    
    # If it's already just an ID (11 characters, no slashes, no dots)
    if len(value) == 11 and not '/' in value and not '.' in value:
        return value
    
    # Handle youtu.be/ format (including with parameters)
    match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', value)
    if match:
        return match.group(1)
    
    # Handle youtube.com/watch?v= format
    match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', value)
    if match:
        return match.group(1)
    
    # Handle youtube.com/embed/ format
    match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]{11})', value)
    if match:
        return match.group(1)
    
    # Handle youtube.com/shorts/ format
    match = re.search(r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})', value)
    if match:
        return match.group(1)
    
    # Handle youtube.com/live/ format
    match = re.search(r'youtube\.com/live/([a-zA-Z0-9_-]{11})', value)
    if match:
        return match.group(1)
    
    # If nothing matches, return the original
    return value