import re
import sys
import json
import os
import subprocess

PID = sys.argv[1]
result = ""
BASE_DIR = "/usr/local/src/himo"
ENV_FILE = f"{BASE_DIR}/colitas.env"

def load_env_file(path):
    env = {}
    if not os.path.exists(path):
        return env

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()
    return env

env = load_env_file(ENV_FILE)

SUPABASE_URL = env.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_APIKEY = env.get("SUPABASE_APIKEY", "")
SUPABASE_JWT = env.get("SUPABASE_JWT", "")
SUPABASE_LOG_COMMAND_URL = f"{SUPABASE_URL}/rest/v1/log_command"

def limit_string_length(input_string, max_length=1000000, suffix_length=1000):
    if len(input_string) <= max_length:
        return input_string
    else:
        #print("nagasakoetemasuyo")
        return input_string[:max_length] + input_string[-suffix_length:]

with open(f'{BASE_DIR}/typescript_{PID}', 'r') as input_file:
    result = ""
    for line in input_file:
        output_line = re.sub(r'\x1b\[[^mGK]*[mGK]', '', line)
        result += output_line
    result = result.split("2004l\n")

try:
    with open(f'{BASE_DIR}/lastcommand_{sys.argv[3]}', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        last_line = lines[-1].strip()
        existence_uuid = 0
        if last_line:
            parts = last_line.split('@w@a@w@')
            log_dict = {}
            for element in parts:
                key_value = element.split('@c@w@c@')
                if len(key_value) == 2:
                    key, value = key_value[0], key_value[1]
                    log_dict[key] = value
            else:
                cmd = []
                try:
                    data = {
                        'student_id': log_dict['StudentID'],
                        'ip_addr': log_dict['GlobalIP'],
                        'path': log_dict['CurrentDir'],
                        'command': log_dict['Command'],
                        'base_command': log_dict['BaseCommand'],
                        'output': limit_string_length(result[-1]),
                        'exit_code': log_dict['ExitCode'],
                        'uuid': sys.argv[2],
                        'after_path': sys.argv[4]
                    }
                    #print("-------after-------")
                    #print(data)
                    data_json = json.dumps(data)
                    cmd = [
                        'curl', '-k', '-X', 'PATCH', f'{SUPABASE_LOG_COMMAND_URL}?uuid=eq.{sys.argv[2]}',
                        '-H', f'apikey: {SUPABASE_APIKEY}',
                        '-H', f'Authorization: Bearer {SUPABASE_JWT}',
                        '-H', 'Content-Type: application/json',
                        '-H', 'Prefer: return=minimal',
                        '-d', data_json
                    ]
                except KeyError as e:
                    data = {
                        'student_id': log_dict['StudentID'],
                        'ip_addr': log_dict['GlobalIP'],
                        'path': log_dict['CurrentDir'],
                        'command': log_dict['Command'],
                        'base_command': log_dict['BaseCommand'],
                        'uuid': sys.argv[2]
                    }
                    #print("-------after-------")
                    #print(data)
                    data_json = json.dumps(data)
                    cmd = [
                        'curl', '-k', '-X', 'POST', SUPABASE_LOG_COMMAND_URL,
                        '-H', f'apikey: {SUPABASE_APIKEY}',
                        '-H', f'Authorization: Bearer {SUPABASE_JWT}',
                        '-H', 'Content-Type: application/json',
                        '-H', 'Prefer: return=minimal',
                        '-d', data_json
                    ]
                    # exit(1)
                #print(result)
                try:
                    result = subprocess.run(cmd, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    #print(result)
                except subprocess.CalledProcessError as e:
                    print(f"log取得のエラーコード: {e.returncode}")
                    print(f"学生の方は無視していただいて大丈夫です。: {e.stderr}")
except subprocess.CalledProcessError as e:
    print(f"コマンドがエラーを返しました。エラーコード: {e.returncode}")
    print(f"エラーメッセージ: {e.stderr}")
