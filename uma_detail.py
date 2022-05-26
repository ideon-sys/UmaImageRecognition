import json
import math
from functools import partial

import cv2
import numpy

from src import imagetools as imgtools, info_json as info, recognize, template_matching

GREEN_REF_VAL = [[100, 180, 0], [190, 255, 70]]
WHITE_REF_VAL = [[250] * 3, [255] * 3]

is_green_color = \
    partial(imgtools.is_color_range, min_range=GREEN_REF_VAL[0], max_range=GREEN_REF_VAL[1], mode=True)

is_white_color = \
    partial(imgtools.is_color_range, min_range=WHITE_REF_VAL[0], max_range=WHITE_REF_VAL[1], mode=True)
"""
指定されたRGB値が緑（白）の閾値内かどうかを返す。
:param rgb: [R, G, B]
:return: bool: Trueなら緑（白）、Falseなら閾値外
"""


def __except_string(img: numpy.ndarray) -> numpy.ndarray:
    """
    画像の文字部分のみを抽出する。
    :param img: ndarray
    :return: 加工したndarray もしくは加工前のndarray
    """
    lower, upper = info.get_string_color()
    # 文字色範囲の値をTrue、範囲外をFalseに置き換えた配列を取得
    x = ((img > lower[::-1]) & (img < upper[::-1])).all(axis=2)
    # 置き換えた配列からnonzeroでTrueの位置を抽出して、その位置から画像を切り出して返す。
    result = numpy.nonzero(x)
    return img[min(result[0]): max(result[0]) + 1, min(result[1]): max(result[1]) + 1] if len(result[0]) > 0 else img


def __get_skillname_for_json(pt) -> str:
    """
    テンプレートマッチングの比較結果から対応したスキル名を返す。
    :param pt: テンプレートマッチングで取得した位置
    :return: スキル名
    """
    with open("json/skill.json") as fstream:
        read_json = json.load(fstream)
        string_size = read_json["size"]

        # テンプレートマッチングで取得した位置のY軸の中間を{文字列の間隔}で割った数字で辞書検索
        pos = (pt[1] + pt[3]) / 2
        key = math.floor((pos - 2) / string_size)
        skill_name = read_json[str(key)]

    return skill_name


def __is_circle_or_double(img: numpy.ndarray) -> bool:
    """
    # 画像の最後の文字が○か◎を判別する
    :param img: ndarray
    :return: ◎・・・True　○・・・False
    """
    # 画像の右端から文字の色が出現する回数で判断する
    circle_size = 14
    bg_count = 2  # 判別用

    height, width = round(int(img.shape[0]) / 2), int(img.shape[1])
    cpy_img = img[height: height + 1, width - circle_size: width]
    lower, upper = info.get_string_color()
    # 文字色範囲の値をTrue、範囲外をFalseに置き換えた配列を取得
    x = ((cpy_img > lower[::-1]) & (cpy_img < upper[::-1])).all(axis=2)
    count = numpy.count_nonzero(x)

    return True if count > bg_count else False


def __extract_umadetail(img: numpy.ndarray) -> numpy.ndarray:
    """
    画像から背景部分を除いた部分を抽出する。
    :param img : ndarray
    :return: リサイズ後のndarray
    """
    aspect = info.get_image_aspect()[0]
    height, width = img.shape[:2]

    # 上部(緑部分)を設定する。
    # 検索条件は、誤検知を少なくする為、画像の3箇所（1/3,1/2,2/3地点）の色が閾値内に収まる部分を条件とする。
    cpy_img = cv2.hconcat([img[0: height, int(width * 0.33): int(width * 0.33) + 1],
                           img[0: height, int(width * 0.5): int(width * 0.5) + 1],
                           img[0: height, int(width * 0.66): int(width * 0.66) + 1]])
    result1 = ((cpy_img >= GREEN_REF_VAL[0][::-1]) & (cpy_img <= GREEN_REF_VAL[1][::-1])).all(axis=2)
    top_pos = numpy.where(result1 == [True, True, True])[0][0]

    # 下部(白部分)を設定
    result2 = ((cpy_img >= WHITE_REF_VAL[0][::-1]) & (cpy_img <= WHITE_REF_VAL[1][::-1])).all(axis=2)
    bottom_pos = numpy.where(result2 == [True, True, True])[0][-1]

    # 切り取る高さを基準としてアスペクト比で幅を計算
    true_height = bottom_pos - top_pos
    resize_w = int((width - (true_height * aspect)) / 2)

    # トリミング [top: bottom, left: right]
    dst = img[top_pos: bottom_pos, resize_w: width - resize_w]
    return dst


