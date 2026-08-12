from pathlib import Path
from urllib.parse import parse_qs, urlparse

from pytubefix import YouTube
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
)


# -------------------------------------------------------------------
# CONFIGURAÇÕES
# -------------------------------------------------------------------

# Substitua pela URL real do vídeo.
URL_VIDEO = "https://www.youtube.com/watch?v=SEU_ID_AQUI"

# Pasta onde a transcrição será salva.
PASTA_SAIDA = Path("transcricoes")

# Idiomas preferenciais para buscar a transcrição.
IDIOMAS = ("pt", "pt-BR", "en")


# -------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# -------------------------------------------------------------------

def extrair_video_id(url: str) -> str:
    """
    Extrai o ID do vídeo a partir de diferentes formatos de URL.

    Exemplos aceitos:

    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://www.youtube.com/live/VIDEO_ID
    """

    partes_url = urlparse(url)

    # Remove "www." para facilitar a validação do domínio.
    dominio = partes_url.netloc.lower().removeprefix("www.")

    # Trata URLs curtas, como:
    # https://youtu.be/VIDEO_ID
    if dominio == "youtu.be":
        video_id = partes_url.path.strip("/").split("/")[0]

        if video_id:
            return video_id

    # Trata URLs de Shorts e transmissões ao vivo.
    # Exemplos:
    # /shorts/VIDEO_ID
    # /live/VIDEO_ID
    partes_caminho = [
        parte
        for parte in partes_url.path.split("/")
        if parte
    ]

    if len(partes_caminho) >= 2:
        tipo_url = partes_caminho[0].lower()

        if tipo_url in {"shorts", "live"}:
            return partes_caminho[1]

    # Trata a URL padrão:
    # https://www.youtube.com/watch?v=VIDEO_ID
    parametros = parse_qs(partes_url.query)

    if "v" in parametros and parametros["v"][0]:
        return parametros["v"][0]

    raise ValueError(
        f"Não foi possível extrair o ID do vídeo da URL:\n{url}"
    )


def limpar_nome_arquivo(nome: str) -> str:
    """
    Remove caracteres que não podem ser usados em nomes de arquivos
    no Windows.

    Caracteres removidos:

        < > : " / \ | ? *

    Também limita o nome para evitar caminhos muito longos.
    """

    caracteres_invalidos = '<>:"/\\|?*'

    # Substitui cada caractere inválido por um sublinhado.
    nome_limpo = "".join(
        "_"
        if caractere in caracteres_invalidos
        else caractere
        for caractere in nome
    )

    # Remove espaços e pontos no final do nome.
    nome_limpo = nome_limpo.strip().rstrip(".")

    # Limita o tamanho do nome do arquivo.
    nome_limpo = nome_limpo[:150]

    # Usa um nome padrão caso o título esteja vazio.
    return nome_limpo or "transcricao_video"


def segundos_para_timestamp(segundos: float) -> str:
    """
    Converte segundos para o formato HH:MM:SS.

    Exemplo:

        65.8 segundos -> 00:01:05
    """

    total_segundos = int(segundos)

    horas, resto = divmod(total_segundos, 3600)
    minutos, segundos_restantes = divmod(resto, 60)

    return (
        f"{horas:02d}:"
        f"{minutos:02d}:"
        f"{segundos_restantes:02d}"
    )


def obter_titulo_video(url: str) -> str:
    """
    Obtém o título do vídeo usando a biblioteca pytubefix.

    O título será utilizado no nome do arquivo da transcrição.
    """

    video = YouTube(url)
    return video.title


def salvar_transcricao(
    titulo_video: str,
    video_id: str,
    linhas: list[str],
) -> Path:
    """
    Salva a transcrição em um arquivo .txt usando o título do vídeo.

    O ID também é incluído no nome para evitar conflito caso existam
    vídeos diferentes com títulos iguais.

    Exemplo de nome gerado:

        Como aprender Python [abc123].txt
    """

    # Cria a pasta caso ela ainda não exista.
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    # Remove caracteres inválidos do título.
    titulo_limpo = limpar_nome_arquivo(titulo_video)

    # Monta o nome final do arquivo.
    nome_arquivo = f"{titulo_limpo} [{video_id}].txt"

    # Junta todas as linhas em um único texto.
    conteudo = "\n".join(linhas)

    # Cria o caminho completo do arquivo.
    caminho_arquivo = PASTA_SAIDA / nome_arquivo

    # Salva usando UTF-8 para preservar acentos e caracteres especiais.
    caminho_arquivo.write_text(
        conteudo,
        encoding="utf-8",
    )

    return caminho_arquivo


# -------------------------------------------------------------------
# FUNÇÃO PRINCIPAL
# -------------------------------------------------------------------

def baixar_transcricao(url: str) -> None:
    """
    Obtém a transcrição do vídeo e salva o resultado usando o título
    do vídeo como nome do arquivo.
    """

    try:
        # Extrai o ID do vídeo.
        video_id = extrair_video_id(url)
        print(f"ID do vídeo: {video_id}")

        # Obtém o título para utilizar no nome do arquivo.
        print("Obtendo o título do vídeo...")
        titulo_video = obter_titulo_video(url)
        print(f"Título: {titulo_video}")

        # Cria o cliente da API de transcrição.
        api = YouTubeTranscriptApi()

        print("Buscando a transcrição...")

        # Busca a transcrição nos idiomas definidos em IDIOMAS.
        transcricao = api.fetch(
            video_id,
            languages=list(IDIOMAS),
        )

        # Cada trecho da transcrição será transformado em uma linha
        # com timestamp e texto.
        linhas = []

        for trecho in transcricao.snippets:
            timestamp = segundos_para_timestamp(trecho.start)

            linhas.append(
                f"[{timestamp}] {trecho.text}"
            )

        # Verifica se algum conteúdo foi retornado.
        if not linhas:
            print("[ERRO] A transcrição não contém trechos.")
            return

        # Salva o arquivo usando o título do vídeo.
        caminho_arquivo = salvar_transcricao(
            titulo_video=titulo_video,
            video_id=video_id,
            linhas=linhas,
        )

        print("\n[OK] Transcrição salva com sucesso!")
        print(f"Arquivo: {caminho_arquivo.resolve()}")
        print(f"Total de trechos: {len(linhas)}")

    except TranscriptsDisabled:
        print(
            "[ERRO] As transcrições estão desativadas para este vídeo."
        )

    except NoTranscriptFound:
        print(
            "[ERRO] Nenhuma transcrição foi encontrada nos idiomas "
            f"selecionados: {', '.join(IDIOMAS)}."
        )

    except ValueError as erro:
        print(f"[ERRO] {erro}")

    except KeyboardInterrupt:
        print("\n[INFO] Operação cancelada pelo usuário.")

    except Exception as erro:
        print(f"[ERRO] Ocorreu um erro inesperado: {erro}")


# -------------------------------------------------------------------
# EXECUÇÃO DO PROGRAMA
# -------------------------------------------------------------------

if __name__ == "__main__":
    baixar_transcricao(URL_VIDEO)