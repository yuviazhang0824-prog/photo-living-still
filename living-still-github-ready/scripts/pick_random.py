#!/usr/bin/env python3
"""真随机抽签：从候选动画元素中抽一个。

用法: python3 pick_random.py 火苗 蒸汽 窗帘 挂钟摆锤
输出: 抽中的元素（打印到 stdout）
"""
import random
import sys


def main() -> None:
    candidates = [a for a in sys.argv[1:] if a.strip()]
    if len(candidates) < 2:
        sys.exit("至少传 2 个候选元素，例: pick_random.py 火苗 蒸汽 窗帘")
    # SystemRandom 走操作系统熵源，避免模型自己"挑顺眼的"
    pick = random.SystemRandom().choice(candidates)
    print(pick)


if __name__ == "__main__":
    main()
