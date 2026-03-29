#!/bin/bash

BASE_DIR="/usr/local/src/himo"

# ユーザー名とパスワードを読み取る
USERNAME=$(cat "${BASE_DIR}/username.txt")
PASSWORD=$(cat "${BASE_DIR}/password.txt")
cd /home/admin

directory="${BASE_DIR}/key"

rm -r "$directory"/*



if [ ! -d "$directory" ]; then
    mkdir "$directory"
fi
curl -o "${BASE_DIR}/key/pubkey.zip" https://api.fml.org/dist/pubkey.zip
unzip -d "${BASE_DIR}/key" -P QOL2024nasuno "${BASE_DIR}/key/pubkey.zip"
# ttyd を実行する
/usr/local/bin/ttyd -W -p 443 --ssl --ssl-cert "${BASE_DIR}/key/fullchain3.pem" --ssl-key "${BASE_DIR}/key/privkey3.pem" -c "$USERNAME:$PASSWORD" bash
