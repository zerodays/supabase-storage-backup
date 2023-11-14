# Supabase Backup GitHub Action

This GitHub Action is designed to automate the process of backing up files from Supabase storage, compressing them into a ZIP file, and then committing the ZIP file as an artifact. It's a robust solution for ensuring your Supabase data is regularly and securely backed up.

## Features

- **Automated Backup:** Automatically backs up files from Supabase storage.
- **ZIP Compression:** Compresses the backup into a ZIP file for efficient storage.
- **Artifact Commit:** Commits the ZIP file as an artifact for easy access and tracking.

## Prerequisites

Before you can use this GitHub Action, ensure you have:

- A GitHub account with a repository for which you want to set up this action.
- Access to a Supabase project, including the Project URL and Service Role Key.

## Inputs

The action accepts the following inputs:

- `SUPABASE_URL`: **Required**. Your Supabase Project URL.
- `SUPABASE_SERVICE_ROLE`: **Required**. Your Supabase Service Role Key.
- `ZIP_FILENAME`: The name for the output ZIP file. Default is `backup.zip`.

## Setup

1. **Add the Action to Your Workflow:**
   Copy the provided action YAML configuration into your repository's `.github/workflows` directory. You can name the file as per your preference (e.g., `supabase_backup.yml`).

2. **Configure the Action:**
   Customize the inputs as per your requirements. Required inputs must be provided for the action to work correctly.

3. **Set Environment Variables:**
   Store your `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE` as secrets in your GitHub repository and reference them in your workflow file. This approach keeps sensitive information secure.

## Usage

Once set up, the action will run as per the triggers defined in your workflow file. By default, it will:

1. Set up a Python environment.
2. Install necessary Python dependencies.
3. Set the current date as an environment variable.
4. Run the backup and zip process.
5. Upload the backup ZIP file as an artifact, tagged with the current date and time for easy identification.

## Customization

You can modify the action to suit your needs. Possible customizations include changing the backup frequency, modifying the backup script, or altering the ZIP file naming convention.

## Support and Contribution

For support, start by checking the GitHub issues for similar problems. If your issue is unique, feel free to open a new issue.

Contributions to improve this GitHub Action are welcome.