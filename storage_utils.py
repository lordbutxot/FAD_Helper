"""
Storage utilities for persistent file uploads using Supabase Storage
Handles faction logo uploads to Supabase Storage buckets (persistent across deployments)
"""
import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename

# Storage client (initialized on first use)
_supabase_client = None

def get_supabase_client():
    """Get or create Supabase client"""
    global _supabase_client
    if _supabase_client is None:
        try:
            from supabase import create_client, Client
            url = current_app.config.get('SUPABASE_URL')
            key = current_app.config.get('SUPABASE_KEY')
            
            if url and key:
                _supabase_client = create_client(url, key)
                print("✅ Supabase storage client initialized")
            else:
                print("⚠️  Supabase credentials not configured - falling back to local storage")
        except ImportError:
            print("⚠️  Supabase library not installed - falling back to local storage")
        except Exception as e:
            print(f"⚠️  Error initializing Supabase client: {e}")
    
    return _supabase_client

def upload_faction_logo(file):
    """
    Upload faction logo to Supabase Storage
    Returns: (filename, public_url) tuple or (None, None) on error
    """
    if not file or file.filename == '':
        return None, None
    
    # Validate file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return None, None
    
    # Generate unique filename
    filename = f"{uuid.uuid4().hex}.{ext}"
    
    try:
        client = get_supabase_client()
        
        if client:
            # Upload to Supabase Storage
            bucket_name = current_app.config.get('SUPABASE_STORAGE_BUCKET', 'faction-logos')
            
            # Read file data
            file_data = file.read()
            
            # Upload to Supabase
            response = client.storage.from_(bucket_name).upload(
                path=filename,
                file=file_data,
                file_options={"content-type": f"image/{ext}"}
            )
            
            # Get public URL
            public_url = client.storage.from_(bucket_name).get_public_url(filename)
            
            print(f"✅ Uploaded logo to Supabase: {filename}")
            return filename, public_url
        else:
            # Fallback to local storage for development
            return _upload_local_fallback(file, filename)
            
    except Exception as e:
        print(f"❌ Error uploading to Supabase: {e}")
        # Attempt local fallback
        try:
            file.seek(0)  # Reset file pointer
            return _upload_local_fallback(file, filename)
        except:
            return None, None

def _upload_local_fallback(file, filename):
    """Fallback to local filesystem storage (for development)"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/faction_logos')
    os.makedirs(upload_folder, exist_ok=True)
    
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    print(f"ℹ️  Saved logo locally (dev mode): {filename}")
    # Return None for URL to use local path
    return filename, None

def delete_faction_logo(filename):
    """
    Delete faction logo from Supabase Storage
    """
    if not filename:
        return
    
    try:
        client = get_supabase_client()
        
        if client:
            bucket_name = current_app.config.get('SUPABASE_STORAGE_BUCKET', 'faction-logos')
            client.storage.from_(bucket_name).remove([filename])
            print(f"✅ Deleted logo from Supabase: {filename}")
        else:
            # Fallback to local deletion
            _delete_local_fallback(filename)
            
    except Exception as e:
        print(f"⚠️  Error deleting from Supabase: {e}")
        # Try local fallback
        _delete_local_fallback(filename)

def _delete_local_fallback(filename):
    """Fallback to delete from local filesystem"""
    try:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/faction_logos')
        filepath = os.path.join(upload_folder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"ℹ️  Deleted logo locally: {filename}")
    except Exception as e:
        print(f"⚠️  Error deleting local file: {e}")

def get_logo_url(filename):
    """
    Get the URL for a faction logo
    Returns either Supabase public URL or local path
    """
    if not filename:
        return None
    
    try:
        client = get_supabase_client()
        
        if client:
            bucket_name = current_app.config.get('SUPABASE_STORAGE_BUCKET', 'faction-logos')
            public_url = client.storage.from_(bucket_name).get_public_url(filename)
            return public_url
        else:
            # Fallback to local URL
            return f"/static/faction_logos/{filename}"
            
    except Exception as e:
        print(f"⚠️  Error getting logo URL: {e}")
        return f"/static/faction_logos/{filename}"
