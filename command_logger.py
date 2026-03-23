import re
import sys
import json
import subprocess

PID = sys.argv[1]
result = ""

def limit_string_length(input_string, max_length=1000000, suffix_length=1000):
    if len(input_string) <= max_length:
        return input_string
    else:
        #print("nagasakoetemasuyo")
        return input_string[:max_length] + input_string[-suffix_length:]

with open(f'/usr/local/src/himo/typescript_{PID}', 'r') as input_file:
    result = ""
    for line in input_file:
        output_line = re.sub(r'\x1b\[[^mGK]*[mGK]', '', line)
        result += output_line
    result = result.split("2004l\n")

try:
    with open(f'/usr/local/src/himo/lastcommand_{sys.argv[3]}', 'r', encoding='utf-8') as file:
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
                        'StudentID': log_dict['StudentID'],
                        'ip_addr': log_dict['GlobalIP'],
                        'path': log_dict['CurrentDir'],
                        'command': log_dict['Command'],
                        'output': limit_string_length(result[-1]),
                        'ExitCode': log_dict['ExitCode'],
                        'uuid': sys.argv[2],
                        'after_path': sys.argv[4]
                    }
                    #print("-------after-------")
                    #print(data)
                    data_json = json.dumps(data)
                    cmd = ['curl', '-X', 'POST', 'https://supapush2.himohimo.workers.dev/', '-H', 'Content-Type: application/json', '-H', 'table: logdata', '-H', f'uuid: {sys.argv[2]}', '-H', 'type: PATCH', '-d', data_json]
                except KeyError as e:
                    data = {
                        'StudentID': log_dict['StudentID'],
                        'ip_addr': log_dict['GlobalIP'],
                        'path': log_dict['CurrentDir'],
                        'command': log_dict['Command'],
                        'uuid': sys.argv[2]
                    }
                    #print("-------after-------")
                    #print(data)
                    data_json = json.dumps(data)
                    cmd = ['curl', '-X', 'POST', 'https://supapush2.himohimo.workers.dev/', '-H', 'Content-Type: application/json', '-H', 'table: logdata', '-H', 'type: POST', '-d', data_json]
                    # exit(1)
                # data_json = json.dumps(data)
                #print(result)
                # cmd = ['curl', '-X', 'POST', 'https://supabasepusher.himohimo.workers.dev/', '-H', 'Content-Type: application/json', '-H', 'table: logdata', '-H', f'uuid: {sys.argv[2]}','-d', data_json]
                try:
                    result = subprocess.run(cmd, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    #print(result)
                except subprocess.CalledProcessError as e:
                    print(f"log取得のエラーコード: {e.returncode}")
                    print(f"学生の方は無視していただいて大丈夫です。: {e.stderr}")
except subprocess.CalledProcessError as e:
    print(f"コマンドがエラーを返しました。エラーコード: {e.returncode}")
    print(f"エラーメッセージ: {e.stderr}")
