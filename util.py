import random


# 需注意: random.randint是左闭右闭, np.random.randint是左闭右开chr(12288)

class People:

    def __init__(self):
        self.name = ''
        self.skill_name = ''  # 主动技能
        self.talent_name = ''  # 被动技能
        self.HP_FULL = 100
        self.HP = 100
        self.HP_before_attack = 100  # 回合开始前的生命值(V2V对科斯魔, V2V的被动基于此值, 而非受撕裂伤害后的HP)
        self.ATK_ROW = 0  # 初始攻击力
        self.ATK = 0
        self.DEF = 0
        self.speed = 0
        self.skill_wait = 1  # 每几个回合释放主动技能
        self.talent_probability = 1  # 被动发动概率
        self.talent_time = 0  # 被动发动时间 0回合开始, 1行动后
        self.print_info = True  # 是否打印信息

        self.player_number = 1  # 比赛编号
        self.multi = 1  # 倍率
        self.seal = False  # 封印状态, 无法行动
        self.mute = False  # 沉默状态, 只能普攻
        self.confuse = False  # 混乱状态
        self.talent_hurt_self = False  # 天赋攻击自己
        self.talent_not_mute = False  # 天赋不被沉默
        self.split = 0  # 撕裂层数, 0即没有撕裂状态
        self.shield = 0  # 护盾值, 0即没有护盾
        self.delay_hurt = []  # 受到延迟伤害
        self.delay_attack_before_act = []  # 延迟的行动前攻击
        self.delay_attack_after_act = []  # 延迟的行动后攻击
        self.speed_change = None  # 速度变化字典, key: change_times, change_value, recover(恢复)
        self.ATK_change = None  # 攻击力变化字典, key: change_times, change_value, recover(恢复)
        self.DEF_change = None  # 防御力变化字典, key: change_times, change_value, recover(恢复)
        self.simple_atk_hurt = 0  # 普攻造成伤害
        self.de_hurt = 0  # 减伤, 受到伤害为 hurt*(1-de_hurt)
        self.evade = 0  # 闪避, 0-100, 0即没有闪避率, 15即15%闪避率
        self.evade_state = False  # 闪避所有攻击

    def print_attack(self, attack_type):
        """
        打印攻击信息
        0: talent, 1: attack, 2: skill
        """
        if self.print_info:
            attack_dict = {0: self.talent_name, 1: '普通攻击', 2: self.skill_name}
            print(f'{self.name}发动{attack_dict[attack_type]}!')

    def attack(self, p2, epoch):
        """
        一回合的攻击
        :return: 0:无人获胜, 1:self 获胜, 2:p2 获胜
        """
        self.HP_before_attack = self.HP
        # 速度升降
        if self.speed_change is not None:
            assert self.speed_change['change_times'] in [-1, 1]
            if self.speed_change['change_times'] == 1:
                # if self.print_info:
                #     print(f'    {self.name}速度变化 (speed: {self.speed} -> ', end='')
                self.speed += self.speed_change['change_value']
                # if self.print_info:
                #     print(f'{self.speed})')
                if self.speed_change['recover']:
                    self.speed_change = dict(change_times=1, change_value=-self.speed_change['change_value'], recover=False)
                else:
                    self.speed_change = None
            else:
                self.speed_change['change_times'] = 1

        # 攻击力升降
        if self.ATK_change is not None:
            assert self.ATK_change['change_times'] in [-1, 1]
            if self.ATK_change['change_times'] == 1:
                if self.print_info:
                    print(f'    {self.name}攻击力变化 (ATK: {self.ATK} -> {self.ATK+self.ATK_change["change_value"]})')
                self.ATK += self.ATK_change['change_value']
                if self.ATK_change['recover']:
                    self.ATK_change = dict(change_times=1, change_value=-self.ATK_change['change_value'], recover=False)
                else:
                    self.ATK_change = None
            else:
                self.ATK_change['change_times'] = 1

        # 防御力升降
        if self.DEF_change is not None:
            assert self.DEF_change['change_times'] in [-1, 1]
            if self.DEF_change['change_times'] == 1:
                if self.print_info:
                    print(f'    {self.name}防御力变化 (DEF: {self.DEF} -> {self.DEF+self.DEF_change["change_value"]})')
                self.DEF += self.DEF_change['change_value']
                if self.DEF_change['recover']:
                    self.DEF_change = dict(change_times=1, change_value=-self.DEF_change['change_value'], recover=False)
                else:
                    self.DEF_change = None
            else:
                self.DEF_change['change_times'] = 1

        # 撕裂伤害
        if len(self.delay_hurt):
            delay_hurt = self.delay_hurt.pop(0)
            if delay_hurt['split']:
                self.split -= 1
            if self.print_info:
                print(f'    {self.name}受延迟伤害')
            winner = self.be_hit([delay_hurt])
            if winner:
                return winner

        # 封印状态, 无法行动  
        if self.seal:
            self.seal = False
            self.delay_attack_before_act = []
            self.delay_attack_after_act = []
            return 0

        # 未被沉默
        self.simple_atk_hurt = 0
        if not self.mute:

            # 回合开始的被动技能
            if self.talent_time == 0:
                if self.talent_hurt_self:
                    self.talent_hurt_self = False
                    winner = self.be_hit(self.run_talent(p2))
                else:
                    winner = p2.be_hit(self.run_talent(p2))
                if winner:
                    return winner

            # 行动前的延迟攻击
            if len(self.delay_attack_before_act):
                winner = p2.be_hit([self.delay_attack_before_act.pop(0)])
                if winner:
                    return winner

            # 释放主动技能, 不能普攻
            if epoch % self.skill_wait == 0:
                winner = p2.be_hit(self.run_skill(p2))
            else:  # 没有释放主动技能, 可以普攻
                if self.confuse:
                    if self.print_info:
                        print(f'    {self.name}受混乱影响将攻击自己')
                    self.confuse = False
                    winner = self.be_hit(self.simple_atk())
                else:
                    p2_HP_before_simple_atk = p2.HP
                    winner = p2.be_hit(self.simple_atk())
                    self.simple_atk_hurt = p2_HP_before_simple_atk - p2.HP
            if winner:
                return winner

            # 行动后的延迟攻击
            if len(self.delay_attack_after_act):
                delay_attack_after_act = self.delay_attack_after_act.pop(0)
                if delay_attack_after_act is not None:
                    winner = p2.be_hit([delay_attack_after_act])
                    if winner:
                        return winner

            # 行动后的被动技能
            if self.talent_time == 1:
                if self.talent_hurt_self:
                    self.talent_hurt_self = False
                    winner = self.be_hit(self.run_talent(p2))
                else:
                    winner = p2.be_hit(self.run_talent(p2))
                if winner:
                    return winner

        # 被沉默但天赋免疫沉默, QianJie
        elif self.talent_not_mute:
            self.mute = False
            # 回合开始的被动技能
            self.run_talent(p2)
            # 普攻
            if self.confuse:
                self.confuse = False
                if self.print_info:
                    print(f'    {self.name}受混乱影响将攻击自己')
                winner = self.be_hit(self.simple_atk())
            else:
                winner = p2.be_hit(self.simple_atk())
            if winner:
                return winner
        # 被沉默，只能普攻
        else:
            self.mute = False
            if self.confuse:
                self.confuse = False
                if self.print_info:
                    print(f'    {self.name}受混乱影响将攻击自己')
                winner = self.be_hit(self.simple_atk())
            else:
                winner = p2.be_hit(self.simple_atk())
            if winner:
                return winner
        # 解除p2闪避状态
        if p2.evade_state:
            p2.evade_state = False
        return 0

    def be_hit(self, hit_info_dict_list):
        """
        角色被攻击
        """
        # ##### 计算总伤害
        # 没有伤害则返回0
        if hit_info_dict_list is None:
            return 0
        # 返回整型即获胜者编号
        if isinstance(hit_info_dict_list, int):
            return hit_info_dict_list
        # 是否闪避
        if self.evade:
            if not self.evade_state:
                if random.randint(1, 100) <= self.evade:
                    self.evade_state = True
                    if self.print_info:
                        print(f'    {self.name}进入闪避状态')
        # 正常计算伤害
        sum_hurt = 0
        if not self.evade_state:
            if len(hit_info_dict_list):
                for hit_info_dict in hit_info_dict_list:
                    if self.shield:
                        if hit_info_dict['can_block']:
                            hurt = int(hit_info_dict['hit_value'] * hit_info_dict['multi']) - self.DEF
                        else:
                            hurt = int(hit_info_dict['hit_value'] * hit_info_dict['multi'])
                        cur_hurt = max(0, hurt - self.shield)
                        self.shield = max(0, self.shield - hurt)
                        if self.shield:
                            if self.print_info:
                                print(f'    {self.name}护盾余量{self.shield}')
                        else:
                            shield_hurt = int(self.DEF * random.randint(200, 400) / 100)
                            shield_hurt_de_HP = max(0, shield_hurt - hit_info_dict['p1'].DEF)
                            if self.print_info:
                                print(f'    {self.name}护盾破碎, {hit_info_dict["p1"].name}受反伤 (HP: {hit_info_dict["p1"].HP} -> {hit_info_dict["p1"].HP-shield_hurt_de_HP})')
                            hit_info_dict['p1'].HP -= shield_hurt_de_HP
                            if hit_info_dict['p1'].HP <= 0:
                                return self.player_number
                    elif hit_info_dict['can_block']:
                        cur_hurt = max(
                            0, (int(hit_info_dict['hit_value'] * hit_info_dict['multi']) - self.DEF))
                    else:
                        cur_hurt = int(hit_info_dict['hit_value'] * hit_info_dict['multi'])
                    sum_hurt += cur_hurt

                    if hit_info_dict['hemophagia']:
                        HP_after_hemophagia = min(100, hit_info_dict['p1'].HP + cur_hurt)
                        if self.print_info:
                            print(f'    {hit_info_dict["p1"].name}恢复{cur_hurt}点生命值 (HP: {hit_info_dict["p1"].HP} -> {HP_after_hemophagia}')
                        hit_info_dict['p1'].HP = HP_after_hemophagia
            else:
                return 0
        # ##### 造成伤害
        sum_hurt = int(sum_hurt * (1 - self.de_hurt))
        if self.print_info:
            print(f'    {self.name}受{sum_hurt}点伤害 (HP: {self.HP} -> {self.HP-sum_hurt})')
        self.HP -= sum_hurt
        if self.HP <= 0:
            return hit_info_dict['p1'].player_number
        else:
            return 0

    def run_talent(self, p2):
        if self.talent_additional_judgment(p2):
            if random.randint(1, 100) <= self.talent_probability:
                if self.print_info:
                    self.print_attack(0)
                return self.talent(p2)

    def run_skill(self, p2):
        if self.skill_additional_judgment(p2):
            if self.print_info:
                self.print_attack(2)
            return self.skill(p2)

    def talent_additional_judgment(self, p2):
        return True

    def skill_additional_judgment(self, p2):
        return True

    def simple_atk(self):
        """
        普攻
        :return: hit_info_dict
        """
        if self.print_info:
            self.print_attack(1)
        return [self.hit_info(hit_value=self.ATK, multi=self.multi)]

    def talent(self, p2):
        """
        被动技能/天赋
        """
        pass

    def skill(self, p2):
        """
        主动技能
        """
        pass

    def hit_info(self, **kwargs):
        """
        攻击信息
        :param kwargs: hit_value, multi, can_block, hemophagia
        hit_value 单次伤害
        multi 倍率
        can_block 能否被防御力抵消一部分
        hemophagia 回复实际伤害血量
        split 撕裂伤害, 为真实伤害
        """
        d = dict(p1=self, hit_value=1, multi=1, can_block=True, hemophagia=False, split=False)
        d.update(**kwargs)
        return d


