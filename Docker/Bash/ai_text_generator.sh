#!/bin/bash

TGPT="/usr/local/bin/tgpt"
TGPT_URL="https://raw.githubusercontent.com/aandrew-me/tgpt/main/install"
PROJECT_DIR="$HOME/bin/scripts/py-wa-scheduler"
VENV_DIR="$PROJECT_DIR/.venv"
TEMP_DIRECTORY="/run/user/1001/py-wa-scheduler"
TEMP_FILE="/run/user/1001/py-wa-scheduler/text_generated.txt"
PROMPT_BASE="Sou João e minha namorada, Maria. Me ajude a surpreendê-la com uma mensagem que celebra o amor, toca o coração dela, inspira sua alma e fortalece o vínculo entre nós. Use o tema a seguir como ponto de partida para gerar uma mensagem inesquecível, expressando o amor de forma criativa e original. Você pode se dirigir a ela pelo nome ou usar apelidos carinhosos, tais como 'meu bem', 'minha linda', 'minha fofinha', 'minha princesinha' e 'meu amorzinho'. Escreva a mensagem como se fosse eu escrevendo para ela. Apenas forneça estritamente o que se pede, sem elaborar comentários ou maiores detalhes sobre o que você produzir."
SENTENCES=(
    "[Inspiração e Reflexão] Um Pensamento Só Para Ela: Compartilhe uma citação inspiradora que a faça refletir sobre a vida, o amor ou a felicidade."
    "[Inspiração e Reflexão] O Que Aprender Hoje: Fale sobre algum fato curioso ou interessante e como isso, hipoteticamente, me fez pensar nela."
    "[Inspiração e Reflexão] Gratidão Pelo Nosso Amor: Expresse minha gratidão por tê-la em minha vida, destacando suas qualidades (personalidade, beleza, inteligência, doçura, companheira, amiga, sensata)."
    "[Criatividade e Romance] Uma História Só Nossa: Crie uma mini história fictícia onde nós dois somos os protagonistas, em um cenário romântico ou divertido."
    "[Criatividade e Romance] Se Você Fosse Uma Música...: Descreva uma música que possa me fazer lembrar dela, explicando os sentimentos e possíveis lembranças que evoca."
    "[Criatividade e Romance] Cores do Nosso Amor: Relacione cada cor a uma característica do nosso relacionamento, criando uma paleta única e especial."
    "[Intimidade e Conexão] Sonhos Compartilhados: Compartilhe um possível evento onírico em que estivemos juntos, criando um momento de intimidade e cumplicidade."
    "[Intimidade e Conexão] Lembranças Queridas: Elabore um possível momento especial que estivemos juntos, descrevendo nossas emoções e o que o torna tão único."
    "[Intimidade e Conexão] Planos para o Futuro: Conte sobre meus possíveis planos para o futuro, incluindo-a em seus sonhos e aspirações."
    "[Pequenos Gestos, Grandes Impactos] Elogio Sincero: Destaque uma possível qualidade digna de admiração dela, seja física, intelectual ou emocional."
    "[Pequenos Gestos, Grandes Impactos] Motivo do Meu Sorriso: Conte sobre algo engraçado ou fofo que, hipoteticamente, aconteceu no meu dia e que me fez lembrar dela."
    "[Pequenos Gestos, Grandes Impactos] Simplesmente Te Amo: Às vezes, as palavras mais simples são as mais poderosas. Faça uma declaração de amor de forma genuína e sincera."
)
INDEX=$((RANDOM % ${#SENTENCES[@]}))
RANDOM_SENTENCE="${SENTENCES[$INDEX]}"
RECIPIENT="$1"
SUBJECT="${2:-$RANDOM_SENTENCE}"


show_usage() {
    echo "Uso: $0 <destinatario> [assunto]"
    echo "  <destinatario> - (obrigatório) número do destinatário com o código do país e o DDD."
    echo "  [assunto] - (opcional) define o assunto do texto a ser gerado."
    exit 1
}

limpar_e_sair() {
    rm -f "$TEMP_FILE"
    exit
}

if [ -z "$1" ]; then
    echo "Erro: O parâmetro obrigatório não foi fornecido."
    show_usage
fi

if [ ! -f "$TGPT" ]; then
    echo "Arquivo $TGPT não encontrado. Baixando o script..."
    if curl -sSL "$TGPT_URL" | bash -s /usr/local/bin; then
        echo "Script baixado e executado com sucesso."
    else
        echo "Erro ao baixar ou executar o script."
        exit 1
    fi
fi

if ! cd "$PROJECT_DIR"; then
    echo "Erro ao acessar o diretório $PROJECT_DIR."
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Ambiente virtual não encontrado. Criando um novo..."
    if python3 -m venv .venv; then
        echo "Ambiente virtual criado com sucesso."
    else
        echo "Erro ao criar o ambiente virtual."
        exit 1
    fi
fi

if [ ! -d "$TEMP_DIRECTORY" ]; then
    mkdir -p "$TEMP_DIRECTORY"
fi

echo "Ativando o ambiente virtual..."
source .venv/bin/activate
echo "Ambiente virtual ativado"

tgpt -q --provider duckduckgo --preprompt "$PROMPT_BASE" "Com isso, assuma minha posição e elabore uma mensagem para ela com a seguinte dinâmica: \"$SUBJECT\"" > "$TEMP_FILE" &
wait $!
clear

python3 -u script.py "$RECIPIENT" --file "$TEMP_FILE"
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "A execução do Python falhou com código de saída: $exit_code"
fi

limpar_e_sair