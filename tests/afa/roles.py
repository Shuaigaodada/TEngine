import os
import env
from typing import *
import unicodedata as _ucdata
from TEngine.components import Resource

__all__ = ['Role']
ChEnRoleNames: Dict[str, str] = None

class Role:
    def __init__(self, name: str, cost: int) -> None:
        self.name = name
        self.cost = cost
        self.level = 1
        
        # role attrs
        self.maxHealthPoint = 1000
        self.healthPoint = 1000
        self.physicAttackPoint = 90
        self.magicAttackPoint = 20
        self.maxManaPoint = 100
        self.manaPoint = 10
        self.physicDefensePoint = 20
        self.magicDefensePoint = 10
        self.speed = 5
        self.criticalRate = 10
        self.criticalDamage = 150
        self.skillCanCritical = False
        
        self.score = 0
    
    def as_json( self ) -> Dict[ str, int | bool | str ]:
        """
        return {
            "name": self.name,
            "cost": self.cost,
            "level": self.level,
            "maxHealthPoint": self.maxHealthPoint,
            "healthPoint": self.healthPoint,
            "physicAttackPoint": self.physicAttackPoint,
            "magicAttackPoint": self.magicAttackPoint,
            "maxManaPoint": self.maxManaPoint,
            "manaPoint": self.manaPoint,
            "physicDefensePoint": self.physicDefensePoint,
            "magicDefensePoint": self.magicDefensePoint,
            "speed": self.speed,
            "criticalRate": self.criticalRate,
            "criticalDamage": self.criticalDamage,
            "skillCanCritical": self.skillCanCritical,
            "score": self.score
        }
        """
        return {
            "name": self.name,
            "cost": self.cost,
            "level": self.level,
            "maxHealthPoint": self.maxHealthPoint,
            "healthPoint": self.healthPoint,
            "physicAttackPoint": self.physicAttackPoint,
            "magicAttackPoint": self.magicAttackPoint,
            "maxManaPoint": self.maxManaPoint,
            "manaPoint": self.manaPoint,
            "physicDefensePoint": self.physicDefensePoint,
            "magicDefensePoint": self.magicDefensePoint,
            "speed": self.speed,
            "criticalRate": self.criticalRate,
            "criticalDamage": self.criticalDamage,
            "skillCanCritical": self.skillCanCritical,
            "score": self.score
        }
    
    def __eq__( self, other: "Role" ) -> bool:
        return self.name == other.name and self.level == other.level
    
    def initiveSkill(self) -> None:
        pass
    def passiveSkill(self) -> None:
        pass
    
    @property
    def sell_price(self) -> int:
        return self.cost * ( 3 ** ( self.level - 1 ) )
    @property
    def sell_count(self) -> List["Role"]:
        return [ type( self )() ] * ( 3 ** (self.level - 1) )

    @property
    def name_lenght(self) -> int:
        return sum(2 if _ucdata.east_asian_width(c) in 'FW' else 1 for c in self.name)
    
    def __str__(self) -> str:
        return self.name
    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def createOfName(roleName: "Role") -> 'Role':
        global ChEnRoleNames
        if ChEnRoleNames is None:
            basePath = os.path.dirname(__file__)
            srcPath = os.path.join(basePath, 'src')
            ChEnRoleNames = Resource(srcPath).load("TranslateNames.json").as_json()    
        
        try:
            name = roleName if type(roleName) is str else roleName.name
            name = ChEnRoleNames[name]
            roleInstance: Role = globals()[name]()
            return roleInstance
        except KeyError:
            raise ValueError(f'Role name "{name}" not found: dict_keys({list(ChEnRoleNames.keys())})')

class Kayn(Role):
    def __init__(self):
        super().__init__("凯隐", 5)
        self.maxHealthPoint = [900, 1620, 2916]
        self.maxManaPoint = [50]
        self.manaPoint = 0
        self.physicAttackPoint = [80, 144, 259]
        self.physicDefensePoint = [40]
        self.magicDefensePoint = [40]
        self.score = [100, 500, 3500]
    
    def initiveSkill(self) -> None:
        super().initiveSkill()
        skillDamage = [450, 600, 6666][self.level - 1] + self.magicAttackPoint
        return skillDamage