def view(p: People):
    print(f'{p.name.ljust(6, chr(12288))}HP{p.HP:3d}  ATK{p.ATK:3d}  DEF{p.DEF:3d}')  # 速{p.speed:3d}


def fight(P1, P2):
    """
    单次模拟
    """
    player1, player2 = P1(), P2()
    player2.player_number = 2

    counter = 1
    while min(player1.HP, player2.HP) > 0:
        if player2.speed > player1.speed:
            player1, player2 = player2, player1
        print('')
        print(f'----------ROUND {counter}----------')
        view(player1)
        view(player2)
        winner = player1.attack(player2, counter)
        if winner:
            break
        winner = player2.attack(player1, counter)
        if winner:
            break
        counter += 1
    print()

    player1, player2 = P1(), P2()
    player2.player_number = 2
    if winner == 1:
        print(f'{player1.name} WIN!')
    elif winner == 2:
        print(f'{player2.name} WIN!')
    else:
        print(winner)


def fight_single(P1, P2, show):
    """
    用于n次模拟的单次模拟
    """
    player1, player2 = P1(), P2()
    player2.player_number = 2
    if not show:
        player1.print_info, player2.print_info = False, False

    counter = 1
    while min(player1.HP, player2.HP) > 0:
        if player2.speed > player1.speed:
            player1, player2 = player2, player1
        winner = player1.attack(player2, counter)
        if winner:
            break
        winner = player2.attack(player1, counter)
        if winner:
            break
        counter += 1
    return winner


def fights(P1, P2, n: int, show=False):
    """
    n次模拟
    """
    win_list = []
    for i in range(n):
        if show:
            print(f'{i + 1}/{n}')
        win_list.append(fight_single(P1, P2, show))
    p1_win = win_list.count(1)
    p2_win = win_list.count(2)

    player1, player2 = P1(), P2()
    player2.player_number = 2
    print(f'p1 {player1.name}\t{p1_win}\np2 {player2.name}\t{p2_win}')
    print(f'{player1.name}胜率：{p1_win / n}')
    print(f'{player2.name}胜率：{p2_win / n}')
    return win_list
