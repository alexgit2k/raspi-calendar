#!/bin/bash

echo "Uninstalling ..."
if [[ $EUID -ne 0 ]]; then
  echo "You must be root" 2>&1
  exit 1
fi

# Cronjob
echo "* Cronjob"
rm /etc/cron.d/display

# Service
echo "* Service"
systemctl stop taskeditor
systemctl disable taskeditor
rm /lib/systemd/system/taskeditor.service
systemctl daemon-reload
