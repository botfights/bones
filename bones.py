# bones.py

# see README.md for more dox

import random, sys, getopt


PLAY_TO = 1


def player_random(whoami, legal_plays, table, tile_counts, scores):
    return random.choice(legal_plays)


def get_play(g, player_idx, legal_plays):
    tile_counts = map(lambda x: len(g.hands[x]), range(4))
    play = g.players[player_idx](player_idx, legal_plays, g.table, tile_counts, g.scores)
    return play


class Game:
    pass


def new_game(options, player_north, player_east, player_south, player_west):
    g = Game()
    g.options = options
    g.players = [player_north, player_east, player_south, player_east]
    g.scores = [0, 0]
    return g


def dump_game(g):
    print 'score: NS: %d EW: %d' % (g.scores[0], g.scores[1])
    print 'boneyard: %s' % str(g.boneyard)
    print 'N: %s' % str(g.hands[0])
    print 'S: %s' % str(g.hands[1])
    print 'E: %s' % str(g.hands[2])
    print 'W: %s' % str(g.hands[3])
    print 'table: %s' % str(g.table)


def new_hand(g):
    g.tiles = wash_tiles(new_tiles())
    g.hands = [g.tiles[:5], g.tiles[5:10], g.tiles[10:15], g.tiles[15:20]]
    g.boneyard = g.tiles[20:]
    g.table = []
    g.whose_set = 0
    g.successive_knocks = 0
    return g


def play_game(g):
    while 1:
        if g.scores[0] >= PLAY_TO:
            return 0
        if g.scores[1] >= PLAY_TO:
            return 1
        new_hand(g)
        play_hand(g)


def play_move(g):

    ends = get_ends(g.table)
    pip_ends = get_pip_ends(ends)
    legal_plays = get_plays(ends, pip_ends, g.hands[g.whose_move])
    if 0 == len(legal_plays):
        while 2 < len(g.boneyard):
            g.hands[g.whose_move].append(g.boneyard.pop())
            legal_plays = get_plays(ends, pip_ends, g.hands[g.whose_move])
        if 0 == len(legal_plays):
            g.successive_knocks += 1
            if 4 == g.successive_knocks:
                north_points = sum(map(lambda x: x[0] + x[1], g.hands[0]))
                east_points = sum(map(lambda x: x[0] + x[1], g.hands[1]))
                south_points = sum(map(lambda x: x[0] + x[1], g.hands[2]))
                west_points = sum(map(lambda x: x[0] + x[1], g.hands[3]))
                if (north_points < east_points and north_points < west_points) \
                   (south_points < east_points and south_points < west_points):
                    g.score[0] += east_points + west_points
                else:
                    g.score[1] += north_points + south_points
                return True
        return False

    play = get_play(g, g.whose_move, legal_plays)
    if play not in legal_plays:
        play = legal_plays.values()[0]

    g.successive_knocks = 0

    g.table.append(play)
    for i in range(len(g.hands[g.whose_move])):
        if g.hands[g.whose_move][i] == play[0]:
            g.hands[g.whose_move] = g.hands[g.whose_move][:i] + g.hands[g.whose_move][i+1:]
            break
    count = get_count(get_ends(g.table))
    if 0 == count % 5:
        g.scores[g.whose_move % 2] += (count // 5)
    if 0 == len(g.hands[g.whose_move]):
        if g.whose_move in (0, 2):
            player_points = (1, 3)
            scorer = 0
        else:
            player_points = (0, 2)
            scorer = 1
        points = sum(map(lambda x: x[0] + x[1], g.hands[player_points[0]])) + \
                 sum(map(lambda x: x[0] + x[1], g.hands[player_points[1]]))
        g.scores[scorer] += points
        return True
    return False


def play_hand(g):
    g.whose_move = g.whose_set
    g.whose_set += 1
    if 4 == g.whose_set:
        g.whose_set = 0
    while 1:
        dump_game(g)
        hand_over = play_move(g)
        if hand_over:
            break
        g.whose_move += 1
        if 4 == g.whose_move:
            g.whose_move = 0


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
            s.append('%d%dxx' % (a[0], a[1]))
        else:
            s.append('%d%d%d%d' % (a[0], a[1], b[0], b[1]))
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
        a = (int(i[0]), int(i[1]))
        if a[0] < a[1]:
            a = (a[1], a[0])
        b = None
        if 0 != len(table):
            b = (int(i[2]), int(i[3]))
            if b[0] < b[1]:
                b = (b[1], b[0])
            legal = False
            for end, playable in ends.items():
                if (playable & 1) and end[0] in (a[0], a[1]):
                    b = end
                    legal = True
                    break
                if (playable & 2) and end[1] in (a[0], a[1]):
                    b = end
                    legal = True
                    break
                if (playable & 4) and end[0] in (a[0], a[1]):
                    b = end
                    legal = True
                    break
                if (playable & 8) and end[0] in (a[0], a[1]):
                    b = end
                    legal = True
                    break
            if not legal:
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


def render(table):
    tiles = {} # center_x, center_y, direction, count_neighbors
    x_dir = [0, 1, 0, -1]
    y_dir = [-1, 0, 1, 0]
    for i in table:
        a, b = i
        if 0 == len(tiles):
            tiles[a] = [0, 0, EAST, 0]
        else:
            b_loc = tiles[b]
            if b[0] == b[1]:    # single on double
                pass
            elif a[0] == a[1]:  # double on single
                tiles[a] = [b_loc[0] + (3 * x_dir[b_loc[2]]), b_loc[1] + (3 * y_dir[b_loc[2]]), (b_loc[2] + 1) % 4, 0]
            else:               # single on single
                tiles[a] = [b_loc[0] + (4 * x_dir[b_loc[2]]), b_loc[1] + (4 * y_dir[b_loc[2]]), b_loc[2], 0]
            tiles[b][3] += 1
    return tiles


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
            if 1 & playable:
                pip_ends[end[0]][end] = playable
            if 2 & playable:
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
        for i in range(int(argv[1])):
            tiles = new_tiles()
            wash_tiles(tiles)
            hand = tiles[:5]
            hand.sort(reverse=True)
            print serialize_hand(hand)

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

    elif 'render' == c:
        table = deserialize_table(argv[1])
        tiles = render(table)
        print tiles

    elif 'get_plays' == c:
        hand = deserialize_hand(argv[1])
        table = deserialize_table(argv[2])
        ends = get_ends(table)
        pip_ends = get_pip_ends(ends)
        plays = get_plays(ends, pip_ends, hand)
        print plays


    elif 'test_game' == c:
        f = lambda w, l, t, c, s: player_random(w, l, t, c, s)
        g = new_game({}, f, f, f, f)
        play_game(g)

    else:
        print 'i don\'t know how to "%s".' % command
        usage()
        sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