class Yorick(Role):
    def __init__(self) -> None:
        super().__init__("约里克", 5)
        self.maxHealthPoint = [1000, 1800, 3240]
        self.score = [150, 450, 3250]

class Ziggs(Role):
    def __init__(self) -> None:
        super().__init__("吉格斯", 5)
        self.score = [100, 500, 4000]

class Sona(Role):
    def __init__(self) -> None:
        super().__init__("娑娜", 5)
        self.score = [80, 600, 3600]

class Qiyana(Role):
    def __init__(self) -> None:
        super().__init__("奇亚娜", 5)
        self.score = [200, 800, 4850]

class Lucian(Role):
    def __init__(self) -> None:
        super().__init__("卢锡安", 5)
        self.score = [210, 600, 5000]

class Jhin(Role):
    def __init__(self) -> None:
        super().__init__("烬", 5)
        self.score = [100, 700, 3900]

class Illaoi(Role):
    def __init__(self) -> None:
        super().__init__("俄洛伊", 5)
        self.score = [300, 650, 4500]

class Zac(Role):
    def __init__(self) -> None:
        super().__init__("扎克", 4)
        self.score = [130, 350, 1260]

class Karthus(Role):
    def __init__(self) -> None:
        super().__init__("卡尔萨斯", 4)
        self.score = [100, 400, 1650]

class Caitlyn(Role):
    def __init__(self) -> None:
        super().__init__("凯特琳", 4)
        self.score = [160, 480, 1450]

class Tristana(Role):
    def __init__(self) -> None:
        super().__init__("崔斯特", 4)
        self.score = [140, 320, 1200]

class Zed(Role):
    def __init__(self) -> None:
        super().__init__("劫", 4)
        self.score = [80, 400, 1650]

class Blitzcrank(Role):
    def __init__(self) -> None:
        super().__init__("布里茨", 4)
        self.score = [160, 340, 1750]

class Fiddlesticks(Role):
    def __init__(self) -> None:
        super().__init__("佛耶戈", 4)
        self.score = [240, 490, 2100]

class Thresh(Role):
    def __init__(self) -> None:
        super().__init__("锤石", 4)
        self.score = [210, 440, 2055]

class Poppy(Role):
    def __init__(self) -> None:
        super().__init__("波比", 4)
        self.score = [200, 480, 1990]
    
class Ahri(Role):
    def __init__(self) -> None:
        super().__init__("阿狸", 4)
        self.score = [140, 490, 2050]

class Akali(Role):
    def __init__(self) -> None:
        super().__init__("阿卡丽", 4)
        self.score = [200, 470, 1900]

class Ezreal(Role):
    def __init__(self) -> None:
        super().__init__("伊泽瑞尔", 4)
        self.score = [190, 480, 2000]

class Yone(Role):
    def __init__(self) -> None:
        super().__init__("永恩", 3)
        self.score = [50, 240, 520]

class Veigar(Role):
    def __init__(self) -> None:
        super().__init__("薇古丝", 3)
        self.score = [100, 210, 620]

class Samira(Role):
    def __init__(self) -> None:
        super().__init__("莎弥拉", 3)
        self.score = [70, 230, 560]

class Sett(Role):
    def __init__(self) -> None:
        super().__init__("瑟提", 3)
        self.score = [80, 225, 525]

class Riven(Role): 
    def __init__(self) -> None:
        super().__init__("瑞文", 3)
        self.score = [120, 299, 625]

class Nidalee(Role):
    def __init__(self) -> None:
        super().__init__("妮蔻", 3)
        self.score = [80, 210, 452]

class Mordekaiser(Role):
    def __init__(self) -> None:
        super().__init__("莫德凯撒", 3)
        self.score = [50, 250, 520]

class Lulu(Role):
    def __init__(self) -> None:
        super().__init__("璐璐", 3)
        self.score = [110, 225, 721]

class Lux(Role):
    def __init__(self) -> None:
        super().__init__("拉克丝", 3)
        self.score = [100, 220, 699]

