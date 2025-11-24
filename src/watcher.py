# src/watcher.py
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from handlers_docx import anonymize_docx
from handlers_pdf import anonymize_pdf


INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
CONFIG_PATH = "config/rules.yaml"

class AnonymizeHandler(FileSystemEventHandler):
    def _wait_for_stable_file(self, path: Path, attempts: int = 6, delay: float = 0.5) -> bool:
        """Esperar a que el archivo deje de crecer y esté accesible.

        En Windows, los eventos de creación se disparan mientras la aplicación
        origen sigue escribiendo, lo que provoca errores de "Package not found"
        o "Permission denied" al intentar procesar el fichero de inmediato.
        Este método observa el tamaño en disco y verifica que se puede abrir
        el archivo antes de continuar.
        """

        for _ in range(attempts):
            if not path.exists():
                time.sleep(delay)
                continue

            try:
                size_before = path.stat().st_size
            except FileNotFoundError:
                time.sleep(delay)
                continue

            time.sleep(delay)

            try:
                size_after = path.stat().st_size
            except FileNotFoundError:
                continue

            if size_before == 0 or size_before != size_after:
                continue

            try:
                with path.open("rb"):
                    return True
            except OSError:
                time.sleep(delay)
                continue

        return False
    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        ext = path.suffix.lower()
        print(f"检测到新文件: {path}")

        if not self._wait_for_stable_file(path):
            print(f"文件仍在写入中，稍后重试: {path}")
            return

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
