import os
import shutil
import subprocess
from pathlib import Path

# Pfade definieren
input_dir = Path(r"C:\Users\rsonnen\Desktop\Dokument_Analyse\docs")
output_dir = Path(r"C:\Users\rsonnen\Desktop\Sicherung")
converter_path = Path(r"C:\Users\rsonnen\Desktop\Dokument_Analyse\FileToPdfConverter 3.exe")

# Unterstützte Dateitypen
allowed_extensions = {'.docx', '.doc', '.rtf', '.txt', '.html', '.xlsx', '.xls'}

def main():
    # Durchlaufe alle Dateien im Eingabeverzeichnis
    for file_path in input_dir.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(input_dir)
            output_file_path = output_dir / relative_path.with_suffix('.pdf')
            output_file_path.parent.mkdir(parents=True, exist_ok=True)

            if file_path.suffix.lower() in allowed_extensions:
                print(f"Konvertiere: {file_path}")
                try:
                    subprocess.run([
                        str(converter_path),
                        str(file_path),
                        str(output_file_path)
                    ], check=True)
                    print(f"Fertig. PDF gespeichert als: {output_file_path}")
                except subprocess.CalledProcessError as e:
                    print(f"Fehler bei der Konvertierung von {file_path}: {e}")
            elif file_path.suffix.lower() == '.pdf':
                # Bereits vorhandene PDFs kopieren
                shutil.copy2(file_path, output_file_path)
                print(f"PDF kopiert nach: {output_file_path}")
