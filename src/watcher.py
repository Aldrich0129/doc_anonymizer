# src/watcher.py
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from handlers_docx import anonymize_docx
from handlers_pdf import anonymize_pdf
from config import load_rules


INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
CONFIG_PATH = "config/rules.yaml"

class AnonymizeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        ext = path.suffix.lower()
        print(f"检测到新文件: {path}")

        rel_name = path.name
        output_path = OUTPUT_DIR / rel_name

        try:
            if ext == ".docx":
                anonymize_docx(str(path), str(output_path), CONFIG_PATH)
            elif ext == ".pdf":
                anonymize_pdf(str(path), str(output_path), CONFIG_PATH)
            else:
                print(f"不支持的文件类型: {ext}")
                return
            print(f"已脱敏并保存到: {output_path}")
        except Exception as e:
            print(f"处理失败 {path}: {e}")

def start_watcher():
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    event_handler = AnonymizeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(INPUT_DIR), recursive=False)
    observer.start()
    print(f"开始监听文件夹: {INPUT_DIR.resolve()}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watcher()
