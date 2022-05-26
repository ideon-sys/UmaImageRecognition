import itertools

import cv2
import numpy
from PIL.Image import fromarray
from PIL import Image


def is_color_range(rgb: [int, int, int], min_range: [int, int, int], max_range: [int, int, int],
                   mode: bool = False) -> bool:
    """
    rgbに指定された値が範囲内かどうかを判別する。
    :param rgb: [R,G,B]
    :param min_range: [R,G,B]
    :param max_range: [R,G,B]
    :param mode: Trueを指定した場合、引数rgbを[B,G,R]として判別する。（cv2向け）
    :return: 範囲内ならTrue,外ならFalse
    """
    p = rgb[::-1] if mode else rgb
    detect = False
    if all(min_range <= p) and all(p <= max_range):
        detect = True
    return detect


def resize_by_aspect(img: numpy.ndarray, arg_height: int) -> cv2:
    """
    指定した高さを基準として、アスペクト比を固定して、リサイズする。
    :param img: リサイズしたい画像（cv2）
    :param arg_height: リサイズ後の高さ
    :return: リサイズ後の画像（cv2）
    """
    height, width = img.shape[:2]
    aspect = width / height
    nh = arg_height
    nw = round(nh * aspect)

    return cv2.resize(img, dsize=(nw, nh))


def search_color(img: numpy.ndarray, scan_direction: int, start_pos: list,
                 min_rgb: list, max_rgb: list, opt_except: bool = False) -> int:
    """
    画像内の指定された位置から指定した方向に走査を行い、指定した色が最初に出現する位置を返します。
    :param img: ndarray
    :param scan_direction: 走査する方向 0: S, 1: N, 2: E, 3: W
    :param start_pos: 走査を開始する位置 [y, x]
    :param min_rgb: [R,G,B] 検索する色（最小）
    :param max_rgb: [R,G,B] 検索する色（最大）
    :param opt_except: Trueを指定した場合、指定色以外を検索　Falseを指定した、省略の場合、指定色を検索
    :return: int 最初に見つかった位置 見つからなかった場合は負数
    """
    height, width = img.shape[:2]

    if scan_direction == 0:
        r = range(start_pos[0], height, 1)
    elif scan_direction == 1:
        r = range(start_pos[0] - 1, 0, -1)
    elif scan_direction == 2:
        r = range(start_pos[1], width, 1)
    elif scan_direction == 3:
        r = range(start_pos[1] - 1, 0, -1)

    for i in r:
        colors = img[(i, start_pos[1])] if scan_direction <= 1 else img[(start_pos[0], i)]
        if opt_except:
            min_copy, max_copy = list(map(lambda x: x - 1, min_rgb)), \
                                 list(map(lambda x: x + 1, max_rgb))
            result = (is_color_range(colors, [0] * 3, min_copy, True)
                      or is_color_range(colors, max_copy, [255] * 3, True))
        else:
            result = is_color_range(colors, min_rgb, max_rgb, True)

        if result:
            return i
    return -1


def except_light_color(img: numpy.ndarray, luminance: int) -> numpy.ndarray:
    """
    画像の明るい部分を白色に加工します。
    :param img: ndarray
    :param luminance: 除去する色の輝度 指定した値以上の色を除去対象とする 0〜100の値を指定 0に近いほど暗く、100に近いほど明るい
    :return: 加工したndarray もしくは加工前のndarray
    """
    height, width = img.shape[:2]
    dst = img.copy()
    for x, y in itertools.product(range(0, width, 1), range(0, height, 1)):
        colors = dst[(y, x)]
        dbg = int(get_luminance(colors))
        if not dbg <= luminance:
            dst[(y, x)] = [255] * 3
    return dst


def cv_image(img: Image) -> numpy.ndarray:
    """
    Pillow から numpy へ変換を行う。
    :param img: PILImage
    :return: ndarray
    """
    if img.mode == "RGB":
        return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)
    if img.mode == "L":
        return numpy.array(img)
    raise ValueError("cv_image: unsupported mode: %s" % img.mode)


def pil_image(img: numpy.ndarray) -> Image:
    """
    numpy から Pillow へ変換を行う。
    :param img: ndarray
    :return: PILImage
    """
    if img.shape[2:] == (3,):
        return fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    return fromarray(img)


def get_luminance(rgb: list) -> int:
    """
    指定した色の輝度を取得する。
    :param rgb: 色 [R, G, B]
    :return: 輝度
    """
    # 輝度を求める公式の計算結果をそのまま返す。
    return (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 2550
