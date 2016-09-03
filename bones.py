# bones.py

# see README.md for more dox

import os, random, sys, itertools, logging, imp, time, itertools, getopt

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

g_catch_exceptions = False


NORTH   = 1
EAST    = 2
SOUTH   = 3
WEST    = 4

NORTHSOUTH  = 1
EASTWEST    = 0

# 64 44 42 43 61 14 45:44

def new_tiles():
    a = []
    for i in range(7):
        for j in range(i + 1):
            a.append((i, j))
    return a


def wash_tiles(tiles):
    random.shuffle(tiles)
    return tiles


def serialize_hand(hand):
    s = []
    for a in hand:
        s.append('%d%d' % (a[0], a[1]))
    return ' '.join(s)


def serialize_table(table):
    s = []
    for i in table:
        a, b = i
        if b == None:
            s.append('%d%d' % (a[0], a[1]))
        else:
            s.append('%d%d:%d%d' % (a[0], a[1], b[0], b[1]))
    return ' '.join(s)


def deserialize_hand(s):
    hand = []
    for i in s.split():
        a = (int(i[0]), int(i[1]))
        if a[0] < a[1]:
            a = (a[1], a[0])
        hand.append(a)
    return hand


def deserialize_table(s):
    ends = {}
    table = []
    for i in s.split():
        j = i.split(':')
        a = (int(j[0][0]), int(j[0][1]))
        if a[0] < a[1]:
            a = (a[1], a[0])
        if 2 == len(j):
            b = (int(j[1][0]), int(j[1][1]))
            if b[0] < b[1]:
                b = (b[1], b[0])
        if 0 == len(table):
            b = None
        else:
            for end, playable in ends.items():
                if (playable & 1) and end[0] in (a[0], a[1]):
                    b = end
                    break
                if (playable & 2) and end[1] in (a[0], a[1]):
                    b = end
                    break
                if (playable & 4) and end[0] in (a[0], a[1]):
                    b = end
                    break
                if (playable & 8) and end[0] in (a[0], a[1]):
                    b = end
                    break
            if None == b:
                raise Exception('invalid play in deserializing "%s"' % s)

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
            ends[b] &= 2
            ends[a] = 2

        # high on low
        #
        elif a[0] == b[1]:
            ends[b] &= 1
            ends[a] = 2

        # low on high
        #
        elif a[1] == b[0]:
            ends[b] &= 2
            ends[a] = 2

        # low on low
        #
        elif a[1] == b[1]:
            ends[b] &= 1
            ends[a] = 1

        table.append((a, b))
    return table


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
            ends[b] &= 2
            ends[a] = 2

        # high on low
        #
        elif a[0] == b[1]:
            ends[b] &= 1
            ends[a] = 2

        # low on high
        #
        elif a[1] == b[0]:
            ends[b] &= 2
            ends[a] = 2

        # low on low
        #
        elif a[1] == b[1]:
            ends[b] &= 1
            ends[a] = 1

    return ends


def get_pip_ends(ends):
    pip_ends = [{}, {}, {}, {}, {}, {}, {}]
    for end, playable in ends.items():
        if 0 == playable:
            continue
        if end[0] == end[1]:
            pip_ends[end[0]][end] = playable
        else:
            if 1 == playable:
                pip_ends[end[0]][end] = playable
            if 2 == playable:
                pip_ends[end[1]][end] = playable
    return pip_ends


def get_plays(ends, pip_ends, hand):
    plays = []
    if 0 == len(ends):
        for i in hand:
            plays.append((i, None))
    else:
        for i in hand:
            for end, playable in pip_ends[i[0]].items():
                plays.append((i, end))
            if i[0] != i[1]:
                for end, playable in pip_ends[i[1]].items():
                    plays.append((i, end))
    return plays


def get_count(ends):
    count = 0
    for end, playable in ends.items():
        if end[0] == end[1]:
            if playable & 3:
                count += 2 * end[0]
        else:
            if playable & 1:
                count += end[0]
            if playable & 2:
                count += end[1]
    return count


def main(argv):

    c = argv[0]

    if 0:
        pass

    elif 'new_tiles' == c:
        tiles = new_tiles()
        print tiles

    elif 'wash_tiles' == c:
        tiles = new_tiles()
        wash_tiles(tiles)
        print tiles

    elif 'count_tiles' == c:
        tiles = new_tiles()
        print len(tiles)

    elif 'new_hand' == c:
        tiles = new_tiles()
        wash_tiles(tiles)
        hand = tiles[:5]
        hand.sort(reverse=True)
        print serialize_hand(hand)

    elif 'reserialize_hand' == c:
        hand = deserialize_hand(argv[1])
        print serialize_hand(hand)

    elif 'new_hands' == c:
        for i in range(argv[1]):
            tiles = new_tiles()
            wash_tiles(tiles)
            hand = tiles[:5]
            hand.sort(reverse=True)
            print hand

    elif 'deserialize' == c:
        table = deserialize_table(argv[1])
        print table

    elif 'reserialize' == c:
        table = deserialize_table(argv[1])
        s = serialize_table(table)
        print s

    elif 'get_ends' == c:
        table = deserialize_table(argv[1])
        ends = get_ends(table)
        print ends

    elif 'get_count' == c:
        table = deserialize_table(argv[1])
        ends = get_ends(table)
        count = get_count(ends)
        print count

    elif 'get_pip_ends' == c:
        table = deserialize_table(argv[1])
        ends = get_ends(table)
        pip_ends = get_pip_ends(ends)
        print pip_ends

    elif 'get_plays' == c:
        hand = deserialize_hand(argv[1])
        table = deserialize_table(argv[2])
        ends = get_ends(table)
        pip_ends = get_pip_ends(ends)
        plays = get_plays(ends, pip_ends, hand)
        print plays

    else:
        print 'i don\'t know how to "%s".' % command
        usage()
        sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
