from pathlib import Path
import shutil
import subprocess

url = "https://x.com/ScobarHacker/status/2112005120368005179?s=20"
destino = Path("pasta_video_DL")
destino.mkdir(parents=True, exist_ok=True)

if shutil.which("yt-dlp") is None:
    raise RuntimeError(
        "yt-dlp não foi encontrado no PATH. "
        "Instale com: python -m pip install -U yt-dlp"
    )

if shutil.which("ffmpeg") is None:
    raise RuntimeError(
        "FFmpeg não foi encontrado no PATH."
    )

comando = [
    "yt-dlp",
    
    "--cookies", "cookies.txt", 

    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "--merge-output-format", "mp4",

    # Comando que impede a sobrescrita de arquivos já baixados
    "--no-overwrites",

    # Nome dinâmico utilizando o ID do post (tweet) para evitar conflitos
    "-o", str(destino / "video_X_%(id)s.%(ext)s"),

    url,
]

try:
    subprocess.run(comando, check=True)
    print("Processo do yt-dlp finalizado com sucesso.")

except subprocess.CalledProcessError as erro:
    print(f"Falha no yt-dlp. Código de saída: {erro.returncode}")

except Exception as erro:
    print(f"Erro: {type(erro).__name__}: {erro}")