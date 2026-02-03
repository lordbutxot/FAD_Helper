# Supabase Storage Setup for Faction Logos

## Problem: Logos Disappearing on Deployment

On platforms like Render.com, the file system is **ephemeral** - it gets wiped on every deployment. This means any uploaded faction logos stored locally in `static/faction_logos/` are lost.

## Solution: Supabase Storage

We use Supabase Storage buckets for persistent file storage across deployments.

## Setup Instructions

### 1. Create Storage Bucket in Supabase

1. Go to your Supabase project dashboard
2. Navigate to **Storage** in the left sidebar
3. Click **New Bucket**
4. Create a bucket named: `faction-logos`
5. Set it to **Public** (so logo URLs work without auth)

### 2. Configure Storage Policies

In the Supabase Storage settings for the `faction-logos` bucket:

**Create these policies:**

#### Policy 1: Public Read Access
```sql
CREATE POLICY "Public can view faction logos"
ON storage.objects FOR SELECT
USING (bucket_id = 'faction-logos');
```

#### Policy 2: Authenticated Users Can Upload
```sql
CREATE POLICY "Authenticated users can upload logos"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'faction-logos' 
  AND auth.role() = 'authenticated'
);
```

#### Policy 3: Users Can Update Their Uploads
```sql
CREATE POLICY "Users can update their logos"
ON storage.objects FOR UPDATE
USING (bucket_id = 'faction-logos')
WITH CHECK (bucket_id = 'faction-logos');
```

#### Policy 4: Users Can Delete
```sql
CREATE POLICY "Users can delete logos"
ON storage.objects FOR DELETE
USING (bucket_id = 'faction-logos');
```

### 3. Get Your Supabase Credentials

1. In Supabase dashboard, go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://[your-project].supabase.co`
   - **Project API Key** (anon/public key)

### 4. Add Environment Variables to Render

In your Render.com dashboard:

1. Go to your web service
2. Navigate to **Environment**
3. Add these variables:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

4. Click **Save Changes**
5. Redeploy your application

## How It Works

### Upload Flow
1. User uploads faction logo via web form
2. `storage_utils.py` uploads file to Supabase Storage
3. Supabase returns a public URL for the file
4. Both `logo_filename` and `logo_url` are saved to database
5. Templates display logo using the Supabase URL

### Fallback for Development
- If Supabase credentials aren't configured, system falls back to local file storage
- Perfect for local development without needing Supabase setup

### Migration
- `migrate_logo_url.py` adds the `logo_url` column to existing databases
- Runs automatically on deployment via `start.sh`

## Testing

After setup, upload a faction logo and verify:
1. Logo appears correctly on dashboard
2. Logo URL in database starts with `https://[your-project].supabase.co/storage/`
3. Logo persists after redeployment

## Troubleshooting

### Logo not uploading
- Check Render environment variables are set correctly
- Check Supabase bucket exists and is public
- Check storage policies are configured

### Logo URL is local path
- Supabase credentials not configured - check environment variables
- System falling back to local storage (dev mode)

### 404 on logo URL
- Bucket not set to public
- Storage policies not configured correctly
- Wrong bucket name in config

## Benefits

✅ **Persistent** - Logos survive deployments and rebuilds
✅ **Fast** - Served from Supabase CDN
✅ **Scalable** - No impact on your application server
✅ **Free** - Supabase free tier includes 1GB storage
✅ **Reliable** - Professional CDN infrastructure
