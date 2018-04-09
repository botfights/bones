# p_biggest.py -- play biggest tile

import random


def get_play(whoami, my_hand, legal_plays, table, tile_counts, scores):
    best = None
    for i in legal_plays:
        x = i[0][0] + i[0][1]
        if (None == best) or (best[0] < x):
            best = [x, [i, ]]
        elif best[0] == x:
            best[1].append(i)
    return random.choice(best[1])

