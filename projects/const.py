import typing as T
from Player import *
Star = "★"
OneStar = "★"
TwoStar = "★★"
ThreeStar = "★★★"

currentPlayerPile = "当前牌库: "
currentPlayerCards = "当前拥有角色: "
upgradeCard = "升级-4金币(f)"
refreshCard = "刷新-2金币(d)"
title = "金铲铲之战"

def getLevelInformation(player: Player, nxp: T.Dict[str, int]):
    return f"当前经验: {player.exp if nxp[str(player.level)] != -1 else '满级'}/{nxp[str(player.level)] if nxp[str(player.level)] != -1 else '满级'}, 当前等级: {player.level}"
def roundString(round: int, stage: int):
    return f"{round}-{stage}"

getAwardTip = " - 你有奖励未领取，按g领取奖励"