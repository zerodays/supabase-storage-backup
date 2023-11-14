#!/usr/bin/env python3
import os
import zipfile
from supabase import create_client, Client

# Fetch inputs from environment variables
SUPABASE_URL = os.getenv(
    'SUPABASE_URL')
SUPABASE_SERVICE_ROLE = os.getenv(
    'SUPABASE_SERVICE_ROLE')
BACKUP_DIR = 'supabase-backup'
ZIP_FILENAME = os.getenv('ZIP_FILENAME', 'backup.zip')

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)


def download_objects(bucket_name, path="", created_dirs=set()):
    # Define the path for the current level
    current_path = os.path.join(BACKUP_DIR, bucket_name, path)
    if current_path not in created_dirs:
        os.makedirs(current_path, exist_ok=True)
        created_dirs.add(current_path)

    objects = supabase.storage.from_(bucket_name).list(path)

    for obj in objects:
        obj_name = obj['name']
        full_obj_path = os.path.join(path, obj_name)

        is_directory = obj['id'] is None

        # Recursively download directories
        if is_directory:
            print(f"Downloading directory: {full_obj_path}")
            download_objects(bucket_name, full_obj_path, created_dirs)
            continue

        file_path = os.path.join(current_path, obj_name)
        print(f"Downloading file: {file_path}")
        try:
            response = supabase.storage.from_(
                bucket_name).download(full_obj_path)
            with open(file_path, 'wb+') as f:
                f.write(response)
        except Exception as e:
            print(f"Error downloading {full_obj_path}: {e}")


def zip_backup():
    zip_filename = os.path.join(BACKUP_DIR, ZIP_FILENAME)
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(BACKUP_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, BACKUP_DIR))
    print(f"Backup zip created: {zip_filename}")


# Main execution
if __name__ == "__main__":
    buckets = supabase.storage.list_buckets()
    for bucket in buckets:
        download_objects(bucket.name)

    zip_backup()
