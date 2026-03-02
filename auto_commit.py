# auto_commit.py
import time
from pathlib import Path
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ===================== 配置部分 =====================
REPO_DIR = Path(r"d:\Documents\GitHub\JerryLogSupport.github.io")      # ← 改成你的仓库绝对路径！！
WATCH_FILES = [                                       # 只监控这些文件（可加多个）
    "mydata.xlsx",                                    # 你的 Excel 文件名
    "index.html"                                      # 主页文件
]
COMMIT_MESSAGE = "自动保存更新 - {filename}"

# 是否只监控特定文件（推荐），或整个文件夹（设为 True 则监控所有）
WATCH_ONLY_SPECIFIED = False

# ===================== 事件处理 =====================
class GitAutoCommitHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        relative_path = file_path.relative_to(REPO_DIR)

        # 如果设置了只监控特定文件，这里过滤
        if WATCH_ONLY_SPECIFIED:
            if relative_path.name not in WATCH_FILES:
                return

        print(f"检测到修改: {relative_path}")

        try:
            # git add
            subprocess.run(["git", "add", str(relative_path)], check=True, cwd=REPO_DIR)
            print("  已 git add")

            # git commit
            msg = COMMIT_MESSAGE.format(filename=relative_path.name)
            result = subprocess.run(
                ["git", "commit", "-m", msg],
                capture_output=True, text=True, cwd=REPO_DIR
            )

            if result.returncode == 0:
                print(f"  已 commit: {msg}")
            elif "nothing to commit" in result.stdout:
                print("  无实际变化，跳过 commit")
                return
            else:
                print("  commit 失败:", result.stderr.strip())
                return

            # git push
            push_result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True, text=True, cwd=REPO_DIR
            )

            if push_result.returncode == 0:
                print("  已 push 到 GitHub ✓")
            else:
                print("  push 失败:", push_result.stderr.strip())

        except Exception as e:
            print(f"发生错误: {e}")

# ===================== 主程序 =====================
if __name__ == "__main__":
    print(f"启动监控：{REPO_DIR}")
    print(f"监控文件：{WATCH_FILES if WATCH_ONLY_SPECIFIED else '整个文件夹'}")
    print("按 Ctrl+C 停止...\n")

    event_handler = GitAutoCommitHandler()
    observer = Observer()
    
    # 监控整个仓库目录（recursive=True 包括子文件夹）
    observer.schedule(event_handler, str(REPO_DIR), recursive=True)
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("监控已停止")
    observer.join()