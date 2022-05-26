import cv2
import numpy


def matching(img: numpy.ndarray, template: numpy.ndarray) -> int:
    """
    :param img: 画像(ndarray)
    :param template: テンプレート(ndarray)
    :return: [最小値、最大値、最小値の位置、最大値の位置]
    """
    # グレースケール変換
    gray1 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)

    # テンプレートマッチング
    match = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)
    return cv2.minMaxLoc(match)


def get_template_matching_min_point(img: numpy.ndarray, template: numpy.ndarray) -> list:
    """
    テンプレートマッチングを実行して閾値が指定した値以上の場合、最大の部分の座標を返す。
    :param img: 画像(ndarray)
    :param template: テンプレート(ndarray)
    :return: マッチングした座標[left, top, right, bottom]
    """
    min_value, max_value, min_pt, max_pt = matching(img, template)
    height, width = template.shape[:2]
    return min_pt[0], min_pt[1], min_pt[0] + width, min_pt[1] + height


def get_template_matching_max_point(img: numpy.ndarray, template: numpy.ndarray) -> list:
    """
    テンプレートマッチングを実行して閾値が指定した値以上の場合、最大の部分の座標を返す。
    :param img: 画像(ndarray)
    :param template: テンプレート(ndarray)
    :return: マッチングした座標[left, top, right, bottom]
    """
    min_value, max_value, min_pt, max_pt = matching(img, template)
    height, width = template.shape[:2]
    return max_pt[0], max_pt[1], max_pt[0] + width, max_pt[1] + height
