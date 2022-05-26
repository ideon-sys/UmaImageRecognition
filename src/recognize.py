import sys
import pyocr
import pyocr.builders
from PIL import Image


def recognize_number(img: Image) -> str:
    """
    数字を対象とした文字認識を行い、結果を返す。
    :param img: Image
    :return: 認識結果の文字列
    """
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        sys.exit(1)
    return tools[0].image_to_string(
        img,
        lang="eng",
        builder=pyocr.builders.TextBuilder())


def recognize_jpn_string(img: Image) -> str:
    """
    日本語文字列を対象とした文字認識を行い、結果を返す。
    :param img: Image
    :return: 認識結果の文字列
    """
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        sys.exit(1)
    return tools[0].image_to_string(
        img,
        lang="jpn",
        builder=pyocr.builders.TextBuilder())