def __get_skill_for_template_matching(img: numpy.ndarray, start_pos: int) -> dict:
    mydict = {}
    position = info.get_position_skills(start_pos)
    for index, item in enumerate(position):
        skill, lv = item
        # 対象部分の画像を抽出
        target_img = img[skill.top: skill.bottom, skill.left: skill.right].copy()
        height, width = target_img.shape[:2]
        # 抜き出した画像の背景色を消去
        luminance = 60
        target_img = imgtools.except_light_color(__except_string(target_img), luminance)
        # ↓　テンプレートマッチング
        matching_png = info.get_template_matching_image_path_skill()
        cv_tmp_match = cv2.imread(matching_png)
        res = template_matching.matching(cv_tmp_match, target_img)
        # ↑　テンプレートマッチング
        threshold = 0.2
        # 閾値以下、もしくは[0, 0]の座標を返しているなら処理しない
        if res[1] < threshold or numpy.all(res[3] == numpy.array([0, 0])):
            continue
        pt = res[3][0], res[3][1], res[3][0] + width, res[3][1] + height  # max_pt
        # 文字位置からスキル名を取得
        skill_name = __get_skillname_for_json(pt)
        # 最終文字が○か◎かどうか判定する
        circle, double_circle = "◯", "◎"
        if skill_name[-1] == circle or skill_name[-1] == double_circle:
            skill_name = "{0}{1}".format(skill_name[:-1],
                                         (double_circle if __is_circle_or_double(target_img) else circle))
        # 初回のスキルだけ、固有スキルの可能性があるので、レベルも取得
        level = ""
        if index == 0:
            level = recognize.recognize_number(
                imgtools.pil_image(img[lv.top: lv.bottom, lv.left: lv.right]))
            level = "lv{0}".format(level[-1]) if level[-1].isdecimal() else level
        mydict[skill_name] = level
    return mydict


def imread_umadetail(img_path: str) -> numpy.ndarray:
    try:
        read_test = cv2.imread(img_path)
        return imgtools.resize_by_aspect(__extract_umadetail(read_test), 1000)
    except Exception as e:
        return e


def get_selected_tab(img: numpy.ndarray) -> str:
    """
    読み込んだ画像の選択しているタブを取得する。
    :param img: ndarray
    :return:
    """
    # ["育成情報", "スキル", "因子"]のタブ　適当な箇所の色を抜き出して、白系ではない箇所を選択項目として設定
    # (白系の方が指定する範囲がわかりやすいため)
    min_white, max_white = info.get_tabs_selected_color()
    pos_skill, pos_factor = info.get_tabs_selected_detect_pos()

    if not imgtools.is_color_range(img[pos_skill[0], pos_skill[1]], min_white, max_white, True):
        return info.get_tabs_name()[1]
    elif not imgtools.is_color_range(img[pos_factor[0], pos_factor[1]], min_white, max_white, True):
        return info.get_tabs_name()[2]
    else:
        return info.get_tabs_name()[0]


def get_skill(img: numpy.ndarray) -> dict:
    """
    スキルを取得する。
    :return: dict [key: スキル名, vallue: スキルLv]
    """
    # Y軸が不定の為、Y軸の読み込み開始位置を設定する
    # ※スキル数が14を超える場合、１枚で入り切らず、２枚の読み込みが必要な場合があり、Y軸がズレる可能性があるため
    pos_detail = info.get_position_info()
    pos_skill_detect = info.get_position_skills_detect()  # スキル左側の文字の座標（LEFT）
    color_detail_bg = info.get_color_info_bg()

    # Y軸の初期設定　最初に”詳細の背景色”が見つかる場所
    find_pos = imgtools.search_color(img=img, scan_direction=0,
                                     start_pos=[pos_detail.top, pos_skill_detect], min_rgb=[color_detail_bg] * 3,
                                     max_rgb=[color_detail_bg] * 3)
    # Y軸の設定　初期設定の値から最初に”詳細の背景色以外”が見つかる場所 ＋外枠の2px
    start_pos = imgtools.search_color(img=img, scan_direction=0,
                                      start_pos=[find_pos, pos_skill_detect], min_rgb=[color_detail_bg] * 3,
                                      max_rgb=[color_detail_bg] * 3, opt_except=True) + 2

    return __get_skill_for_template_matching(img, start_pos)


