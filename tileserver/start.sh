#!/bin/bash
set -e
set -x

sudo -u tirex tirex-master
sudo -u tirex tirex-backend-manager
apachectl -D FOREGROUND