# Script: Automated Trash Folder Cleaner (Excluding Shared Path)

## Script Purpose

This script is designed to help you free up disk space by automatically finding and deleting `.Trash-1000` folders within your `/home/ubuntu/` directory. It specifically **excludes** any `.Trash-1000` folders located under `/home/ubuntu/shared/`, ensuring shared data remains untouched. For each found folder, it will show its current size, ask for your confirmation, and then **permanently delete the entire folder**.

**WARNING:** This script uses `rm -rf`, which is a powerful command. Deleting files or directories with `rm -rf` is **permanent and cannot be undone**. Please exercise extreme caution and ensure you understand what the script does before running it.

## Understanding the `.Trash-1000` Folder

When you delete a file or folder from a location like your project directories while working in a **Jupyter Notebook environment** (or other graphical file management tools), the system often creates a hidden folder named `.Trash-1000` in that specific directory. This acts as a local "Recycle Bin" for items deleted from that spot, allowing temporary storage before permanent removal. The `1000` in the name usually refers to your user ID. This script targets and removes these temporary `.Trash-1000` folders to reclaim disk space.

## How to Create and Run the Script

Follow these steps to create the script file and execute it in your terminal.

### 1. Create the Script File

You can create the script file by directly pasting the entire command block below into your terminal. This method uses a "here document" to write the multi-line script content into a new file named `delete_specific_trash_folders.sh`.

```bash
cat << 'EOF' > delete_specific_trash_folders.sh
#!/bin/bash

echo "Script will find all '.Trash-1000' folders under /home/ubuntu/ (excluding /home/ubuntu/shared/) and offer to delete them."
echo "This operation will permanently delete the ENTIRE found '.Trash-1000' folders and cannot be undone!"
echo "" # Empty line for readability

# Path to exclude from search
EXCLUDE_PATH="/home/ubuntu/shared"

# Find all .Trash-1000 folders under /home/ubuntu/, excluding EXCLUDE_PATH
# Using -path to exclude the specific directory
TRASH_FOLDERS=($(find /home/ubuntu -type d -name ".Trash-1000" -not -path "${EXCLUDE_PATH}/*" 2>/dev/null))

if [ ${#TRASH_FOLDERS[@]} -eq 0 ]; then
    echo "No '.Trash-1000' folders found under /home/ubuntu/ (excluding '$EXCLUDE_PATH/'). Script finished."
    exit 0
fi

echo "Found the following '.Trash-1000' folders to process:"
for folder in "${TRASH_FOLDERS[@]}"; do
    echo "- $folder"
done
echo ""

# Loop through each found trash folder
for TRASH_FOLDER_FULL_PATH in "${TRASH_FOLDERS[@]}"; do
    echo "--- Processing: '$TRASH_FOLDER_FULL_PATH' ---"

    # --- Display disk usage BEFORE deletion ---
    echo "--- Disk Usage BEFORE Deletion ---"
    if [ -d "$TRASH_FOLDER_FULL_PATH" ]; then
        echo "Current disk usage of '$TRASH_FOLDER_FULL_PATH':"
        du -sh "$TRASH_FOLDER_FULL_PATH"
        echo "" # Empty line for readability

        # Get user confirmation for this specific folder
        read -p "Do you want to proceed with deleting the ENTIRE folder '$TRASH_FOLDER_FULL_PATH'? (yes/no): " response

        # Convert response to lowercase
        response=$(echo "$response" | tr '[:upper:]' '[:lower:]')

        if [[ "$response" == "yes" ]]; then
            echo "Starting deletion of: '$TRASH_FOLDER_FULL_PATH'"
            # --- Deleting the entire folder ---
            rm -rf "$TRASH_FOLDER_FULL_PATH"

            if [ $? -eq 0 ]; then
                echo "Folder successfully deleted: '$TRASH_FOLDER_FULL_PATH'"
            else
                echo "ERROR: An issue occurred while deleting the folder: '$TRASH_FOLDER_FULL_PATH'."
                echo "Permissions or another problem might be present. Please check manually."
            fi
        else
            echo "Deletion cancelled for '$TRASH_FOLDER_FULL_PATH'."
        fi
    else
        echo "ERROR: Folder '$TRASH_FOLDER_FULL_PATH' not found or disappeared unexpectedly. Skipping."
    fi

    echo "" # Empty line for readability

    # --- Display disk usage AFTER deletion (or cancellation) ---
    echo "--- Disk Usage AFTER Operation ---"
    if [ -d "$TRASH_FOLDER_FULL_PATH" ]; then
        echo "Folder '$TRASH_FOLDER_FULL_PATH' still exists (deletion was cancelled or failed):"
        du -sh "$TRASH_FOLDER_FULL_PATH"
    else
        echo "Folder '$TRASH_FOLDER_FULL_PATH' no longer exists. Space has been reclaimed."
    fi
    echo "" # Empty line for readability
done

echo "Script finished."
EOF
```

### 2. Make the Script Executable

After creating the file, you need to give it permission to run as a program. Open your terminal and run the following command in the directory where you saved `delete_specific_trash_folders.sh`:

```bash
chmod +x delete_specific_trash_folders.sh
```

### 3. Run the Script

Once the script is executable, you can run it from your terminal:

```bash
./delete_specific_trash_folders.sh
```

The script will then proceed to find the relevant `.Trash-1000` folders (excluding the shared path), display their sizes, and prompt you for confirmation for each one before performing any deletion.