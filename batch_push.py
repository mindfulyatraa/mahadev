import os
import subprocess
import time

def run_command(command):
    try:
        subprocess.check_call(command, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def batch_push():
    # 1. Initialize Git
    print("🧹 Cleaning old git...")
    if os.path.exists(".git"):
        # Windows requires specific command to remove hidden .git
        os.system("rmdir /s /q .git")
    
    print("🌱 Re-initializing Git...")
    run_command("git init")
    run_command("git branch -M main")
    run_command("git remote add origin https://github.com/mindfulyatraa/mahadev.git")

    # 2. Add Base Files (Code & Config)
    print("📄 Adding base files...")
    base_files = ["youtube_uploader.py", "requirements.txt", ".gitignore", "client_secrets.json", ".github"]
    for f in base_files:
        if os.path.exists(f):
            run_command(f"git add {f}")
    
    run_command('git commit -m "Base setup: Code and Config"')
    print("☁️  Pushing base code...")
    run_command("git push -u origin main")

    # 3. Add Videos in Batches
    video_folder = "videos"
    if not os.path.exists(video_folder):
        print("No videos folder found!")
        return

    all_files = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if os.path.isfile(os.path.join(video_folder, f))]
    total_files = len(all_files)
    batch_size = 50
    
    print(f"🎥 Found {total_files} videos. Starting batch push (Batch size: {batch_size})...")

    for i in range(0, total_files, batch_size):
        batch = all_files[i : i + batch_size]
        print(f"📦 Processing batch {i//batch_size + 1} ({len(batch)} files)...")
        
        # Add files
        for file_path in batch:
            # Escape spaces for shell
            safe_path = file_path.replace(" ", "?") # git add handles wildcards or we can quote. 
            # Actually subprocess with quotes is better
            subprocess.call(['git', 'add', file_path])

        # Commit
        run_command(f'git commit -m "Add videos batch {i}-{i+len(batch)}"')
        
        # Push
        print("🚀 Pushing batch...")
        success = False
        attempts = 0
        while not success and attempts < 3:
            success = run_command("git push")
            if not success:
                print("⚠️ Push failed. Retrying in 5 seconds...")
                time.sleep(5)
                attempts += 1
        
        if not success:
            print("❌ Critical Batch Push Failed. Stopping.")
            break
        
        print("✅ Batch Pushed!")

    print("🎉 All Batches Complete!")

if __name__ == "__main__":
    batch_push()
