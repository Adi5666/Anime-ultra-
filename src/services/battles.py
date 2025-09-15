\
import random

def calc_damage(atk, df):
    base = max(1, atk - int(df*0.6))
    variance = random.randint(-2, 3)
    return max(1, base + variance)

def turn_order(a_spd, b_spd):
    return ("A","B") if a_spd >= b_spd else ("B","A")
