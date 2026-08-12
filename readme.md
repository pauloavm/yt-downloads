# YT Downloads

Projeto simples e eficiente para facilitar o **download de vídeos** e a **extração de transcrições** de vídeos do YouTube.

---

## 🚀 Funcionalidades

### Baixar vídeos

Faça o download de vídeos do YouTube diretamente para o seu computador.

Os vídeos baixados serão armazenados na pasta:

```text
pasta_video_DL/
```

### Extrair transcrições

Obtenha automaticamente o texto das legendas ou transcrições disponíveis nos vídeos do YouTube.

As transcrições são salvas com:

- Nome do vídeo;
- ID do vídeo;
- Timestamps no formato `HH:MM:SS`.

Os arquivos serão armazenados na pasta:

```text
transcricoes/
```

---

## 🛠️ Pré-requisitos

Antes de começar, certifique-se de que os seguintes programas estejam instalados:

- **Python 3.8 ou superior**;
- **Pip**, o gerenciador de pacotes do Python;
- Conexão estável com a internet.

Para verificar se o Python está instalado, execute:

```bash
python --version
```

Em alguns sistemas, pode ser necessário utilizar:

```bash
python3 --version
```

Para verificar o Pip:

```bash
pip --version
```

Ou:

```bash
pip3 --version
```

---

## 📥 Instalação

### 1. Clonar o repositório

Abra o terminal, o Prompt de Comando ou o PowerShell e execute:

```bash
git clone <url-do-repositorio>
```

Depois, entre na pasta do projeto:

```bash
cd yt-downloads
```

> Substitua `<url-do-repositorio>` pelo endereço real do repositório.

---

### 2. Criar um ambiente virtual

Recomenda-se utilizar um ambiente virtual para manter as dependências do projeto isoladas.

No Windows:

```bash
python -m venv venv
```

No Linux ou macOS:

```bash
python3 -m venv venv
```

---

### 3. Ativar o ambiente virtual

#### Windows — Prompt de Comando

```bash
venv\Scripts\activate
```

#### Windows — PowerShell

```powershell
venv\Scripts\Activate.ps1
```

#### Linux ou macOS

```bash
source venv/bin/activate
```

Após a ativação, o terminal normalmente exibirá o nome do ambiente virtual no início da linha, por exemplo:

```text
(venv) C:\caminho\do\projeto>
```

---

### 4. Instalar as dependências

Com o ambiente virtual ativado e dentro da pasta do projeto, execute:

```bash
pip install -r requirements.txt
```

O arquivo `requirements.txt` contém as bibliotecas necessárias para executar os scripts:

- `pytubefix`;
- `youtube-transcript-api`.

---

## ▶️ Como utilizar

## Baixar vídeos

Antes de executar o script, abra o arquivo responsável pelo download e informe a URL do vídeo na variável correspondente.

Exemplo:

```python
URL_VIDEO = "https://www.youtube.com/watch?v=SEU_ID_AQUI"
```

Depois, execute:

```bash
python baixar_video.py
```

Caso o arquivo tenha sido criado com o nome `baixar_videos.py`, execute:

```bash
python baixar_videos.py
```

O vídeo será salvo automaticamente na pasta:

```text
pasta_video_DL/
```

---

## 📝 Baixar transcrições

Abra o arquivo de transcrição e informe a URL do vídeo:

```python
URL_VIDEO = "https://www.youtube.com/watch?v=SEU_ID_AQUI"
```

Depois, execute:

```bash
python baixar_transcricao.py
```

A transcrição será salva automaticamente na pasta:

```text
transcricoes/
```

O arquivo terá um nome semelhante a:

```text
transcricoes/
└── Nome do vídeo [ID_DO_VIDEO].txt
```

O conteúdo será organizado com timestamps:

```text
[00:00:00] Bem-vindos ao vídeo.
[00:00:05] Hoje vamos falar sobre este assunto.
[00:00:12] Vamos começar.
```

---

## 📁 Estrutura do projeto

Uma possível estrutura de arquivos é:

```text
yt-downloads/
├── baixar_video.py
├── baixar_transcricao.py
├── requirements.txt
├── README.md
├── pasta_video_DL/
├── transcricoes/
└── venv/
```

A pasta `venv/` será criada somente se você utilizar um ambiente virtual.

---

## ⚠️ Observações importantes

- É necessária uma conexão estável com a internet.
- Alguns vídeos podem possuir restrições de idade, privacidade ou região.
- Vídeos privados ou protegidos podem não permitir download ou acesso à transcrição.
- Nem todos os vídeos possuem legendas ou transcrições disponíveis.
- A transcrição dependerá dos idiomas disponíveis no vídeo.
- O download pode falhar caso o YouTube altere seus mecanismos de acesso.
- Utilize o projeto somente em vídeos cujo download seja permitido.
- Respeite os direitos autorais, os termos de uso do YouTube e a legislação aplicável.

---

## 🔧 Solução de problemas

### Erro ao instalar as dependências

Atualize o Pip:

```bash
python -m pip install --upgrade pip
```

Depois, tente instalar as dependências novamente:

```bash
pip install -r requirements.txt
```

---

### Comando `python` não encontrado

No Linux ou macOS, tente utilizar:

```bash
python3 baixar_video.py
```

Ou:

```bash
python3 baixar_transcricao.py
```

No Windows, verifique se o Python foi adicionado ao `PATH` durante a instalação.

---

### Nenhuma transcrição encontrada

Verifique se:

- O vídeo possui legendas ou transcrição;
- O idioma desejado está disponível;
- A URL foi informada corretamente;
- O vídeo não é privado ou restrito.

Os idiomas configurados no projeto são:

```python
IDIOMAS = ("pt", "pt-BR", "en")
```

---

## 📄 Licença

Este projeto é destinado a fins educacionais e deve ser utilizado de forma responsável, respeitando os direitos autorais e os termos de uso das plataformas acessadas.
