# p_computer.py -- play random tile from list of tiles that score the most points

import random


def get_ends(table):
    ends = {}
    for i in table:
        a, b = i

        # first play?
        #
        if None == b:
            ends[a] = 3

        # play on a double?
        #
        elif b[0] == b[1]:
            ends[b] = {3:2, 2:8, 8:4, 4:0}[ends[b]]
            if a[0] == b[0]:
                ends[a] = 2
            else:
                ends[a] = 1

        # high on high
        #
        elif a[0] == b[0]:
            ends[b] &= 14
            ends[a] = 2

        # high on low
        #
        elif a[0] == b[1]:
            ends[b] &= 13
            ends[a] = 2

        # low on high
        #
        elif a[1] == b[0]:
            ends[b] &= 14
            ends[a] = 1

        # low on low
        #
        elif a[1] == b[1]:
            ends[b] &= 13
            ends[a] = 1

    for i, j in ends.items():
        if 0 == j:
            del ends[i]

    return ends


def get_count(ends):
    count = 0
    for end, playable in ends.items():
        if end[0] == end[1]:
            if playable & 3:
                count += end[0] + end[1]
        else:
            if playable & 1:
                count += end[0]
            if playable & 2:
                count += end[1]
    return count


def get_play(whoami, my_hand, legal_plays, table, tile_counts, scores):

    # get the playable ends
    #
    ends = get_ends(table)

    # get the count
    #
    count = get_count(ends)

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

