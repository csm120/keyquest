KeyQuest Source Code Package
============================

IMPORTANT: EXTRACTION INSTRUCTIONS
===================================

This ZIP file contains a folder structure with subdirectories:

KeyQuest-Source-v[VERSION]-[DATE]/
    keyquest.pyw
    README.md
    requirements.txt
    modules/
        (Python module files)
    games/
        (Game module files)
    Sentences/
        (Sentence files)
    docs/
        (Documentation files)

CORRECT EXTRACTION METHODS:

Windows File Explorer:
    1. Right-click the ZIP file
    2. Select "Extract All..."
    3. Choose destination folder
    4. Click "Extract"
    This will create the folder structure correctly.

Windows PowerShell:
    Expand-Archive -Path "KeyQuest-Source-v[VERSION]-[DATE].zip" -DestinationPath "."

7-Zip (if installed):
    Right-click ZIP > 7-Zip > Extract Here
    OR
    Right-click ZIP > 7-Zip > Extract to "KeyQuest-Source-v[VERSION]-[DATE]\"

INCORRECT METHODS TO AVOID:
    - Do NOT use command-line unzip with options that flatten the structure
    - Do NOT manually drag files out of the ZIP viewer
    - If files appear with backslashes in their names (like "folder\file.txt"),
      your extraction tool is not preserving the directory structure

VERIFY EXTRACTION:
    After extraction, you should see:
    - A folder named KeyQuest-Source-v[VERSION]-[DATE]
    - Inside that folder: keyquest.pyw and SUBDIRECTORIES (modules, games, etc.)
    - NOT individual files with backslashes in their names

If you see files with names like "KeyQuest-Source-v[VERSION]-[DATE]\requirements.txt"
all in one folder, the extraction failed. Try a different extraction method.

For setup instructions:
- In this repository: `docs/dev/DEVELOPER_SETUP.md`
- In an extracted source package: `DEVELOPER_SETUP.md`
