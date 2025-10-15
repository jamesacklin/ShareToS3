# ShareToS3

A Sublime Text package for quickly uploading text files to S3-compatible storage and copying the public URL to your clipboard.

## Features

- Upload current buffer content to S3 with automatic timestamped filename
- Upload with custom filename via input panel
- Copy public URL to clipboard automatically
- Support for AWS S3 and S3-compatible storage (MinIO, DigitalOcean Spaces, etc.)
- AWS Signature Version 4 authentication

## Installation

### Via Package Control (Recommended)

1. Install [Package Control](https://packagecontrol.io/installation)
2. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
3. Run `Package Control: Install Package`
4. Search for "ShareToS3" and install

### Manual Installation

1. Clone this repository to your Sublime Text Packages directory
2. Restart Sublime Text

## Configuration

Configure your S3 settings via **Preferences → Package Settings → ShareToS3 → Settings - User**:

```json
{
  "s3_endpoint": "https://your-minio-server.com",
  "s3_username": "your-access-key",
  "s3_password": "your-secret-key",
  "s3_url_prefix": "https://your-minio-server.com",
  "s3_bucket": "your-bucket-name",
  "s3_region": "global"
}
```

### Settings Reference

- **s3_endpoint**: S3 endpoint URL (e.g., `https://s3.amazonaws.com` for AWS)
- **s3_username**: S3 access key ID
- **s3_password**: S3 secret access key
- **s3_url_prefix**: Public URL prefix for accessing uploaded files
- **s3_bucket**: S3 bucket name (optional, defaults to "uploads")
- **s3_region**: AWS region (optional, defaults to "global" for MinIO)

## Usage

### Upload with Auto-Generated Filename

1. Open or create a text file in Sublime Text
2. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
3. Run `ShareToS3: Upload`
4. File uploads with timestamp filename (e.g., `2024-01-15_14-30-25.txt`)
5. Public URL is copied to clipboard automatically

### Upload with Custom Filename

1. Open or create a text file in Sublime Text
2. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
3. Run `ShareToS3: Upload with Custom Name`
4. Enter desired filename in the input panel
5. File uploads and public URL is copied to clipboard

## Commands

- **ShareToS3: Upload** - Upload with auto-generated timestamp filename
- **ShareToS3: Upload with Custom Name** - Upload with custom filename

## Supported Storage Providers

- Amazon S3
- MinIO
- DigitalOcean Spaces
- Backblaze B2 (S3-compatible API)
- Any S3-compatible storage service

## Troubleshooting

### "Please configure S3 settings" Error

Make sure all required settings are configured:

- `s3_endpoint`
- `s3_username`
- `s3_password`
- `s3_url_prefix`

### "Buffer is empty" Error

The current file/buffer has no content. Add some text before uploading.

### Upload Fails

Check:

1. S3 credentials are correct
2. Bucket exists and is accessible
3. Network connectivity
4. S3 endpoint URL is correct

## License

MIT License
