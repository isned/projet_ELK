from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class LogstashHandler(FileSystemEventHandler):
    """Gestionnaire pour détecter les nouveaux fichiers dans un dossier."""
    def __init__(self, logstash_path, config_file):
        self.logstash_path = logstash_path
        self.config_file = config_file

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.csv'):
            print(f"Nouveau fichier détecté : {event.src_path}")
            self.run_logstash()

    def run_logstash(self):
        """Démarre Logstash avec le fichier de configuration."""
        try:
            print("Démarrage de Logstash...")
            subprocess.run(
                [f"{self.logstash_path}/bin/logstash", "-f", self.config_file],
                check=True
            )
            print("Logstash a terminé son exécution.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de Logstash : {e}")

def start_observer(directory_to_watch, logstash_path, config_file):
    """Démarre l'observateur pour surveiller les fichiers dans un dossier."""
    event_handler = LogstashHandler(logstash_path, config_file)
    observer = Observer()
    observer.schedule(event_handler, path=directory_to_watch, recursive=False)
    observer.start()
    print(f"Surveillance démarrée sur : {directory_to_watch}")
    return observer
