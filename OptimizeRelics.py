import time
import json
from Config import weapon_dict, weapon_type_dict, main_attribute_to_value_dict, suite_buff_dict
from Config import connect
import copy
# to be continued
import multiprocessing.managers


class Weapon:
    def __init__(self, weapon_name: str):
        self.weapon_name = ""
        for key in weapon_dict:
            if weapon_name == weapon_dict[key]['name']:
                self.weapon_name = weapon_dict[key]['name']
                self.attack = weapon_dict[key]['attack']
                self.type = weapon_dict[key]['type']
                self.main_attribute = weapon_dict[key]['main_attribute']
                self.main_attribute_value = weapon_dict[key]['main_attribute_value']
        if self.weapon_name == "":
            print("This weapon dose not exist.")

    def show_weapon_info(self):
        print("Weapon Name: {0};\nWeapon attack: {1};\nWeapon type: {2}\nMain Attribute: {3}\nValue: {4}\n".format(
            self.weapon_name, self.attack, weapon_type_dict[self.type], self.main_attribute, self.main_attribute_value))


class Relic:
    def __init__(self, key: int, attributes: dict):
        try:
            self.no = key
            self.name = attributes['name']
            self.place = attributes['place']
            self.suite = attributes['suite'].strip('：')
            self.rank = attributes['rank']
            self.main_attribute = attributes['main_attribute']
            if self.place == '死之羽':
                self.main_attribute_value = 311
            elif self.place == '生之花':
                self.main_attribute_value = 4780
            else:
                self.main_attribute_value = main_attribute_to_value_dict.get(self.main_attribute, 0)
            self.sub_attributes = attributes['sub_attributes']
        except:
            print("Relic data wrong.")

    def show_relic_info(self):
        print(
            "Relic Number: {0};\nRelic Name: {1};\nPlace: {2};\nSuite: {3};\nMain Attribute: {4};".format(
                self.no, self.name, self.place, self.suite, self.main_attribute))
        print("Attribute Value: {0};\n".format(self.sub_attributes))


class RelicsDataSet:
    def __init__(self, relic_json_path: str):
        self.relics_json_file = open(relic_json_path, "r", encoding='utf-8')
        self.all_relics = json.load(self.relics_json_file)
        cur = connect.cursor()
        sql = '''DROP TABLE relics'''
        cur.execute(sql)
        sql = '''CREATE TABLE IF NOT EXISTS relics(id int primary key,name text, place text, main_attribute text, attributes text, rank int, suite text);'''
        cur.execute(sql)
        for relic_key in self.all_relics.keys():
            relic = self.all_relics[relic_key]
            relic = Relic(relic_key, relic)
            sql = '''INSERT INTO relics VALUES (?,?,?,?,?,?,?)'''
            cur.execute(sql, (
                relic.no, relic.name, relic.place, relic.main_attribute, str(relic.sub_attributes), relic.rank,
                relic.suite))
        connect.commit()
        print("Relics dataset successfully updated.")

    @staticmethod
    def select(place: str = "default", main_attribute: str = "default", suite: str = "default", rank: int = 20,
               conn=" AND "):
        cursor = connect.cursor()
        place_need = "place = " + "\"" + place + "\""
        main_attribute_need = "main_attribute = " + "\"" + main_attribute + "\""
        suite_need = "suite = " + "\"" + suite + "\""

        combined_need = "WHERE rank = 20"
        if place != "default":
            combined_need += conn + place_need
        if main_attribute != "default":
            combined_need += conn + main_attribute_need
        if suite != "default":
            combined_need += conn + suite_need
        sql = """SELECT * FROM relics {0}""".format(combined_need)
        print("SQL语句: " + sql, end=",")
        result_relics = []
        for relic in cursor.execute(sql):
            r = Relic(relic[0],
                      {'name': relic[1], 'place': relic[2], 'main_attribute': relic[3],
                       'sub_attributes': eval(relic[4]),
                       'rank': relic[5], 'suite': relic[6]})
            result_relics.append(r)
        print("总计{0}条查询结果。".format(len(result_relics)))
        return result_relics


