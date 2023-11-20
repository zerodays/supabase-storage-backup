# Supabase Backup GitHub Action

This GitHub Action is designed to automate the process of backing up files from Supabase storage, compressing them into a ZIP file in the process.

## Features

- **Automated Backup:** Automatically backs up files from Supabase storage.
- **ZIP Compression:** Compresses the backup into a ZIP file for efficient storage.

## Prerequisites

Before you can use this GitHub Action, ensure you have:

- A GitHub account with a repository for which you want to set up this action.
- Access to a Supabase project, including the Project URL and Service Role Key.

## Inputs

The action accepts the following inputs:

- `SUPABASE_URL`: **Required**. Your Supabase Project URL.
- `SUPABASE_SERVICE_ROLE`: **Required**. Your Supabase Service Role Key.
- `OUTPUT_ZIP_FILE_NAME`: The name of the ZIP file to be created. Defaults to `supabase-storage-backup.zip`.

## Setup

1. **Add the Action to Your Workflow:**
   Copy the provided action YAML configuration into your repository's `.github/workflows` directory. You can name the file as per your preference (e.g., `supabase_backup.yml`).

2. **Configure the Action:**
   Customize the inputs as per your requirements. Required inputs must be provided for the action to work correctly.

3. **Set Environment Variables:**
   Store your `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE` as secrets in your GitHub repository and reference them in your workflow file. This approach keeps sensitive information secure.

Example workflow file:

   ```yaml
   name: Supabase Storage Backup

   on:
      schedule:
         - cron: "0 0 * * *"

   jobs:
      backup:
         runs-on: ubuntu-latest

         steps:
            - name: Checkout Repository
              uses: actions/checkout@v2

            - name: Supabase Backup
              uses: zerodays/supabase-storage-backup@v1
               with:
                  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
                  SUPABASE_SERVICE_ROLE: ${{ secrets.SUPABASE_SERVICE_ROLE }}
                  OUTPUT_ZIP_FILE_NAME: backup.zip
            - name: Save Backup
              uses: actions/upload-artifact@v2
              with:
                  name: backup
                  path: backup.zip
   ```



## Usage

Once set up, the action will run as per the triggers defined in your workflow file. 

The action will create a ZIP file containing all files in your Supabase storage bucket. The ZIP file will be stored on `OUTPUT_ZIP_FILE_NAME`.
What is done with the artifact is up to you. You can download it manually or use it in a subsequent workflow step. For example, you could upload the ZIP file to a cloud storage provider like AWS S3.


## Support and Contribution

For support, start by checking the GitHub issues for similar problems. If your issue is unique, feel free to open a new issue.

Contributions to improve this GitHub Action are welcome.