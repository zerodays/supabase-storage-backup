import os
import zipfile
from pathlib import Path
from supabase import create_client, Client, StorageException
from supabase.lib.client_options import ClientOptions
import shutil
import time
import random
from typing import Optional

STORAGE_CLIENT_TIMEOUT = 60


def fetch_environment_variables() -> tuple[str, str, str, int]:
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        raise ValueError("SUPABASE_URL environment variable is required")
    supabase_service_role = os.getenv("SUPABASE_SERVICE_ROLE")
    if not supabase_service_role:
        raise ValueError("SUPABASE_SERVICE_ROLE environment variable is required")
    output_file_name = os.getenv("OUTPUT_ZIP_FILE_NAME", "supabase-storage-backup.zip")

    max_retries = int(os.getenv("SUPABASE_MAX_RETRIES", "3"))

    return (
        supabase_url,
        supabase_service_role,
        output_file_name,
        max_retries,
    )


def create_supabase_client(url: str, service_role: str) -> Client:
    return create_client(
        url,
        service_role,
        ClientOptions(
            storage_client_timeout=STORAGE_CLIENT_TIMEOUT,
        ),
    )


def retry_operation(operation, max_retries=3, initial_delay=1, max_delay=30):
    """Retry an operation with exponential backoff."""
    retries = 0
    while True:
        try:
            return operation()
        except (StorageException, TimeoutError) as e:
            retries += 1
            if retries > max_retries:
                raise

            # Calculate delay with jitter
            delay = min(
                initial_delay * (2 ** (retries - 1)) + random.uniform(0, 1), max_delay
            )
            print(
                f"Operation failed: {e}. Retrying in {delay:.2f} seconds... (Attempt {retries}/{max_retries})"
            )
            time.sleep(delay)


def download_objects(
    bucket_name: str,
    path: str = "",
    created_dirs: set[str] = set(),
    failed_downloads: Optional[list] = None,
):
    if failed_downloads is None:
        failed_downloads = []

    # Define the path for the current level
    current_path = Path("supabase-backup") / bucket_name / path
    if current_path not in created_dirs:
        current_path.mkdir(parents=True, exist_ok=True)
        created_dirs.add(current_path)

    try:
        # Use retry logic for listing objects
        objects = retry_operation(
            lambda: supabase.storage.from_(bucket_name).list(path),
            max_retries=max_retries,
        )

        for obj in objects:
            obj_name = obj["name"]
            full_obj_path = Path(path) / obj_name

            is_directory = obj["id"] is None

            # Recursively download directories
            if is_directory:
                print(f"Downloading directory: {full_obj_path}")
                download_objects(
                    bucket_name, str(full_obj_path), created_dirs, failed_downloads
                )
                continue

            file_path = current_path / obj_name
            try:
                # Use retry logic for downloading files
                response = retry_operation(
                    lambda: supabase.storage.from_(bucket_name).download(
                        str(full_obj_path)
                    ),
                    max_retries=max_retries,
                )
                with open(file_path, "wb+") as f:
                    f.write(response)
            except Exception as e:
                error_msg = f"Error downloading {bucket_name}/{full_obj_path}: {e}"
                print(error_msg)
                failed_downloads.append(error_msg)
    except Exception as e:
        error_msg = f"Error listing objects in {bucket_name}/{path}: {e}"
        print(error_msg)
        failed_downloads.append(error_msg)

    return failed_downloads


def zip_backup(zip_filename: str):
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk("supabase-backup"):
            for file in files:
                file_path = Path(root) / file
                if file_path == zip_filename:
                    continue
                zipf.write(file_path, file_path.relative_to("supabase-backup"))
    print(f"Backup zip created: {zip_filename}")


def cleanup():
    shutil.rmtree("supabase-backup")


def write_error_log(failed_items):
    if not failed_items:
        return

    with open("backup_errors.log", "w") as f:
        f.write("SUPABASE STORAGE BACKUP ERRORS\n")
        f.write("=============================\n\n")
        for item in failed_items:
            f.write(f"{item}\n")
    print(f"Error log written to backup_errors.log ({len(failed_items)} errors)")


# Main execution
if __name__ == "__main__":
    (
        supabase_url,
        supabase_service_role,
        output_file_name,
        max_retries,
    ) = fetch_environment_variables()

    supabase = create_supabase_client(supabase_url, supabase_service_role)

    failed_items = []
    try:
        buckets = retry_operation(
            lambda: supabase.storage.list_buckets(), max_retries=max_retries
        )

        for bucket in buckets:
            failed_downloads = download_objects(bucket.name)
            if failed_downloads:
                failed_items.extend(failed_downloads)

        zip_backup(output_file_name)

        if failed_items:
            write_error_log(failed_items)

        cleanup()

        if failed_items:
            print(
                f"Backup completed with {len(failed_items)} errors. See backup_errors.log for details."
            )
        else:
            print("Backup completed successfully!")

    except Exception as e:
        print(f"Critical error: {e}")
        write_error_log(failed_items)
