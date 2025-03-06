# Using SFTP with Visual Studio Code for PythonAnywhere Deployment

You're absolutely right! Using SFTP (Secure File Transfer Protocol) with Visual Studio Code is a much easier way to deploy your project to PythonAnywhere. This guide will walk you through setting up and using SFTP to directly upload and sync your files.

## Advantages of Using SFTP

1. **Direct File Transfer**: Upload files directly from VS Code to PythonAnywhere without needing GitHub as an intermediary
2. **Selective Uploads**: Choose which files to upload rather than pushing everything
3. **Sync Capability**: Keep your local and remote directories in sync
4. **Visual Interface**: See your remote files alongside your local files
5. **Immediate Updates**: Changes are reflected immediately on PythonAnywhere

## Step 1: Install the SFTP Extension in VS Code

1. Open VS Code
2. Click on the Extensions icon in the sidebar (or press Ctrl+Shift+X)
3. Search for "SFTP" 
4. Install the "SFTP" extension by Natizyskunk (or another popular SFTP extension)
5. Reload VS Code if prompted

## Step 2: Get Your PythonAnywhere SFTP Credentials

1. Log in to your PythonAnywhere account
2. Go to the "Consoles" tab
3. Click on "SFTP" in the "Other" section
4. Note down the following information:
   - **Username**: JuggleAgent
   - **Host**: ssh.pythonanywhere.com
   - **Port**: 22
   - **Password**: Your PythonAnywhere password (By.jV7&9nC.HALA)

## Step 3: Configure SFTP in VS Code

1. In VS Code, open your project folder (sales_agent)
2. Press F1 (or Ctrl+Shift+P) to open the command palette
3. Type "SFTP: Config" and select it
4. This will create a `.vscode/sftp.json` file with default settings
5. Replace the contents with the following configuration:

```json
{
    "name": "PythonAnywhere",
    "host": "ssh.pythonanywhere.com",
    "protocol": "sftp",
    "port": 22,
    "username": "JuggleAgent",
    "password": "By.jV7&9nC.HALA",
    "remotePath": "/home/JuggleAgent/SalesAgentJoline",
    "uploadOnSave": false,
    "ignore": [
        ".vscode",
        ".git",
        ".DS_Store",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache",
        ".env"
    ]
}
```

6. Save the file

## Step 4: Create the Remote Directory Structure

Before uploading files, you need to make sure the target directory exists on PythonAnywhere:

1. Log in to PythonAnywhere
2. Go to the "Consoles" tab
3. Start a new Bash console
4. Run the following commands:

```bash
cd
mkdir -p SalesAgentJoline
mkdir -p SalesAgentJoline/attachments
mkdir -p SalesAgentJoline/templates
mkdir -p SalesAgentJoline/config
mkdir -p SalesAgentJoline/handlers
mkdir -p SalesAgentJoline/models
mkdir -p SalesAgentJoline/services
```

## Step 5: Upload Your Files

There are several ways to upload your files using the SFTP extension:

### Method 1: Upload the Entire Project

1. Press F1 (or Ctrl+Shift+P) to open the command palette
2. Type "SFTP: Upload Project" and select it
3. Wait for the upload to complete
4. You'll see progress notifications in the bottom right corner

### Method 2: Upload Specific Files or Folders

1. Right-click on a file or folder in the Explorer
2. Select "SFTP: Upload"
3. The file or folder will be uploaded to the corresponding location on PythonAnywhere

### Method 3: Sync Local to Remote

1. Press F1 (or Ctrl+Shift+P) to open the command palette
2. Type "SFTP: Sync Local -> Remote" and select it
3. This will synchronize your local project with the remote server, uploading new or changed files

## Step 6: Configure the Web App on PythonAnywhere

After uploading your files, you need to configure the web app:

1. Log in to PythonAnywhere
2. Go to the "Web" tab
3. Click on your web app (JuggleAgent.pythonanywhere.com)
4. In the "Code" section:
   - Set "Source code" to: `/home/JuggleAgent/SalesAgentJoline`
   - Set "Working directory" to: `/home/JuggleAgent/SalesAgentJoline`
5. In the "Virtualenv" section:
   - Set it to: `/home/JuggleAgent/salesagent_venv_py38`
6. In the "WSGI configuration file" section:
   - Click on the WSGI file link
   - Update it to use the correct path and import your app

## Step 7: Set Up Auto-Sync (Optional)

If you want files to automatically upload whenever you save them:

1. Open the `.vscode/sftp.json` file
2. Change `"uploadOnSave": false` to `"uploadOnSave": true`
3. Save the file

Now, whenever you save a file in VS Code, it will automatically be uploaded to PythonAnywhere.

## Step 8: Explore Remote Files (Optional)

You can also browse and edit remote files directly:

1. Press F1 (or Ctrl+Shift+P) to open the command palette
2. Type "SFTP: List" and select it
3. This will open a view of your remote files
4. You can browse, open, edit, and save remote files directly

## Step 9: Reload Your Web App

After uploading your files:

1. Go to the "Web" tab on PythonAnywhere
2. Click the "Reload" button
3. Visit your site at https://juggleagent.pythonanywhere.com/

## Tips for Effective SFTP Usage

1. **Selective Uploads**: Only upload what you need. For example, don't upload virtual environments or large binary files.

2. **Exclude Sensitive Files**: Make sure to exclude sensitive files like `.env` from uploads by adding them to the "ignore" list in your SFTP configuration.

3. **Test Locally First**: Always test your changes locally before uploading them to PythonAnywhere.

4. **Check Permissions**: If you encounter permission issues, you may need to adjust file permissions on PythonAnywhere:
   ```bash
   chmod -R 755 ~/SalesAgentJoline
   ```

5. **Use Sync Carefully**: The sync feature is powerful but can overwrite files. Make sure you understand which direction you're syncing (local to remote or remote to local).

6. **Create Backups**: Before making major changes, create a backup of your remote files:
   ```bash
   cd ~
   cp -r SalesAgentJoline SalesAgentJoline_backup
   ```

## Troubleshooting SFTP Issues

1. **Connection Issues**:
   - Make sure your internet connection is stable
   - Verify your username and password are correct
   - Check if PythonAnywhere is experiencing any service issues

2. **Permission Denied**:
   - Make sure you have the correct permissions on PythonAnywhere
   - Check if the target directory exists

3. **Upload Failures**:
   - Try uploading smaller batches of files
   - Check if you have enough disk space on PythonAnywhere

4. **Path Issues**:
   - Verify that the "remotePath" in your SFTP configuration is correct
   - Make sure all necessary directories exist on the remote server

## Conclusion

Using SFTP with Visual Studio Code is indeed a much easier way to deploy your project to PythonAnywhere compared to using GitHub. It gives you direct control over file transfers and allows for immediate updates to your deployment.

Once you've set up SFTP, you can focus on developing your application locally and easily push changes to PythonAnywhere whenever you're ready, without having to go through the extra steps of committing to Git and pulling on the server.