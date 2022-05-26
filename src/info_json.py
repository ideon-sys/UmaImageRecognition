import functools
import json


class Position:
    def __init__(self, arg_top, arg_left, arg_bottom, arg_right):
        self.left = int(arg_left)
        self.top = int(arg_top)
        self.right = int(arg_right)
        self.bottom = int(arg_bottom)
        self.width = int(arg_right - arg_left)
        self.height = int(arg_bottom - arg_top)


with open("json/info.json") as fstream:
    read_json = json.load(fstream)


def get_position(status: str, mydict: dict = read_json) -> Position:
    target = mydict[status]
    return Position(target["top"], target["left"], target["bottom"], target["right"])


get_position_speed = functools.partial(get_position, status="speed")
get_position_stamina = functools.partial(get_position, status="stamina")
get_position_power = functools.partial(get_position, status="power")
get_position_guts = functools.partial(get_position, status="guts")
get_position_intelligence = functools.partial(get_position, status="intelligence")
get_position_turf = functools.partial(get_position, status="turf")
get_position_dirt = functools.partial(get_position, status="dirt")
get_position_sprint = functools.partial(get_position, status="sprint")
get_position_mile = functools.partial(get_position, status="mile")
get_position_medium = functools.partial(get_position, status="medium")
get_position_long = functools.partial(get_position, status="long")
get_position_runner = functools.partial(get_position, status="runner")
get_position_leader = functools.partial(get_position, status="leader")
get_position_betweener = functools.partial(get_position, status="betweener")
get_position_chaser = functools.partial(get_position, status="chaser")
get_position_info = functools.partial(get_position, status="info")


def get_color_info_bg() -> int:
    return read_json['info']['color']['bg']


def get_string_color() -> list:
    return [read_json['string']['color']['min'], read_json['string']['color']['max']]


def get_position_skills_detect() -> int:
    ofs = read_json['info']['skills']['ofs']
    pos_name = get_position("name", ofs)
    return read_json['info']['skills']['leftside']['left'] + pos_name.left


def get_position_skills_leftside() -> int:
    return read_json['info']['skills']['leftside']['left']


def get_position_skills_rightside() -> int:
    return read_json['info']['skills']['rightside']['left']


def get_position_skills(start_y_pos: int) -> list:
    # スキルの番号
    # 1   2
    # 3   4
    # ... ...
    # 13  14

    ofs = read_json['info']['skills']['ofs']
    pos_name = get_position("name", ofs)
    pos_uniquelv = get_position("uniquelv", ofs)
    leftside = get_position_skills_leftside()
    rightside = get_position_skills_rightside()

    pos_list = []
    for i in range(0, 14, 1):
        # 偶奇判別
        x = rightside if i % 2 else leftside
        # Y座標
        y = start_y_pos + int(ofs['next_height'] * int(i / 2))

        new_list = [Position(pos_name.top + y, pos_name.left + x, pos_name.bottom + y, pos_name.right + x),
                    Position(pos_uniquelv.top + y, pos_uniquelv.left + x, pos_uniquelv.bottom + y,
                             pos_uniquelv.right + x)]
        pos_list.append(new_list)

    return pos_list


def get_tabs_name() -> list:
    return read_json['tabs']['names']


def get_tabs_selected_detect_pos() -> list:
    """
    選択しているタブの判別に使用する座標を返す。
    :return: [[”スキル”の座標][”因子”の座標]]
    """
    skill = read_json['tabs']['selected']['skill']
    factor = read_json['tabs']['selected']['factor']
    return [[skill['left'], skill['top']], [factor['left'], factor['top']]]


def get_tabs_selected_color() -> list:
    p = read_json['tabs']['selected']['color']
    return [[p['min_white']] * 3, [p['max_white']] * 3]


def get_image_aspect() -> int:
    """
    ウマ娘の画面にて使用されるサイズのアスペクトを返す。
    :return:
    """
    return read_json['image']['aspect']


def get_template_matching_image_path_skill() -> str:
    return read_json['template_matching']['image_path']['skill']


def get_template_matching_image_path_rank() -> str:
    return read_json['template_matching']['image_path']['rank']