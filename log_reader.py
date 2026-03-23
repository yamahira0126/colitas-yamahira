import time
import os
import subprocess
import json

LOG_FILE = "/tmp/www.py-httplog"
USERNAME_FILE = "/usr/local/src/himo/username.txt"
POST_URL = "https://supapush2.himohimo.workers.dev/"
HEADERS = {
    'Content-Type': 'application/json',
    'table': 'rest',  # テーブル名を 'rest' に変更
    'type': 'POST'
}

def get_student_id():
    """
    username.txt から student_id を取得する
    """
    try:
        with open(USERNAME_FILE, 'r') as file:
            student_id = file.read().strip()
        return student_id
    except FileNotFoundError:
        print(f"Error: {USERNAME_FILE} not found.")
        return None
    except Exception as e:
        print(f"Error while reading {USERNAME_FILE}: {e}")
        return None

def post_log_data(time, command, path, status_code, remote_ip, directory, student_id):
    """
    ログデータをPOSTリクエストで送信する
    """
    try:
        # データを辞書としてまとめる
        data = {
            "time": time,
            "command": command,
            "url_path": path,
            "status_code": status_code,
            "remote_ip": remote_ip,
            "directory": directory,
            "student_id": student_id
        }
        # 辞書をJSON形式に変換
        data_json = json.dumps(data)
        # curlを使ってPOSTリクエストを送信
        cmd = [
            'curl', '-X', 'POST', POST_URL,
            '-H', 'Content-Type: application/json',
            '-H', 'table: rest',
            '-H', 'type: POST',
            '-d', data_json
        ]
        # コマンド実行
        subprocess.run(cmd, check=True)
        print(f"Sent log: {data_json}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to send log: {data_json} - Error: {e}")

def monitor_log_file():
    """
    ログファイルを監視し、新しいエントリをPOSTする
    """
    student_id = get_student_id()  # username.txt から student_id を取得
    if student_id is None:
        print("Error: Unable to get student_id from username.txt.")
        return

    # ログファイルが存在するかを確認
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as file:
                # ログファイルの内容を読み込み
                lines = file.readlines()

            # ログファイルを空にする（消去する）
            open(LOG_FILE, 'w').close()

            # 読み込んだ各行を処理
            for line in lines:
                parts = line.strip().split("|:|")  # パイプで分割
                if len(parts) == 6:
                    # フォーマット: timestamp|:|GET/POST|:|path|:|dir|:|status|:|ip
                    time, command, path, directory, status_code, remote_ip = parts
                    post_log_data(time, command, path, status_code, remote_ip, directory, student_id)

        except Exception as e:
            print(f"Error while reading and processing log file: {e}")
    else:
        print(f"Log file {LOG_FILE} does not exist.")

if __name__ == "__main__":
    monitor_log_file()
