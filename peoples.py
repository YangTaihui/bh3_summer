from util import *


class KaiWen(People):
    def __init__(self):
        super().__init__()
        self.name = '凯文'
        self.skill_name = '清凉一夏'
        self.talent_name = '炎热归零 (斩杀技)'
        self.ATK = 20
        self.DEF = 11
        self.speed = 21
        self.skill_wait = 3
        self.talent_probability = 30
        self.talent_time = 1

    def talent_additional_judgment(self, p2):
        if not self.confuse:
            if p2.HP / p2.HP_FULL < 0.3:
                return True
        return False

    def talent(self, p2):
        return [self.hit_info(hit_value=p2.HP + 1, can_block=0)]

    def skill(self, p2):
        self.ATK += 5
        p2.HP = 0
        return self.player_number


class V2V(People):
    def __init__(self):
        super().__init__()
        self.name = '维尔薇'
        self.skill_name = '创（造）力'
        self.talent_name = '大变活人'
        self.ATK = 20
        self.DEF = 12
        self.speed = 25
        self.skill_wait = 3
        self.talent_counter = 1
        self.talent_probability = 100
        self.talent_time = 0

    def talent_additional_judgment(self, p2):
        if self.HP < 31:
            return True
        return False

    def talent(self, p2: People):
        self.HP += random.randint(10, 20)
        p2.HP += random.randint(10, 20)
        if self.talent_counter:
            atk_add = random.randint(2, 15)
            if self.print_info:
                print(f'    {self.name}永久提升攻击力{atk_add}点')
            self.ATK += atk_add
            self.talent_counter -= 1

    def skill(self, p2):
        p2.confuse = True
        return [self.hit_info(hit_value=self.ATK)]


class KeSiMo(People):
    def __init__(self):
        super().__init__()
        self.name = '科斯魔'
        self.skill_name = '邪渊之钩'
        self.talent_name = '不归之爪'
        self.ATK = 19
        self.DEF = 11
        self.speed = 19
        self.skill_wait = 2
        self.talent_probability = 15
        self.talent_time = 1

    def talent(self, p2):
        p2.split = 3
        p2.delay_hurt = [self.hit_info(hit_value=4, can_block=False, split=True) for _ in range(3)]
        if self.print_info:
            print(f'    {p2.name}裂开了')

    def skill(self, p2):
        hit_info_list = []
        for i in range(4):
            hit_info_list.append(self.hit_info(hit_value=random.randint(11, 22)))
            if p2.split:
                hit_info_list.append(self.hit_info(hit_value=3, can_block=False))
        return hit_info_list


class ABoNiYa(People):
    def __init__(self):
        super().__init__()
        self.name = '阿波尼亚'
        self.skill_name = '深蓝之槛'
        self.talent_name = '该休息了'
        self.ATK = 21
        self.DEF = 10
        self.speed = 30
        self.skill_wait = 4
        self.talent_probability = 30
        self.talent_time = 1

    def talent(self, p2: People):
        if self.confuse:
            self.mute = True
            if self.print_info:
                print(f'    {self.name}由于混乱被自己沉默')
        else:
            p2.mute = True
            if self.print_info:
                print(f'    {p2.name}被沉默')

    def skill(self, p2: People):
        p2.seal = True
        if self.print_info:
            print(f'    {p2.name}被封印')
        return [self.hit_info(hit_value=self.ATK, multi=1.7)]


class GeLeiXiu(People):
    def __init__(self):
        super().__init__()
        self.name = '格蕾修'
        self.skill_name = '水彩泡影'
        self.talent_name = '沙滩监护人'
        self.ATK = 16
        self.DEF = 11
        self.speed = 18
        self.skill_wait = 3
        self.talent_probability = 40
        self.talent_time = 0

    def talent(self, p2: People):
        self.DEF = min(21, self.DEF + 2)
        if self.print_info:
            print(f'    {self.name}防御力永久提升2点 (DEF={self.DEF})')

    def skill(self, p2: People):
        hit_info_list = []
        if self.shield:
            hit_info_list.append(self.hit_info(hit_value=self.DEF))
        self.shield = 15
        return hit_info_list


class Cat(People):
    def __init__(self):
        super().__init__()
        self.name = '帕朵菲莉丝'
        self.skill_name = '沙滩寻宝'
        self.talent_name = '最佳拍档'
        self.ATK = 17
        self.DEF = 10
        self.speed = 24
        self.skill_wait = 3
        self.talent_probability = 30
        self.talent_time = 1

    def talent(self, p2: People):
        if self.print_info:
            print(f'    {self.name}召唤罐头造成30点伤害')
        return [self.hit_info(hit_value=30)]

    def skill(self, p2: People):
        return [self.hit_info(hit_value=30, hemophagia=True)]


class AiLiXiYa(People):
    def __init__(self):
        super().__init__()
        self.name = '爱莉希雅'
        self.skill_name = '夏梦之花'
        self.talent_name = '水花溅射'
        self.ATK = 21
        self.DEF = 8
        self.speed = 20
        self.skill_wait = 2
        self.talent_probability = 35
        self.talent_time = 1

    def talent(self, p2: People):
        if self.confuse:
            self.talent_hurt_self = True
            if self.print_info:
                print(f'    {self.name}由于混乱波动技能攻击自己')
        return [self.hit_info(hit_value=11, can_block=False)]

    def skill(self, p2: People):
        p2.ATK_change = dict(change_times=1, change_value=6, recover=True)
        if self.print_info:
            print(f'    {p2.name}下回合攻击力下降6点')
        return [self.hit_info(hit_value=random.randint(25, 50))]


class MeiBiWuSi(People):
    def __init__(self):
        super().__init__()
        self.name = '梅比乌斯'
        self.skill_name = '栖息水枪'
        self.talent_name = '不稳定物质'
        self.ATK = 21
        self.DEF = 11
        self.speed = 23
        self.skill_wait = 3
        self.talent_probability = 33
        self.talent_time = 1

    def talent_additional_judgment(self, p2):
        if p2.simple_atk_hurt:
            return True
        return False

    def talent(self, p2: People):
        if self.confuse:
            self.DEF = max(0, self.DEF - 3)
            if self.print_info:
                print(f'    {self.name}由于混乱自身防御力永久下降3点 (DEF={self.DEF})')
        else:
            p2.DEF = max(0, p2.DEF - 3)
            if self.print_info:
                print(f'    {p2.name}防御力永久下降3点 (DEF={p2.DEF})')

    def skill(self, p2: People):
        if random.randint(1, 100) <= 33:
            p2.seal = True
            if self.print_info:
                print(f'    {p2.name}昏迷一回合')
        return [self.hit_info(hit_value=33)]


class Hua(People):
    def __init__(self):
        super().__init__()
        self.name = '华'
        self.skill_name = '上伞若水'
        self.talent_name = '攻守兼备 (固定20%减伤)'
        self.ATK = 21
        self.DEF = 12
        self.speed = 15
        self.skill_wait = 2
        self.talent_probability = 100
        self.talent_time = 0
        self.de_hurt = 0.2

    def talent(self, p2: People):
        pass

    def skill(self, p2: People):
        self.DEF += 3
        self.DEF_change = dict(change_times=1, change_value=-3, recover=False)
        next_hit_value = random.randint(10, 33)
        if self.print_info:
            print(f'    {self.name}至下回合行动前防御力上升3点 (DEF={self.DEF}), 下次攻击额外造成{next_hit_value}点元素伤害')
        self.delay_attack_after_act = [None, self.hit_info(hit_value=next_hit_value, can_block=False)]
