# py-WA-scheduler

O **py-WA-scheduler** é um projeto desenvolvido em Python, cujo propósito é permitir o envio automatizado de mensagens pelo WhatsApp Web através do terminal. Pode ser executado tanto em ambientes Windows quanto dentro de um container Docker, facilitando a integração em diversos sistemas.

> **Nota de desenvolvimento:** A versão do Docker, atualmente, tem apenas o intuito de aprendizado. Futuramente, esta versão terá seu tamanho significativamente reduzido. Não obstante seu uso em sistema Linux baseado em Debian rodar perfeitamente, dispensando a implementação com o Docker.

## Funcionalidades

- **Envio de Mensagens Automatizado:** Permite o envio de mensagens de texto para números específicos através do WhatsApp Web.
- **Suporte a Docker:** Pode ser facilmente executado em ambientes Docker, permitindo uma configuração rápida e isolada.
- **Execução em Windows:** Inclui script para execução em ambientes Windows, facilitando a utilização em máquinas locais.

## Requisitos

### Docker

- Docker instalado na máquina.

### Windows

- Python 3.7 ou superior.
- Google Chrome instalado.
- ChromeDriver compatível com a versão do Chrome instalada.

## Instruções de Uso

### Usando com Docker

1. **Construir a Imagem Docker:**

   Navegue até o diretório `Docker` e execute o comando para construir a imagem:

   ```bash
   docker build -t py-wa-scheduler .
   ```

2. **Executar o Container:**

   Após a construção da imagem, você pode executar o container para enviar uma mensagem pelo WhatsApp Web:

   ```bash
   docker run --rm -v py-wa-scheduler:/py-wa-scheduler py-wa-scheduler +5588999999999 "Olá, esta é uma mensagem de teste!"
   ```

### Uso no Linux sem Docker (Debian Bookworm)

1. **Instale as dependências necessárias:**
   - Certifique-se de ter o Python 3.8+ instalado.
   - Instale os pacotes necessários utilizando o `apt` e o `pip`:
  
  ```bash
  # adicionar fonte para encontrar todas as dependências do sistema
  echo "deb http://deb.debian.org/debian/ bookworm-backports main contrib non-free unstable" | tee /etc/apt/sources.list.d/backports.list

  # instalar as dependências necessárias
  apt-get update && \
      apt-get install -y \
      chromium \
      chromium-driver \
      nano \
      libgbm-dev \
      libzbar-dev \
      wget \
      xvfb

  pip3 install -r requirements.txt
  ```

2. **Configure o ambiente virtual:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Executando o script:**
   - Para enviar uma mensagem pelo WhatsApp Web, execute o script da seguinte forma:
     
     ```bash
     python3 -u script.py +5588999999999 "Olá, esta é uma mensagem de teste!"
     ```

### Usando no Windows

1. **Instalar Dependências:**

   No diretório `Windows`, instale as dependências listadas no arquivo `requirements.txt`:

   ```cmd
   pip install -r requirements.txt
   ```

2. **Executar o Script:**

   Rode o arquivo `run.cmd` para executar o script diretamente pelo terminal do Windows. Serão solicitados o número do destinatário e a mensagem, dentro do prompt de comando.

### Notas da configuração

> **+5588999999999**: Substitua pelo número de telefone do destinatário, incluindo o código do país.
> **"Olá, esta é uma mensagem de teste!"**: Substitua pela mensagem que deseja enviar.
> A primeira execução exigirá que você escaneie o QR code para autenticação. As sessões subsequentes usarão as informações salvas para restaurar a sessão.

## Lista de Tarefas Futuras

1. **Mensagens para Grupos:**
   - Implementar a funcionalidade para enviar mensagens para grupos do WhatsApp.
   - Adicionar a capacidade de identificar e selecionar grupos por nome.

2. **Mensagens para Contatos pelo Nome:**
   - Implementar a busca por nome de contato, permitindo o envio de mensagens sem precisar do número de telefone.

3. **Geração de Lançamento Cross-Plataform:**
   - Automatizar a geração de lançamentos do projeto para múltiplas plataformas (Linux, Windows, macOS) sem a necessidade de modificar o código-fonte.

4. **Agendamento de Mensagens:**
   - Adicionar uma funcionalidade para agendar o envio de mensagens em horários específicos.

5. **Suporte a Múltiplos Arquivos de Mensagens:**
   - Implementar a capacidade de enviar mensagens personalizadas em massa, usando arquivos de texto como entrada.

6. **Integração com APIs de Terceiros:**
   - Explorar a integração com APIs para obter informações dinâmicas e enviar mensagens automatizadas, como atualizações de status, lembretes, entre outros.

7. **Melhorias na Interface de Linha de Comando:**
   - Melhorar a usabilidade da CLI, permitindo opções mais intuitivas e configuráveis pelos usuários.

8. **Testes:**
   - Implementar uma suíte de testes automatizados para garantir a estabilidade e confiabilidade do projeto em diferentes ambientes.

## Considerações Finais

Este projeto foi desenvolvido para facilitar o envio automatizado de mensagens pelo WhatsApp Web, integrando-o com o terminal ou container Docker, visando a aplicação em diversos cenários de automação. É fundamental utilizá-lo de maneira responsável e conforme as políticas de uso do WhatsApp.

---

<h5 align="center">
  Made with 💜 by <a href="https://github.com/nullbyte-s/">nullbyte-s</a><br>
  <a href="https://choosealicense.com/licenses/mit/"><br>
  <img src="https://img.shields.io/badge/License-MIT-green.svg">
  </a>
</h5>