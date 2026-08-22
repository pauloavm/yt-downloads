from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from pytubefix import YouTube
from pytubefix.cli import on_progress


# -------------------------------------------------------------------
# Configurações
# -------------------------------------------------------------------

# Cole aqui a URL de um vídeo cujo download seja autorizado.
URL_VIDEO = "https://www.youtube.com/watch?v=zaDhi2fY_RQ"

PASTA_DESTINO = Path("pasta_video_DL")

# Cliente usado pelo pytubefix.
CLIENTE_YOUTUBE = "WEB"

# Altere para True somente se a documentação do pytubefix
# solicitar um PO Token manual.
USAR_PO_TOKEN_MANUAL = False


# -------------------------------------------------------------------
# Exceções personalizadas
# -------------------------------------------------------------------

class ErroBotYouTube(RuntimeError):
    """Indica que o YouTube bloqueou a requisição automatizada."""


class ErroFFmpeg(RuntimeError):
    """Indica que houve um problema com o FFmpeg."""


# -------------------------------------------------------------------
# Funções auxiliares
# -------------------------------------------------------------------

def url_valida(url: str) -> bool:
    """
    Verifica se a URL pertence ao YouTube e utiliza HTTP ou HTTPS.
    """

    try:
        partes = urlparse(url.strip())
    except ValueError:
        return False

    dominio = (partes.hostname or "").lower()

    dominios_validos = {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtu.be",
    }

    return (
        partes.scheme in {"http", "https"}
        and dominio in dominios_validos
    )


def formatar_duracao(segundos: int | None) -> str:
    """
    Converte uma duração em segundos para HH:MM:SS ou MM:SS.
    """

    if segundos is None:
        return "Duração desconhecida"

    horas, resto = divmod(int(segundos), 3600)
    minutos, segundos_restantes = divmod(resto, 60)

    if horas > 0:
        return (
            f"{horas:02d}:"
            f"{minutos:02d}:"
            f"{segundos_restantes:02d}"
        )

    return f"{minutos:02d}:{segundos_restantes:02d}"


def construir_video(url: str) -> YouTube:
    """
    Cria o objeto YouTube usando a configuração definida.
    """

    argumentos = {
        "client": CLIENTE_YOUTUBE,
        "on_progress_callback": on_progress,
    }

    if USAR_PO_TOKEN_MANUAL:
        argumentos["use_po_token"] = True

    return YouTube(url, **argumentos)


def verificar_erro_bot(erro: Exception) -> None:
    """
    Substitui mensagens extensas do YouTube por uma orientação objetiva.
    """

    mensagem = str(erro).lower()

    marcadores = (
        "detected as a bot",
        "po token",
        "potoken",
        "proof of origin",
    )

    if any(marcador in mensagem for marcador in marcadores):
        raise ErroBotYouTube(
            "O YouTube bloqueou esta requisição como automatizada.\n\n"
            "Tente o seguinte:\n"
            "1. Atualize os pacotes com:\n"
            "   python.exe -m pip install --upgrade "
            "pytubefix nodejs-wheel-binaries\n"
            "2. Evite repetir muitas tentativas em sequência.\n"
            "3. Verifique se não está usando VPN ou proxy.\n"
            "4. Se necessário, consulte a documentação oficial do "
            "pytubefix sobre PO Token.\n"
            "5. Confirme se o download do vídeo é permitido."
        ) from erro

    raise erro


def verificar_ffmpeg() -> str:
    """
    Verifica se o executável ffmpeg está disponível no PATH.
    """

    caminho_ffmpeg = shutil.which("ffmpeg")

    if caminho_ffmpeg is None:
        raise ErroFFmpeg(
            "O FFmpeg não foi encontrado.\n\n"
            "Instale o FFmpeg e adicione-o ao PATH do Windows.\n"
            "Depois, abra um novo terminal e execute o programa novamente."
        )

    return caminho_ffmpeg


def obter_stream_progressivo(video: YouTube):
    """
    Obtém o melhor stream com áudio e vídeo juntos.
    """

    return (
        video.streams
        .filter(
            progressive=True,
            file_extension="mp4",
        )
        .order_by("resolution")
        .desc()
        .first()
    )


def obter_stream_video(video: YouTube):
    """
    Obtém o melhor stream de vídeo separado.
    """

    return (
        video.streams
        .filter(
            only_video=True,
            file_extension="mp4",
        )
        .order_by("resolution")
        .desc()
        .first()
    )


def obter_stream_audio(video: YouTube):
    """
    Obtém o melhor stream de áudio separado.
    """

    return (
        video.streams
        .filter(
            only_audio=True,
            file_extension="mp4",
        )
        .order_by("abr")
        .desc()
        .first()
    )


