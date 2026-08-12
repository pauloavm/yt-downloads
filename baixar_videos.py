from pathlib import Path
from urllib.parse import urlparse

from pytubefix import YouTube
from pytubefix.cli import on_progress


# -------------------------------------------------------------------
# 1. Configuração inicial
# -------------------------------------------------------------------

# Substitua este texto pela URL real do vídeo do YouTube.
URL_VIDEO = "https://www.youtube.com/watch?v=SEU_ID_AQUI"

# A pasta será criada dentro da pasta em que o programa for executado.
# Por exemplo: ./pasta_video_DL
PASTA_DESTINO = Path("pasta_video_DL")


# -------------------------------------------------------------------
# 2. Funções auxiliares
# -------------------------------------------------------------------

def url_valida(url: str) -> bool:
    """
    Verifica se o texto informado possui uma URL aparentemente válida.

    Esta validação não garante que o vídeo exista.
    Ela apenas verifica se a URL possui:
    - protocolo http ou https;
    - domínio preenchido.
    """
    try:
        partes = urlparse(url)

        return (
            partes.scheme in {"http", "https"}
            and bool(partes.netloc)
        )

    except ValueError:
        return False


def formatar_duracao(segundos: int | None) -> str:
    """
    Converte a duração do vídeo, originalmente em segundos,
    para o formato HH:MM:SS ou MM:SS.
    """

    # Caso a duração não esteja disponível, evita erro no programa.
    if segundos is None:
        return "Duração desconhecida"

    horas, resto = divmod(segundos, 3600)
    minutos, segundos_restantes = divmod(resto, 60)

    if horas > 0:
        return f"{horas:02d}:{minutos:02d}:{segundos_restantes:02d}"

    return f"{minutos:02d}:{segundos_restantes:02d}"


# -------------------------------------------------------------------
# 3. Validação da entrada
# -------------------------------------------------------------------

if not url_valida(URL_VIDEO):
    raise ValueError(
        "URL inválida. Informe um endereço completo, começando com "
        "'https://' ou 'http://'."
    )


# -------------------------------------------------------------------
# 4. Preparação da pasta de destino
# -------------------------------------------------------------------

# parents=True permite criar pastas intermediárias, se necessário.
# exist_ok=True evita erro caso a pasta já exista.
PASTA_DESTINO.mkdir(parents=True, exist_ok=True)

print(f"Pasta de destino: {PASTA_DESTINO.resolve()}")
print("Conectando ao YouTube...")


# -------------------------------------------------------------------
# 5. Inicialização e download
# -------------------------------------------------------------------

try:
    # Cria o objeto que representa o vídeo.
    #
    # O callback on_progress exibe o progresso do download
    # diretamente no terminal.
    video = YouTube(
        URL_VIDEO,
        on_progress_callback=on_progress
    )

    # Exibe informações básicas antes de iniciar o download.
    print(f"\nTítulo: {video.title}")
    print(f"Duração: {formatar_duracao(video.length)}")
    print("Buscando a maior resolução disponível...")

    # Obtém o stream progressivo de maior resolução disponível.
    #
    # Um stream progressivo normalmente contém vídeo e áudio juntos,
    # facilitando o download em um único arquivo.
    stream = video.streams.get_highest_resolution()

    # Verifica se a biblioteca encontrou algum stream compatível.
    if stream is None:
        print(
            "\nNenhum stream compatível foi encontrado para este vídeo."
        )

    else:
        print(f"Resolução selecionada: {stream.resolution}")
        print("Iniciando o download...\n")

        # Realiza o download na pasta definida anteriormente.
        caminho_arquivo = stream.download(
            output_path=str(PASTA_DESTINO)
        )

        print("\nDownload concluído com sucesso!")
        if caminho_arquivo is None:
            print("Arquivo salvo em: caminho desconhecido")
        else:
            print(f"Arquivo salvo em: {Path(caminho_arquivo).resolve()}")


# Trata o cancelamento manual usando Ctrl+C separadamente.
except KeyboardInterrupt:
    print("\nDownload cancelado pelo usuário.")

# Trata erros relacionados à conexão, URL, disponibilidade do vídeo
# ou incompatibilidade entre a biblioteca e o YouTube.
except Exception as erro:
    print("\nNão foi possível concluir o download.")
    print(f"Detalhes do erro: {erro}")