# p_computer.py -- play random tile from list of tiles that score the most points

import random

import bones


def get_play(whoami, my_hand, legal_plays, table, tile_counts, scores):

    # get the playable ends
    #
    ends = bones.get_ends(table)

    # get the count
    #
    count = bones.get_count(ends)

    # first play? if so, find tiles that score
    #
    best = None
    if 0 == len(ends):
        for i in legal_plays:
            x = i[0][0] + i[0][1]
            if 0 == (x % 5):
                x = 0
            else:
                x = x // 5
            if (None == best) or (best[0] < x):
                best = [x, [i, ]]
            elif best[0] == x:
                best[1].append(i)

    # otherwise, find tiles that scores the most
    #
    else:
        # TODO: check count, might have to deal with doubles differently
        raise NotImplementedError

    # pick a random play from contenders
    #
    return random.choice(best[1])

