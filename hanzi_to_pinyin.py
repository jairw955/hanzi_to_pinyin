import pypinyin
from pypinyin import pinyin, Style
import re
import sys
from collections import defaultdict

# 定义一个函数，将汉字转换为拼音
def hanzi_to_pinyin(hanzi):
    # 使用 pypinyin 转换为拼音
    initials = pinyin(hanzi, style=Style.INITIALS, strict=False)  # 设置 strict=False
    finals = pinyin(hanzi, style=Style.FINALS_TONE3, strict=False)  # 设置 strict=False
    # 提取拼音并格式化
    formatted_pinyin = []
    for initial, final in zip(initials, finals):
        initial = initial[0] if initial[0] else ""
        final = final[0]
        # 格式化为 "声母 韵母" 的形式
        formatted_pinyin.append(f"{initial} {final}" if initial else final)
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
    hanzi_to_pinyin_map = {}
    for hanzi in hanzi_list:
        pinyin_list = hanzi_to_pinyin(hanzi)
        hanzi_to_pinyin_map[hanzi] = pinyin_list[0]  # 只取第一个拼音
        for pinyin in pinyin_list:
            # 去掉声调数字
            pinyin_no_tone = ''.join(filter(lambda x: not x.isdigit(), pinyin)).replace(" ", "")
            pinyin_to_hanzi[pinyin_no_tone].add(hanzi)
    return hanzi_to_pinyin_map, pinyin_to_hanzi

# 主函数
def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    hanzi_list = read_hanzi_from_file(file_path)
    hanzi_to_pinyin_map, pinyin_to_hanzi_map = generate_pinyin_to_hanzi_map(hanzi_list)

    # 按照 Unicode 顺序排序汉字到拼音的映射
    sorted_hanzi_to_pinyin_map = dict(sorted(hanzi_to_pinyin_map.items(), key=lambda item: item[0]))

    # 按照字母顺序排序拼音到汉字的映射
    sorted_pinyin_to_hanzi_map = dict(sorted(pinyin_to_hanzi_map.items(), key=lambda item: item[0]))

    # 保存汉字到拼音的映射为 C 语言数组
    with open('hanzi_to_pinyin.h', 'w', encoding='utf-8') as f:
        f.write("#ifndef __HANZI_TO_PINYIN_H__\n")
        f.write("#define __HANZI_TO_PINYIN_H__\n\n")
        f.write("typedef struct {\n")
        f.write("    wchar_t hanzi;\n")
        f.write("    char *pinyin;\n")
        f.write("} HanziPinyin;\n\n")
        f.write("HanziPinyin hanzi_to_pinyin[] = {\n")
        for hanzi, pinyin in sorted_hanzi_to_pinyin_map.items():
            f.write(f'    {{L\'{hanzi}\', "{pinyin}"}},\n')
        f.write("};\n\n")
        f.write("#endif\n")

    # 保存拼音到汉字的映射为 C 语言数组
    with open('pinyin_to_hanzi.h', 'w', encoding='utf-8') as f:
        f.write("#ifndef __PINYIN_TO_HANZI_H__\n")
        f.write("#define __PINYIN_TO_HANZI_H__\n\n")
        f.write("const char *pinyin_to_hanzi[] = {\n")
        for pinyin, hanzi_set in sorted_pinyin_to_hanzi_map.items():
            f.write(f'    "{pinyin}", "{" ".join(sorted(hanzi_set)).replace(" ", "")}",\n')
        f.write("};\n\n")
        f.write("#endif\n")

if __name__ == "__main__":
    main()
