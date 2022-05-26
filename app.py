import os
import sys
import datetime
import uma_detail


dt_now = datetime.datetime.now()

path = input("ファイル名を指定して下さい。\n") if len(sys.argv) <= 1 else sys.argv[1]

if not os.path.exists(path):
    print("存在するファイルを指定して下さい。")
    msg = "ERROR [{0}] : 存在するファイルを指定して下さい。\n".format(dt_now)
else:
    try:
        src = uma_detail.imread_umadetail(path)
        txt = uma_detail.get_status_to_json(src)
        print("結果")
        print(txt)
        msg = "INFO [{0}] : {1}\n".format(dt_now, txt)
    except IndexError as e:
        print("ファイルの読込に失敗しました。PNG形式のウマ娘詳細画面を使用して下さい。")
        msg = "ERROR [{0}] : ファイルの読込に失敗しました。PNG形式のウマ娘詳細画面を使用して下さい。\n".format(dt_now)

with open("result.log", mode='a', encoding='utf-8') as fstream:
    fstream.write(msg)

input("何かキーを押すと終了します。。\n")