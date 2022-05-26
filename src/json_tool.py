import json


def json_to_list(json_dict: dict, route: str = "", result: list = []):
    """
    jsonの要素を二重リストとして返します。
    :param json_dict: json.loadで読み込んだdict
    :param route: 指定しないでください
    :param result: 指定しないでください
    :return: list
    """
    for key, value in json_dict.items():
        route_key = "{0}['{1}']".format(route, key)
        if type(value) is dict:
            result = json_to_list(value, route_key)
            continue

        # $commentの要素はコメントとして出力しない
        if key == "$comment":
            continue

        result.append([route_key, value])
    return result


def list_to_variable(arg_list: list, filename: str):
    """
    json_to_listで作成したリストをpyファイルとして出力します。
    :param arg_list: json_to_listで作成したlist
    :param filename: ファイル名
    :return: 出力の成否
    """
    try:
        fstream = open(filename, mode='w', encoding='utf-8')
        for item in arg_list:
            fstream.writelines("{0} = {1}\n".format(item[0], item[1]))
    except ValueError:
        return False
    return True