# ステータス
def __get_status(img: numpy.ndarray, pos: info.Position) -> str:
    r = recognize.recognize_number(imgtools.pil_image(img[pos.top: pos.bottom, pos.left: pos.right]))
    return r if str.isdecimal(r) else 0


get_status_speed = partial(__get_status, pos=info.get_position_speed())
get_status_stamina = partial(__get_status, pos=info.get_position_stamina())
get_status_power = partial(__get_status, pos=info.get_position_power())
get_status_guts = partial(__get_status, pos=info.get_position_guts())
get_status_intelligence = partial(__get_status, pos=info.get_position_intelligence())


# 適正
def __get_suitable(img: numpy.ndarray, pos: info.Position) -> str:
    # テンプレートマッチングに使用する画像を取得
    match_image = cv2.imread(info.get_template_matching_image_path_rank())
    match_size = 100
    match_string = ["S", "A", "B", "C", "D", "E", "F", "G"]
    new_image = img[pos.top: pos.bottom, pos.left: pos.right].copy()
    new_image = imgtools.resize_by_aspect(new_image, match_size)

    # テンプレートマッチング（最小値の位置を取得）
    pt = template_matching.get_template_matching_max_point(new_image, match_image)[0]
    # 比較する位置を調整（startとendの処理）して、比較結果を返す
    for i in range(len(match_string)):
        start = -10 + (match_size * i)
        end = 90 + (match_size * i)
        if start < pt < end:
            return match_string[i]
    return "G"


# バ場適正
get_status_turf = partial(__get_suitable, pos=info.get_position_turf())
get_status_dirt = partial(__get_suitable, pos=info.get_position_dirt())
# 距離適性
get_status_sprint = partial(__get_suitable, pos=info.get_position_sprint())
get_status_mile = partial(__get_suitable, pos=info.get_position_mile())
get_status_medium = partial(__get_suitable, pos=info.get_position_medium())
get_status_long = partial(__get_suitable, pos=info.get_position_long())
# 脚質適正
get_status_runner = partial(__get_suitable, pos=info.get_position_runner())
get_status_leader = partial(__get_suitable, pos=info.get_position_leader())
get_status_betweener = partial(__get_suitable, pos=info.get_position_betweener())
get_status_chaser = partial(__get_suitable, pos=info.get_position_chaser())


def get_status_all(img: numpy.ndarray):
    return [get_status_speed(img), get_status_stamina(img), get_status_power(img), get_status_guts(img),
            get_status_intelligence(img), get_status_turf(img), get_status_dirt(img),
            get_status_sprint(img), get_status_mile(img), get_status_medium(img), get_status_long(img),
            get_status_runner(img), get_status_leader(img), get_status_betweener(img),
            get_status_chaser(img)]


def get_status_to_json(img: numpy.ndarray):
    dict = "{0}".format(get_skill(img)).replace("'", '"')
    js = '"speed": {0[0]}, ' \
         '"stamina": {0[1]}, ' \
         '"power": {0[2]}, ' \
         '"guts": {0[3]}, ' \
         '"intelligence": {0[4]},' \
         '"turf": "{0[5]}", ' \
         '"dirt": "{0[6]}",' \
         '"sprint": "{0[7]}",' \
         '"mile": "{0[8]}",' \
         '"medium": "{0[9]}",' \
         '"long": "{0[10]}",' \
         '"runner": "{0[11]}",' \
         '"leader": "{0[12]}",' \
         '"betweener": "{0[13]}",' \
         '"chaser": "{0[14]}",' \
         '"skills": {1} ' \
        .format(get_status_all(img), dict)
    return "{" + js + "}"
