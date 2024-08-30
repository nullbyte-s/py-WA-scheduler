#!/bin/bash

if [ "$(id -u)" -ne "0" ]; then
    echo "Este script deve ser executado como root."
    exit 1
fi

USER_HOME=$(getent passwd 1001 | cut -d: -f6)

SERVICE_FILE="/etc/systemd/system/PWS_run_in_time_slot.service"
if [ ! -f "$SERVICE_FILE" ]; then
    cat << EOF > "$SERVICE_FILE"
[Unit]
Description=[Py-WA-Scheduler] Verifica se a execução programada está dentro dos horários permitidos

[Service]
User=1001
Group=1001
ExecStart=/usr/local/bin/PWS_run_in_time_slot.sh
Type=oneshot

[Install]
WantedBy=multi-user.target
EOF
    echo "Arquivo de serviço criado em $SERVICE_FILE"
else
    echo "Arquivo de serviço já existe em $SERVICE_FILE"
fi

PWS_run_in_time_slot_FILE="/usr/local/bin/PWS_run_in_time_slot.sh"
if [ ! -f "$PWS_run_in_time_slot_FILE" ]; then
    cat << EOF > "$PWS_run_in_time_slot_FILE"
#!/bin/bash

START_TIME="08:00"
END_TIME="20:00"
CURRENT_TIME=\$(date +%H:%M)

if [[ "\$CURRENT_TIME" > "\$START_TIME" && "\$CURRENT_TIME" < "\$END_TIME" ]]; then
    if [ ! -x "$USER_HOME/bin/scripts/py-wa-scheduler/Bash/ai_text_generator.sh" ]; then
        chmod +x "$USER_HOME/bin/scripts/py-wa-scheduler/Bash/ai_text_generator.sh"
    fi
    if [ "$(date +%u)" -le "$((RANDOM % 7 + 1))" ]; then
        echo "Executando o script..."
        "${USER_HOME}/bin/scripts/py-wa-scheduler/Bash/ai_text_generator.sh" +5588999999999
    else
        echo "O script não será executado hoje."
    fi
else
    echo "Fora do horário permitido. Tentando novamente em 45 minutos."
    sudo systemctl start PWS_run_in_time_slot.timer
fi
EOF
    chmod +x "$PWS_run_in_time_slot_FILE"
    echo "Script de checagem e execução criado e executável em $PWS_run_in_time_slot_FILE"
else
    echo "Script de checagem e execução já existe em $PWS_run_in_time_slot_FILE"
fi

TIMER_FILE="/etc/systemd/system/PWS_run_in_time_slot.timer"
if [ ! -f "$TIMER_FILE" ]; then
    cat << EOF > "$TIMER_FILE"
[Unit]
Description=[Py-WA-Scheduler] Timer para o script verificador dos horários permitidos
[Timer]
OnCalendar=daily
Persistent=true
OnUnitActiveSec=45m

[Install]
WantedBy=timers.target
EOF
    echo "Arquivo de timer criado em $TIMER_FILE"
else
    echo "Arquivo de timer já existe em $TIMER_FILE"
fi

systemctl daemon-reload
systemctl enable PWS_run_in_time_slot.timer
systemctl start PWS_run_in_time_slot.timer

echo "Configuração concluída. Timer e serviço foram habilitados e iniciados."

: <<'DESINSTALAR'
sudo systemctl disable PWS_run_in_time_slot.timer
sudo systemctl stop PWS_run_in_time_slot.service PWS_run_in_time_slot.timer
sudo rm /usr/local/bin/PWS_run_in_time_slot.sh /etc/systemd/system/PWS_run_in_time_slot.service /etc/systemd/system/PWS_run_in_time_slot.timer
DESINSTALAR