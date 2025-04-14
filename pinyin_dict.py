import pypinyin
from pypinyin import pinyin, Style
import re
import sys
from collections import defaultdict

# 定义一个函数，将汉字转换为拼音
def hanzi_to_pinyin(hanzi):
    # 使用 pypinyin 转换为拼音
    initials = pinyin(hanzi, style=Style.NORMAL, strict=False, heteronym=True)
    # 提取拼音并格式化
    formatted_pinyin = []
    for initial in initials:
        for single in initial:
            formatted_pinyin.append(f"{single}")

    return formatted_pinyin

# 定义一个函数，从文件中读取汉字
def read_hanzi_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    # 使用正则表达式提取所有汉字
    hanzi_list = re.findall(r'[\u4e00-\u9fff]', content)
    return hanzi_list

# 定义一个函数，生成拼音到汉字的映射
def generate_pinyin_to_hanzi_map(hanzi_list):
    pinyin_to_hanzi = defaultdict(set)
    for hanzi in hanzi_list:
        pinyin_list = hanzi_to_pinyin(hanzi)
        for pinyin in pinyin_list:
            # 去掉声调数字
            pinyin_no_tone = ''.join(filter(lambda x: not x.isdigit(), pinyin)).replace(" ", "")
            pinyin_to_hanzi[pinyin_no_tone].add(hanzi)
    return pinyin_to_hanzi

# 主函数
def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    hanzi_list = read_hanzi_from_file(file_path)
    pinyin_to_hanzi_map = generate_pinyin_to_hanzi_map(hanzi_list)

    # 按照字母顺序排序拼音到汉字的映射
    sorted_pinyin_to_hanzi_map = dict(sorted(pinyin_to_hanzi_map.items(), key=lambda item: item[0]))

    # 保存拼音到汉字的映射为 C 语言数组
    with open('pinyin_to_hanzi.h', 'w', encoding='utf-8') as f:
        f.write("#ifndef __PINYIN_TO_HANZI_H__\n")
        f.write("#define __PINYIN_TO_HANZI_H__\n\n")
        f.write("static lv_pinyin_dict_t lv_ime_pinyin_dict[] =\n{\n")
        for pinyin, hanzi_set in sorted_pinyin_to_hanzi_map.items():
            f.write(f'    {{"{pinyin}", "{" ".join(sorted(hanzi_set)).replace(" ", "")}"}},\n')
        f.write("};\n\n")
        f.write("#endif\n")

if __name__ == "__main__":
    main()
