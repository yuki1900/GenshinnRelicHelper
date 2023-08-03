# 圣遗物背包中每行中每两个圣遗物之间的间隔像素
relic_margin_pixel = 196
relic_per_row = 8
# 个性化设置中的缩放比例
proportion = 0.8
attribute_standard_dict = {
    '攻击力': [[0, 1], [10, 400]], '生命值': [[0, 1], [150, 2000]], '防御力': [[0, 1], [10, 400]], '治疗加成': [[0, 1]],
    '元素精通': [[10, 200]], '元素充能效率': [[0, 1]], '暴击率': [[0, 1]], '暴击伤害': [[0, 1]],
    '物理伤害加成': [[0, 1]], '岩元素伤害加成': [[0, 1]], '风元素伤害加成': [[0, 1]], '雷元素伤害加成': [[0, 1]],
    '火元素伤害加成': [[0, 1]], '水元素伤害加成': [[0, 1]], '冰元素伤害加成': [[0, 1]],
}

main_attribute_to_value_dict = {
    '攻击力': 0.466, '生命值': 0.466, '防御力': 0.583, '治疗加成': 0.359,
    '元素精通': 187, '元素充能效率': 0.518, '暴击率': 0.311, '暴击伤害': 0.622,
    '物理伤害加成': 0.583, '岩元素伤害加成': 0.466, '风元素伤害加成': 0.466, '雷元素伤害加成': 0.466,
    '火元素伤害加成': 0.466, '水元素伤害加成': 0.466, '冰元素伤害加成': 0.466,
}

weapon_type_dict = {1: '弓箭', 2: '法器', 3: '双手剑', 4: '单手剑', 5: '长柄武器'}

weapon_dict = {
    1: {'name': "阿莫斯之弓", 'type': 1, 'attack': 608, 'main_attribute': '攻击力', 'main_attribute_value': 0.496},
    2: {'name': "天空之翼", 'type': 1, 'attack': 674, 'main_attribute': '暴击率', 'main_attribute_value': 0.221},
    3: {'name': "狼的末路", 'type': 3, 'attack': 608, 'main_attribute': '攻击力', 'main_attribute_value': 0.496},
    4: {'name': "薙草之稻光", 'type': 5, 'attack': 608, 'main_attribute': '元素充能效率', 'main_attribute_value': 0.551,
        'buff': 1},
    5: {'name': "辰砂之纺锤", 'type': 4, 'attack': 454, 'main_attribute': '防御力', 'main_attribute_value': 0.69},
    6: {'name': "若水", 'type': 1, 'attack': 542, 'main_attribute': '暴击伤害', 'main_attribute_value': 0.882},
    7: {'name': "西风猎弓", 'type': 1, 'attack': 454, 'main_attribute': '元素充能效率', 'main_attribute_value': 0.613}
}

relic_info_dict = {
    'name': None,
    'place': None,
    'main_attribute': None,
    'rank': None,
    'suite': None,
    'sub_attributes': None,
}
# screen_shoot_position_list = [1745, 160, 645, 740]

relic_info_position_dict = {
    #  'captured_screen': [1745, 160, 645, 740],
    'captured_screen': [1745, 160 + 36, 645, 740],
    'name': [20, 5, 575, 65],
    'place': [15, 90, 120, 40],
    'main_attribute': [15, 190, 240, 55],
    'rank': [25, 405, 100, 50],
    'suite': [10, 680, 360, 50],
    'sub_attributes': [60, 475, 360, 200],
}


def EngulfingLightningBuff(element_charge: float):
    return (element_charge - 1) * 0.28


suite_buff_dict = {
    '海染砗磲': ['治疗加成', 0.2],
    '华馆梦醒形骸记': ['防御力', 0.3],
    '绝缘之旗印': ['元素充能效率', 0.2],
    '追忆之注连': ['攻击力', 0.18],
    '苍白之火': ['攻击力', 0.18],
    '千岩牢固': ['生命值', 0.2],
    '沉沦之心': ['水元素伤害加成', 0.15],
    '悠古的磐岩': ['岩元素伤害加成', 0.15],
    '染血的骑士道': ['攻击力', 0.18],
    '昔日宗室之仪': ['元素爆发伤害加成', 0.2],
    '炽烈的炎之魔女': ['火元素伤害加成', 0.15],
    '流浪大地的乐团': ['元素精通', 80],
    '翠绿之影': ['风元素伤害加成', 0.15],
    '角斗士的终幕礼': ['攻击力', 0.18],
    '被怜爱的少女': ['治疗加成', 0.2],
    '渡过烈火的贤人': ['生命值', 0.2],
    '冰风迷途的勇士': ['冰元素伤害加成', 0.15],
    '来歆余响': ['攻击力', 0.18],
    '辰砂往生录': ['攻击力', 0.18],
}

import sqlite3

connect = sqlite3.connect("relics.db")

if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    d = {"a": None}