def combinar_audio_video(
    caminho_video: Path,
    caminho_audio: Path,
    caminho_saida: Path,
    caminho_ffmpeg: str,
) -> Path:
    """
    Combina os arquivos de vídeo e áudio usando o FFmpeg.
    """

    comando = [
        caminho_ffmpeg,
        "-y",
        "-i",
        str(caminho_video),
        "-i",
        str(caminho_audio),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-shortest",
        str(caminho_saida),
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if resultado.returncode != 0:
        detalhes = resultado.stderr.strip()

        raise ErroFFmpeg(
            "O FFmpeg não conseguiu combinar o áudio e o vídeo.\n\n"
            f"Detalhes:\n{detalhes}"
        )

    if not caminho_saida.exists():
        raise ErroFFmpeg(
            "O FFmpeg terminou sem informar erro, "
            "mas o arquivo final não foi criado."
        )

    return caminho_saida.resolve()


# -------------------------------------------------------------------
# Download
# -------------------------------------------------------------------

def baixar_video(url: str) -> Path:
    """
    Baixa o vídeo usando stream progressivo ou streams separados.
    """

    print("Conectando ao YouTube...")

    video = construir_video(url)

    print("Obtendo o título do vídeo...")
    titulo = video.title

    print(f"\nTítulo: {titulo}")
    print(f"Duração: {formatar_duracao(video.length)}")

    PASTA_DESTINO.mkdir(parents=True, exist_ok=True)

    print("Procurando um stream progressivo...")
    stream_progressivo = obter_stream_progressivo(video)

    if stream_progressivo is not None:
        print(
            "Stream progressivo encontrado. "
            "Áudio e vídeo serão baixados juntos."
        )
        print(
            f"Resolução selecionada: "
            f"{stream_progressivo.resolution or 'desconhecida'}"
        )
        print("Iniciando o download...\n")

        caminho = stream_progressivo.download(
            output_path=str(PASTA_DESTINO)
        )

        if not caminho:
            raise RuntimeError(
                "O download terminou, mas o caminho do arquivo "
                "não foi informado."
            )

        return Path(caminho).resolve()

    print(
        "Nenhum stream progressivo foi encontrado.\n"
        "O vídeo e o áudio serão baixados separadamente."
    )

    print("Procurando o melhor stream de vídeo...")
    stream_video = obter_stream_video(video)

    print("Procurando o melhor stream de áudio...")
    stream_audio = obter_stream_audio(video)

    if stream_video is None:
        raise RuntimeError(
            "Nenhum stream de vídeo compatível foi encontrado."
        )

    if stream_audio is None:
        raise RuntimeError(
            "Nenhum stream de áudio compatível foi encontrado."
        )

    print(
        f"Resolução do vídeo: "
        f"{stream_video.resolution or 'desconhecida'}"
    )
    print(f"Qualidade do áudio: {stream_audio.abr or 'desconhecida'}")
    print("Verificando o FFmpeg...")

    caminho_ffmpeg = verificar_ffmpeg()

    # Arquivos temporários usados antes da combinação final.
    arquivo_video_temp = PASTA_DESTINO / "_video_temporario.mp4"
    arquivo_audio_temp = PASTA_DESTINO / "_audio_temporario.mp4"

    # O arquivo final terá o mesmo nome-base do vídeo baixado.
    nome_final = f"{Path(video.title).stem}.mp4"
    caminho_final = PASTA_DESTINO / nome_final

    # Evita problemas com caracteres proibidos no Windows.
    caracteres_invalidos = '<>:"/\\|?*'
    for caractere in caracteres_invalidos:
        nome_final = nome_final.replace(caractere, "_")

    caminho_final = PASTA_DESTINO / nome_final

    try:
        print("Baixando o vídeo...\n")
        caminho_video_baixado = stream_video.download(
            output_path=str(PASTA_DESTINO),
            filename=arquivo_video_temp.name,
        )

        print("\nBaixando o áudio...\n")
        caminho_audio_baixado = stream_audio.download(
            output_path=str(PASTA_DESTINO),
            filename=arquivo_audio_temp.name,
        )

        if not caminho_video_baixado:
            raise RuntimeError(
                "O download do vídeo terminou sem gerar um arquivo."
            )

        if not caminho_audio_baixado:
            raise RuntimeError(
                "O download do áudio terminou sem gerar um arquivo."
            )

        caminho_video_baixado = Path(caminho_video_baixado)
        caminho_audio_baixado = Path(caminho_audio_baixado)

        print("\nCombinando o áudio e o vídeo com o FFmpeg...")

        return combinar_audio_video(
            caminho_video=caminho_video_baixado,
            caminho_audio=caminho_audio_baixado,
            caminho_saida=caminho_final,
            caminho_ffmpeg=caminho_ffmpeg,
        )

    finally:
        # Remove os arquivos temporários, mesmo se ocorrer algum erro.
        for arquivo_temporario in (
            arquivo_video_temp,
            arquivo_audio_temp,
        ):
            try:
                if arquivo_temporario.exists():
                    arquivo_temporario.unlink()
            except OSError:
                pass


# -------------------------------------------------------------------
# Programa principal
# -------------------------------------------------------------------

def main() -> int:
    url = URL_VIDEO.strip()

    if not url_valida(url):
        print(
            "URL inválida. Use uma URL completa do YouTube, "
            "começando com http:// ou https://.",
            file=sys.stderr,
        )
        return 2

    print(f"Pasta de destino: {PASTA_DESTINO.resolve()}")

    try:
        caminho = baixar_video(url)

    except KeyboardInterrupt:
        print("\nDownload cancelado pelo usuário.")
        return 130

    except ErroBotYouTube as erro:
        print(f"\n[ERRO DE BLOQUEIO]\n{erro}", file=sys.stderr)
        return 1

    except ErroFFmpeg as erro:
        print(f"\n[ERRO DO FFMPEG]\n{erro}", file=sys.stderr)
        return 1

    except Exception as erro:
        try:
            verificar_erro_bot(erro)

        except ErroBotYouTube as erro_bot:
            print(
                f"\n[ERRO DE BLOQUEIO]\n{erro_bot}",
                file=sys.stderr,
            )

        else:
            print(
                f"\n[ERRO] Não foi possível concluir o download:\n{erro}",
                file=sys.stderr,
            )

        return 1

    print("\nDownload concluído com sucesso!")
    print(f"Arquivo salvo em: {caminho}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# winget install Gyan.FFmpeg