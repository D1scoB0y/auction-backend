#!/bin/bash

TIMESTAMP=$(date +%Y-%m-%d)
BACKUP_DIR="/home/backend_admin/dumps"
DATABASE_NAME="auction_db"
BACKUP_FILE="$BACKUP_DIR/$TIMESTAMP.sql"
DIRECTORY_ID="11bNhBWYhXggcqvHK986DqXXqW2j5Pxaq"

# Save file to /home/user/dumps with creation date in title
pg_dump -U auction_admin -h 0.0.0.0 $DATABASE_NAME > $BACKUP_FILE

# Upload file to google drive
gdrive files upload --parent $DIRECTORY_ID $BACKUP_FILE

# Remove file from local storage
rm $BACKUP_FILE

# Calculate the date 7 days ago in the format "Y-m-d"
SEVEN_DAYS_AGO=$(date -d "7 days ago" +%Y-%m-%d)

# List all files in the specified directory and filter out the files created 7 days ago or earlier
FILES_TO_DELETE=$(gdrive files list --query "'$DIRECTORY_ID' in parents" --skip-header | awk -v date="$SEVEN_DAYS_AGO" '$6 <= date { print $1 }')

for FILE_ID in $FILES_TO_DELETE; do
    gdrive files delete "$FILE_ID"
done