class MissFortune(Role):
    def __init__(self) -> None:
        super().__init__("厄运小姐", 3)
        self.score = [40, 220, 630]

class Urgot(Role):
    def __init__(self) -> None:
        super().__init__("厄加特", 3)
        self.score = [80, 350, 780]

class Ekko(Role):
    def __init__(self) -> None:
        super().__init__("艾克", 3)
        self.score = [90, 450, 645]

class Amumu(Role):
    def __init__(self) -> None:
        super().__init__("阿木木", 3)
        self.score = [150, 230, 600]

class Teemo(Role):
    def __init__(self) -> None:
        super().__init__("图奇", 2)
        self.score = [45, 80, 240]

class Senna(Role):
    def __init__(self) -> None:
        super().__init__("赛娜", 2)
        self.score = [55, 90, 340]

class Saraphine(Role):
    def __init__(self) -> None:
        super().__init__("萨勒芬妮", 2)
        self.score = [55, 95, 366]

class Pantheon(Role):
    def __init__(self) -> None:
        super().__init__("潘森", 2)
        self.score = [25, 80, 288]

class Gnar(Role):
    def __init__(self) -> None:
        super().__init__("纳尔", 2)
        self.score = [60, 70, 310]

class Kayle(Role):
    def __init__(self) -> None:
        super().__init__("凯尔", 2)
        self.score = [80, 120, 400]

class Katarina(Role):
    def __init__(self) -> None:
        super().__init__("卡特琳娜", 2)
        self.score = [60, 225, 325]

class Kassadin(Role):
    def __init__(self) -> None:
        super().__init__("卡莎", 2)
        self.score = [50, 70, 225]

class Gangplank(Role):
    def __init__(self) -> None:
        super().__init__("古拉加斯", 2)
        self.score = [60, 90, 230]

class Jax(Role):
    def __init__(self) -> None:
        super().__init__("贾克斯", 2)
        self.score = [75, 122, 333]

class Garen(Role):
    def __init__(self) -> None:
        super().__init__("盖伦", 2)
        self.score = [60, 90, 277]

class Aphelios(Role):
    def __init__(self) -> None:
        super().__init__("厄斐琉斯", 2)
        self.score = [100, 188, 333]

class Bard(Role):
    def __init__(self) -> None:
        super().__init__("巴德", 2)
        self.score = [90, 130, 299]

class Annie(Role):
    def __init__(self) -> None:
        super().__init__("安妮", 1)
        self.score = [15, 50, 120]

class Vi(Role):
    def __init__(self) -> None:
        super().__init__("蔚", 1)
        self.score = [10, 35, 70]

class Evelynn(Role):
    def __init__(self) -> None:
        super().__init__("伊芙琳", 1)
        self.score = [20, 44, 100]

class Nami(Role):
    def __init__(self) -> None:
        super().__init__("娜美", 1)
        self.score = [15, 35, 85]

class Taric(Role):
    def __init__(self) -> None:
        super().__init__("塔里克", 1)
        self.score = [10, 30, 99]

class Olaf(Role):
    def __init__(self) -> None:
        super().__init__("奥拉夫", 1)
        self.score = [15, 35, 111]

class TahmKench(Role):
    def __init__(self) -> None:
        super().__init__("塔姆", 1)
        self.score = [20, 40, 99]

class Yasuo(Role):
    def __init__(self) -> None:
        super().__init__("亚索", 1)
        self.score = [19, 40, 100]

class Lillia(Role):
    def __init__(self) -> None:
        super().__init__("莉莉娅", 1)
        self.score = [14, 48, 88]

class Corki(Role):
    def __init__(self) -> None:
        super().__init__("库奇", 1)
        self.score = [16, 42, 78]

class KSante(Role):
    def __init__(self) -> None:
        super().__init__("奎桑提", 1)
        self.score = [17, 53, 94]

class Kennen(Role):
    def __init__(self) -> None:
        super().__init__("凯南", 1)
        self.score = [13, 37, 82]

class Jinx(Role):
    def __init__(self) -> None:
        super().__init__("金克丝", 1)
        self.score = [18, 42, 102]