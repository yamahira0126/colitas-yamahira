#!/bin/bash

# ユーザー名とパスワードを読み取る
USERNAME=$(cat /usr/local/src/himo/username.txt)
PASSWORD=$(cat /usr/local/src/himo/password.txt)
cd /home/admin

directory="/usr/local/src/himo/key"

rm -r "$directory"/*



if [ ! -d "$directory" ]; then
    mkdir "$directory"
fi
curl -o /usr/local/src/himo/key/pubkey.zip https://api.fml.org/dist/pubkey.zip
unzip -d /usr/local/src/himo/key -P QOL2024nasuno /usr/local/src/himo/key/pubkey.zip
# ttyd を実行する
/usr/local/bin/ttyd -W -p 443 --ssl --ssl-cert /usr/local/src/himo/key/fullchain3.pem --ssl-key /usr/local/src/himo/key/privkey3.pem -c "$USERNAME:$PASSWORD" bash
