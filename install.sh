#!/bin/bash

echo "Installing ..."
if [[ $EUID -ne 0 ]]; then
  echo "You must be root" 2>&1
  exit 1
fi

# Variables
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

# Permissions
chmod a+rx *.py *.sh

# Cronjob
echo "* Cronjob"
echo "# m h dom mon dow user  command" > /etc/cron.d/display
echo "0 * * * * pi cd $SCRIPTPATH/ && ./runme.sh" >> /etc/cron.d/display

# Service
echo "* Service"
echo "
[Unit]
Description=Task-Editor
After=multi-user.target

[Service]
Type=simple
StandardOutput=journal
WorkingDirectory=$SCRIPTPATH/
ExecStart=$SCRIPTPATH/server.py
Restart=on-abort

[Install]
WantedBy=multi-user.target
" > /lib/systemd/system/taskeditor.service
systemctl daemon-reload
systemctl enable taskeditor
systemctl start taskeditor

# Default configuration
if [ ! -f "config.py" ]; then
	cp config.py-dist config.py
    echo "Configure in config.py"
fi
