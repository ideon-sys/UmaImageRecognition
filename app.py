import os
import sys
import uma_detail


if len(sys.argv) <= 1:
    print("第一引数に読み込みたいファイルを指定して下さい")
    exit()
if not os.path.exists(sys.argv[1]):
    print("存在するファイルを指定して下さい。")
    exit()

try:
    src = uma_detail.imread_umadetail(sys.argv[1])
    txt = uma_detail.get_status_to_json(src)
except IndexError as e:
    print("ファイルの読込に失敗しました。PNG形式のウマ娘詳細画面を使用して下さい。")
    exit()
print("結果")
print(txt)