class Character:
    def __init__(self, character_name: str, weapon_name: str, relic_suite: list, relic_suite_num: list,
                 strict: dict = {}):
        information = read_character_base_info(character_name)
        self.talent = 0
        if 'talent' in information.keys():
            self.talent = information['talent']
        self.name = information['name']
        self.element = information['element']
        self.attack, self.defence = information['baseInfo']['attack'], information['baseInfo']['defence']
        self.hp, self.break_info = information['baseInfo']['hp'], information['baseInfo']['breakInfo']
        self.origin_attack = self.attack
        self.all_relics = RelicsDataSet("assets/RelicsNew.json")

        self.flower = self.all_relics.select(place="生之花")
        self.feather = self.all_relics.select(place="死之羽")
        self.sandglass = self.all_relics.select(place="时之沙")
        self.cup = self.all_relics.select(place="空之杯")
        self.hat = self.all_relics.select(place="理之冠")
        self.relics = [self.flower, self.feather, self.sandglass, self.cup, self.hat]

        self.best_relics = {}
        self.best_damage = 0
        self.places = {"生之花": None, "死之羽": None, "时之沙": None, "空之杯": None, "理之冠": None}

        self.additional_attack = 0
        self.additional_fixed_attack = 0
        self.additional_hp = 0
        self.additional_fixed_hp = 0
        self.additional_defence = 0
        self.additional_fixed_defence = 0
        self.critical_rate = 0.05
        self.critical_damage = 0.50
        self.element_damage = 0
        self.element_master = 0
        self.element_charge = 1.00
        self.heal_rate = 0

        self.weapon = Weapon(weapon_name=weapon_name)
        self.buff_info = None
        self.suite = {key: 0 for key in suite_buff_dict.keys()}
        self.strict = strict
        self.relicSuite = relic_suite
        self.relicSuiteNum = relic_suite_num

        self.__init_suite(relic_suite)
        self.__set_suite_buff()
        self.__add_break_buff()
        self.__set_weapon_attribute()

    def __add_talent_buff(self):
        if self.talent == 1:
            self.element_damage += (self.element_charge - 1) * 0.4

    def __init_attributes(self):
        self.attack = self.origin_attack
        self.additional_attack = 0
        self.additional_fixed_attack = 0
        self.additional_hp = 0
        self.additional_fixed_hp = 0
        self.additional_defence = 0
        self.additional_fixed_defence = 0
        self.critical_rate = 0.05
        self.critical_damage = 0.50
        self.element_damage = 0
        self.element_master = 0
        self.element_charge = 1.00
        self.heal_rate = 0
        self.__set_suite_buff()
        self.__add_break_buff()
        self.__set_weapon_attribute()

    def optimaze_relics(self, attack_type: str = '攻击'):
        self.best_damage = self.calculate_self_damage_average(attack_type=attack_type)
        self.__search_all(self.relics[0], iter_depth=0, attack_type=attack_type)

    def __search_all(self, relics: list, iter_depth: int, attack_type: int = 1):
        if iter_depth < 4:
            for relic in relics:
                self.set_relic(relic)
                self.__search_all(self.relics[iter_depth + 1], iter_depth=iter_depth + 1, attack_type=attack_type)
        else:
            for relic in relics:
                self.set_relic(relic)
                if self.__check_suite(suite_name=self.relicSuite, suite_num=self.relicSuiteNum):
                    self.__add_relic_attributes()
                    self.__set_weapon_buff()
                    self.__add_talent_buff()
                    if self.__fit_strict():
                        damage = self.calculate_self_damage_average(attack_type=attack_type)
                        if damage > self.best_damage:
                            self.best_damage = copy.deepcopy(damage)
                            self.best_relics = copy.deepcopy(self.places)
                    self.__init_attributes()

    def __fit_strict(self):
        strict = self.strict
        if strict == {}:
            return True
        for attribute_name in strict.keys():
            attribute_strict = strict[attribute_name]
            if '攻击力' == attribute_name:
                total_attack = self.attack + self.attack * self.additional_attack + self.additional_fixed_attack
                if attribute_strict[0] > total_attack or attribute_strict[1] < total_attack:
                    return False
            elif '防御力' == attribute_name:
                total_defence = self.defence + self.defence * self.additional_defence + self.additional_fixed_defence
                if attribute_strict[0] > total_defence or attribute_strict[1] < total_defence:
                    return False
            elif '生命值' == attribute_name:
                total_hp = self.hp + self.hp * self.additional_hp + self.additional_fixed_hp
                if attribute_strict[0] > total_hp or attribute_strict[1] < total_hp:
                    return False
            elif '暴击率' == attribute_name:
                if attribute_strict[0] > self.critical_rate or attribute_strict[1] < self.critical_rate:
                    return False
            elif '暴击伤害' == attribute_name:
                if attribute_strict[0] > self.critical_damage or attribute_strict[1] < self.critical_damage:
                    return False
            elif '伤害' in attribute_name:
                if self.element in attribute_name:
                    if attribute_strict[0] > self.element_damage or attribute_strict[1] < self.element_damage:
                        return False
            elif '元素精通' == attribute_name:
                if attribute_strict[0] > self.element_master or attribute_strict[1] < self.element_master:
                    return False
            elif '元素充能效率' == attribute_name:
                if attribute_strict[0] > self.element_charge or attribute_strict[1] < self.element_charge:
                    return False
            elif '治疗加成' == attribute_name:
                if attribute_strict[0] > self.heal_rate or attribute_strict[1] < self.heal_rate:
                    return False
            else:
                print(attribute_name)
                print("This relic entry has not occurred. ( Tested in __fitStrict() )")
                return False
            return True

    def __check_suite(self, suite_name: list, suite_num: list):

        l1, l2 = len(suite_name), len(suite_num)
        assert l1 == l2
        for i in range(l1):
            suite, num = suite_name[i], suite_num[i]
            if self.suite[suite] < num:
                return False
        return True

    def __set_weapon_attribute(self):
        self.set_weapon(self.weapon)

    def __set_weapon_buff(self):
        if self.weapon.weapon_name == '薙草之稻光':
            self.additional_attack += min(0.8, (self.element_charge - 1) * 0.28)

    def __set_suite_buff(self, flag=1):
        for suite in suite_buff_dict.keys():
            if self.suite[suite] >= 2:
                attribute_name = suite_buff_dict[suite][0]
                attribute_value = suite_buff_dict[suite][1] * flag
                self.__add_attribute(attribute_name, attribute_value)

    def __init_suite(self, suite_name: list):
        for suite in suite_name:
            select_result = self.all_relics.select(suite=suite)
            if len(select_result) == 0:
                print("This relic suite {0} dose not exist.".format(suite))
                return False

        self.best_relics = copy.deepcopy(self.places)
        return True

    def set_relic(self, relic: Relic):
        if relic.place in self.places.keys():
            self.__del_relic(relic.place)
            self.__add_relic(relic)
            return True
        else:
            print("This place name dose not exist.")
            return False

    def __add_relic_attributes(self, best=False):
        if best:
            places = self.best_relics
        else:
            places = self.places

        for place in places.keys():
            relic = places[place]
            if relic is None:
                print("This place have not been equipped with relic")
                continue
            attributes = relic.sub_attributes
            for attribute in attributes:
                attribute_name = attribute[0]
                attribute_value = attribute[1]
                if not self.__add_attribute(attribute_name, attribute_value):
                    print("Add {0} relic subattribute {1} error.".format(relic.no, attribute_name))

    def __del_relic(self, place: str = ""):
        if self.places[place] is not None:
            # 修改对应套装件数
            self.suite[self.places[place].suite] -= 1
            # 对应位置置空
            self.places[place] = None

    def __add_relic(self, relic: Relic):
        if self.places[relic.place] is None:
            # 修改对应套装件数
            self.suite[relic.suite] += 1
            # 圣遗物设置
            self.places[relic.place] = relic

    def __add_break_buff(self):
        buff_name = self.break_info[0]
        buff_value = self.break_info[1]
        if not self.__add_attribute(buff_name, buff_value):
            print("Add break buff error.")

    def show_relics_combination(self):
        for relic_key in self.best_relics:
            relic = self.best_relics[relic_key]
            if relic:
                relic.show_relic_info()
            else:
                print("Not equipped with relic.")

    def show_character_info(self):
        self.__add_relic_attributes(best=True)
        self.__set_weapon_buff()
        self.__add_talent_buff()
        white_attack = self.attack
        green_attack = self.attack * self.additional_attack + self.additional_fixed_attack
        white_defense = self.defence
        green_defense = self.defence * self.additional_defence + self.additional_fixed_defence
        white_hp = self.hp
        green_hp = self.hp * self.additional_hp + self.additional_fixed_hp
        print("攻击力：{0}+{1}, 总计：{2}".format(white_attack, green_attack, white_attack + green_attack))
        print("防御力：{0}+{1}, 总计：{2}".format(white_defense, green_defense, white_defense + green_defense))
        print("生命值：{0}+{1}, 总计：{2}".format(white_hp, green_hp, white_hp + green_hp))
        print("暴击率：", self.critical_rate)
        print("暴击伤害：", self.critical_damage)
        print("元素精通：", self.element_master)
        print("元素充能效率：", self.element_charge)
        print("元素增伤：", self.element_damage)
        print("武器：", self.weapon)
        print(self.best_relics)
        self.show_relics_combination()
        self.__init_attributes()

    def set_weapon(self, weapon: Weapon):

        self.weapon = weapon
        self.attack += weapon.attack
        if not self.__add_attribute(weapon.main_attribute, weapon.main_attribute_value):
            print("Add weapon attribute error.")

    def calculate_self_damage_average(self, attack_type='攻击'):
        if '攻击' == attack_type:
            return (self.attack * (1 + self.additional_attack) + self.additional_fixed_attack) * \
                   (1 + self.critical_damage) * (1 + self.element_damage) * \
                   min(1.00, self.critical_rate) + (
                               self.attack * (1 + self.additional_attack) + self.additional_fixed_attack) * (
                               1 + self.element_damage) * max(0.00, 1 - self.critical_rate)
        elif '防御' == attack_type:
            return (self.defence * (1 + self.additional_defence) + self.additional_fixed_defence) * \
                   (1 + self.critical_damage) * (1 + self.element_damage) * \
                   min(1.00, self.critical_rate) + (
                               self.defence * (1 + self.additional_defence) + self.additional_fixed_defence) * (
                               1 + self.element_damage) * max(0.00, 1 - self.critical_rate)
        elif '生命' == attack_type:
            return (self.hp * (1 + self.additional_hp) + self.additional_fixed_hp) * \
                   (1 + self.critical_damage) * (1 + self.element_damage) * \
                   min(1.00, self.critical_rate) + (self.hp * (1 + self.additional_hp) + self.additional_fixed_hp) * (
                           1 + self.element_damage) * max(0.00, 1 - self.critical_rate)
        else:
            return (self.attack * (1 + self.additional_attack) + self.additional_fixed_attack) * \
                   (1 + self.critical_damage) * (1 + self.element_damage) * \
                   min(1.00, self.critical_rate) + (
                               self.attack * (1 + self.additional_attack) + self.additional_fixed_attack) * (
                               1 + self.element_damage) * max(0.00, 1 - self.critical_rate)

    def __add_attribute(self, attribute_name, attribute_value):
        attribute_value = round(attribute_value, 3)
        if '攻击力' == attribute_name:
            if abs(attribute_value) > 1:
                self.additional_fixed_attack += attribute_value
            else:
                self.additional_attack += attribute_value
        elif '防御力' == attribute_name:
            if abs(attribute_value) > 1:
                self.additional_fixed_defence += attribute_value
            else:
                self.additional_defence += attribute_value
        elif '生命值' == attribute_name:
            if abs(attribute_value) > 1:
                self.additional_fixed_hp += attribute_value
            else:
                self.additional_hp += attribute_value
        elif '暴击率' == attribute_name:
            self.critical_rate += attribute_value
        elif '暴击伤害' == attribute_name:
            self.critical_damage += attribute_value
        elif '伤害' in attribute_name:
            if self.element in attribute_name:
                self.element_damage += attribute_value
        elif '元素精通' == attribute_name:
            self.element_master += attribute_value
        elif '元素充能效率' == attribute_name:
            self.element_charge += attribute_value
        elif '治疗加成' == attribute_name:
            self.heal_rate += attribute_value
        else:
            print(attribute_name)
            print("This relic entry has not occurred.")
            return False
        return True


def read_character_base_info(character_name='旅行者'):
    with open('assets/CharacterInfo.json', 'r', encoding='utf-8') as file:
        characters_info = json.load(file)
        for info in characters_info:
            if info['name'] == character_name:
                return info
        print("This character's information hasn't been loaded.")
        return info['旅行者']


def test():
    start = time.time()
    ganyu = Character("夜兰", "西风猎弓", ["绝缘之旗印"], [4], {'元素充能效率': [1.8, 2.0],"暴击率":[0.5,0.65],"暴击伤害":[1.6,1.8]})
    ganyu.optimaze_relics(attack_type='生命')
    ganyu.show_character_info()
    print("用时{0}s.".format(time.time() - start))


if __name__ == "__main__":
    test()
    # tree.root.left = Node(2,Node(4),Node(5))
    # tree.root.right = Node(3,Node(6),Node(7))