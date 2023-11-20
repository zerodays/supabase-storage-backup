import os
import zipfile
from pathlib import Path
from supabase import create_client, Client, StorageException
import shutil


def fetch_environment_variables() -> tuple[str, str, str]:
    supabase_url = os.getenv('SUPABASE_URL')
    if not supabase_url:
        raise ValueError("SUPABASE_URL environment variable is required")
    supabase_service_role = os.getenv('SUPABASE_SERVICE_ROLE')
    if not supabase_service_role:
        raise ValueError(
            "SUPABASE_SERVICE_ROLE environment variable is required"
        )
    output_file_name = os.getenv(
        'OUTPUT_ZIP_FILE_NAME', 'supabase-storage-backup.zip')

    return supabase_url, supabase_service_role, output_file_name


def create_supabase_client(url: str, service_role: str) -> Client:
    return create_client(url, service_role)


def download_objects(
    bucket_name: str,
    path: str = "",
    created_dirs: set[str] = set()
):
    # Define the path for the current level
    current_path = Path('supabase-backup') / bucket_name / path
    if current_path not in created_dirs:
        current_path.mkdir(parents=True, exist_ok=True)
        created_dirs.add(current_path)

    try:
        objects = supabase.storage.from_(bucket_name).list(path)
        for obj in objects:
            obj_name = obj['name']
            full_obj_path = Path(path) / obj_name

            is_directory = obj['id'] is None

            # Recursively download directories
            if is_directory:
                print(f"Downloading directory: {full_obj_path}")
                download_objects(
                    bucket_name,
                    str(full_obj_path),
                    created_dirs
                )
                continue

            file_path = current_path / obj_name
            try:
                response = supabase.storage.from_(
                    bucket_name
                ).download(str(full_obj_path))
                with open(file_path, 'wb+') as f:
                    f.write(response)
            except StorageException as e:
                print(f"Error downloading {full_obj_path}: {e}")
    except StorageException as e:
        print(f"Error listing objects in {bucket_name}: {e}")


def zip_backup(zip_filename: str):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk('supabase-backup'):
            for file in files:
                file_path = Path(root) / file
                if file_path == zip_filename:
                    continue
                zipf.write(file_path, file_path.relative_to('supabase-backup'))
    print(f"Backup zip created: {zip_filename}")


def cleanup():
    shutil.rmtree('supabase-backup')


# Main execution
if __name__ == "__main__":
    supabase_url, \
        supabase_service_role, \
        output_file_name = fetch_environment_variables()
    supabase = create_supabase_client(supabase_url, supabase_service_role)

    try:
        buckets = supabase.storage.list_buckets()
        for bucket in buckets:
            download_objects(bucket.name)

        zip_backup(output_file_name)
        cleanup()
    except StorageException as e:
        print(f"Error: {e}")
