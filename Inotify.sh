#!/bin/bash

# 環境変数から student_id を取得
student_id_file="/usr/local/src/himo/username.txt"
if [ -f "$student_id_file" ]; then
    student_id=$(<"$student_id_file")
else
    student_id="unknown"  # ファイルが存在しない場合のデフォルト値
fi

inotifywait -m -r -e modify -e create -e moved_from --format "%e %w%f %f" -q /home/admin |
while read -r event file name; do
    #echo ""
    full_path="$file"

    # ファイル名に "vscode-server" が含まれている場合、処理をスキップ
    if [ "$full_path" != "${full_path//vscode-server/}" ]; then
        continue
    fi
    if [ "${name:0:1}" == "." ]; then
        continue
    fi

    event_type=$(echo "$event" | cut -d ',' -f 1)

    if [ -f "$full_path" ]; then
        type="$event_type"
        is_dir=false
    elif [ -d "$full_path" ]; then
        type="$event_type"
        is_dir=true
    else
        type="UNKNOWN"
        is_dir=false
    fi

    data='{
        "type": "'$type'",
        "path": "'$full_path'",
        "dir": '$is_dir',
        "StudentID": "'$student_id'"
    }'
    #echo $data
    curl -X POST 'https://supapush2.himohimo.workers.dev/' -H 'Content-Type: application/json' -H 'table: files' -d "$data"

    # イベントがMODIFYの場合、ファイルを比較し差分情報をDBに送信
    if [ "$event_type" == "MODIFY" ] || [ "$event_type" == "MOVED_FROM" ] || [ "$event_type" == "CREATE" ]; then
        modified_full_path="${full_path//\/home\/admin/\/usr\/local\/src\/himo\/admin}"
        directory=$(dirname "$modified_full_path")
        mkdir -p "$directory"
        if [ -e "$modified_full_path" ]; then
            # ファイルが存在する場合の処理
            diff_output=$(diff "$modified_full_path" "$full_path")
        else
            # ファイルが存在しない場合の処理
            echo "File not found: $modified_full_path"
            # 例えば、変数を別の値に設定する場合
            #modified_full_path="/some/other/path"
            diff_output=$(diff "/usr/local/src/himo/planetxt.txt" "$full_path")
        fi

        #diff_output=$(diff "$modified_full_path" "$full_path")
        modified_full_path=$(echo "$full_path" | sed 's|^/home/admin||')
        echo "modipath"
        echo $modified_full_path
        echo "diff"
        echo $diff_output
        echo "eve"
        echo $event_type:$full_path
        if [ "$diff_output" == "" ]; then
            rsync -az --delete --exclude='/.*/' "$full_path" "/usr/local/src/himo/admin$modified_full_path"
            continue
        fi
        escaped_diff=$(echo "$diff_output" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e ':a' -e 'N' -e '$!ba' -e 's/\n/\\n/g' -e 's/\\\([^n]\|$\)/^\\\\/g')
        #current_time=$(date "+%Y%m%d%H%M%S")
        escaped_diff="${escaped_diff//\"/\\\"}"
        data2='{
            "path": "'$full_path'",
            "diff": "'$escaped_diff'",
            "StudentID": "'$student_id'"
        }'
        curl -X POST 'https://supapush2.himohimo.workers.dev/' -H 'Content-Type: application/json' -H 'table: diff' -d "$data2"
    fi



    # どのようなイベントであってもrsyncでファイルを同期
    rsync -az --delete --exclude='/.*/' "$full_path" "/usr/local/src/himo/admin$modified_full_path"
done
