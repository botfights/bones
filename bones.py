# bones.py

import random, sys, getopt, imp, logging, time


PLAY_TO = 61
HELP = '''\
bones.py -- botfights harness for dominoes

to play against the computer

    $ python bones.py human

to play a game between two bots

    $ python bones.py game bot1 bot2

to play a round robin tournament

    $ python bones.py tournament 1000 bot1 bot2 bot3 bot4 bot5
'''

from signal import (signal,
                    SIGPIPE,
                    SIG_DFL)

signal(SIGPIPE, SIG_DFL)


class Game:
    pass


def new_game(options, player_north, player_east, player_south, player_west):
    g = Game()
    g.options = options
    g.players = [player_north, player_east, player_south, player_east]
    g.scores = [0, 0]
    g.whose_set = 0
    return g


def get_play(g, player_idx, legal_plays):
    tile_counts = map(lambda x: len(g.hands[x]), range(4))
    play = g.players[player_idx](player_idx, legal_plays, g.table, tile_counts, g.scores)
    return play


def dump(s):
    sys.stdout.write(s)


def dump_game(g):
    dump('score: %d %d\n' % (g.scores[0], g.scores[1]))
    dump('plays: %s\n' % serialize_table(g.table))
    ends = get_ends(g.table)
    dump('ends: %s\n' % ' '.join(map(lambda x: '%d%d:%d' % (x[0][0], x[0][1], x[1]), ends.items())))
    dump('count: %d\n' % get_count(ends))
    dump('boneyard: %s\n' % serialize_hand(g.boneyard))
    dump('N: %s\n' % serialize_hand(g.hands[0]))
    dump('E: %s\n' % serialize_hand(g.hands[1]))
    dump('S: %s\n' % serialize_hand(g.hands[2]))
    dump('W: %s\n' % serialize_hand(g.hands[3]))
    dump('whose_move: %s\n' % "NESW"[g.whose_move])
    dump('%s\n' % ('-' * 40))
    rows = render_table_simple(g.table)
    for row in rows:
        dump(serialize_hand(row) + '\n')
    dump('%s\n' % ('=' * 40))


def new_hand(g):
    g.tiles = wash_tiles(new_tiles())
    g.hands = [g.tiles[:5], g.tiles[5:10], g.tiles[10:15], g.tiles[15:20]]
    g.boneyard = g.tiles[20:]
    g.boneyard.sort(reverse = True)
    g.hands[0].sort(reverse = True)
    g.hands[1].sort(reverse = True)
    g.hands[2].sort(reverse = True)
    g.hands[3].sort(reverse = True)
    g.table = []
    g.successive_knocks = 0
    g.whose_move = g.whose_set
    return g


def play_game(options, player_north, player_east, player_south, player_west):
    g = new_game(options, player_north, player_east, player_south, player_west)
    while 1:
        if g.scores[0] >= PLAY_TO:
            return 0
        if g.scores[1] >= PLAY_TO:
            return 1
        new_hand(g)
        play_hand(g)
        g.whose_set += 1
        if 4 == g.whose_set:
            g.whose_set = 0


def play_move(g):
    ends = get_ends(g.table)
    legal_plays = get_plays(ends, g.hands[g.whose_move])
    if 0 == len(legal_plays):
        while 2 <= len(g.boneyard):
            g.hands[g.whose_move].append(g.boneyard.pop())
            legal_plays = get_plays(ends, g.hands[g.whose_move])
        if 0 == len(legal_plays):
            g.successive_knocks += 1
            if 4 == g.successive_knocks:
                north_points = sum(map(lambda x: x[0] + x[1], g.hands[0]))
                east_points = sum(map(lambda x: x[0] + x[1], g.hands[1]))
                south_points = sum(map(lambda x: x[0] + x[1], g.hands[2]))
                west_points = sum(map(lambda x: x[0] + x[1], g.hands[3]))
                if (north_points < east_points and north_points < west_points) or \
                   (south_points < east_points and south_points < west_points):
                    g.scores[0] += east_points + west_points
                else:
                    g.scores[1] += north_points + south_points
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
    if (0 < count) and (0 == count % 5):
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
        g.scores[scorer] += points // 5
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
            dump_game(g)
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
            s.append('%d%d|xx' % (a[0], a[1]))
        else:
            s.append('%d%d|%d%d' % (a[0], a[1], b[0], b[1]))
    return ' '.join(s)


def render_table_simple(table):
    rows = []
    for play in table:
        if None == play[1]:
            rows.append([play[0], ])
            continue
        found = False

        for row in rows:
            if row[0][0] == play[1][0] and row[0][1] == play[1][1]:
                if play[0][1] == row[0][0]:
                    row.insert(0, (play[0][0], play[0][1]))
                else:
                    row.insert(0, (play[0][1], play[0][0]))
                found = True
                break
            if row[0][0] == play[1][1] and row[0][1] == play[1][0]:
                if play[0][1] == row[0][0]:
                    row.insert(0, (play[0][0], play[0][1]))
                else:
                    row.insert(0, (play[0][1], play[0][0]))
                found = True
                break
            if row[-1][0] == play[1][0] and row[-1][1] == play[1][1]:
                if play[0][0] == row[-1][1]:
                    row.append((play[0][0], play[0][1]))
                else:
                    row.append((play[0][1], play[0][0]))
                found = True
                break
            if row[-1][0] == play[1][1] and row[-1][1] == play[1][0]:
                if play[0][0] == row[-1][1]:
                    row.append((play[0][0], play[0][1]))
                else:
                    row.append((play[0][1], play[0][0]))
                found = True
                break
        if not found:
            if play[1][0] == play[1][1]:
                rows.append([])
                rows[-1].append((play[1][0], play[1][1]))
                if play[0][0] == play[1][0]:
                    rows[-1].append((play[0][0], play[0][1]))
                else:
                    rows[-1].append((play[0][1], play[0][0]))
            else:
                print rows
                raise Exception('didn\'t expect "%s"' % str(play))
    return rows


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


def get_plays(ends, hand):
    plays = []
    if 0 == len(ends):
        for i in hand:
            plays.append((i, None))
    else:

        # don't return duplicates (but only need to check singles)
        #
        singles = {}
        for i in hand:
            for end, playable in ends.items():

                # am i trying to play on a double?
                #
                if end[0] == end[1]:
                    if end[0] in (i[0], i[1]):
                        plays.append((i, end))
                    continue

                # check singles
                #
                if ((playable & 1) and (end[0] in (i[0], i[1]))) or \
                   ((playable & 2) and (end[1] in (i[0], i[1]))):
                    if (end, i[0], i[1]) not in singles:
                        plays.append((i, end))
                        singles[(end, i[0], i[1])] = 1
    return plays


def get_count(ends):
    count = 0
    for end, playable in ends.items():
        if playable & 1:
            count += end[0]
        if playable & 2:
            count += end[1]
    return count


def split_playername(playername):
    parts = playername.split(':')
    if 1 == len(parts):
        return (parts[0], parts[0], 'player', 'get_play')
    if 2 == len(parts):
        return (parts[0], parts[1], 'player', 'get_play')
    if 3 == len(parts):
        return (parts[0], parts[1], parts[2], 'get_play')
    if 4 == len(parts):
        return (parts[0], parts[1], parts[2], parts[3])
    raise Exception('i don\'t know how to parse "%s"' % playername)


def make_player(playername, path, modulename, attr):
    fp = pathname = description = m = None
    try:
        fp, pathname, description = imp.find_module(modulename, [path, ])
    except:
        logging.warn('caught exception "%s" finding module %s' % (sys.exc_info()[1], modulename))

    try:
        if fp:
            m = imp.load_module(playername, fp, pathname, description)
    except:
        logging.warn('caught exception "%s" importing %s' % (sys.exc_info()[1], playername))
    finally:
        if fp:
            fp.close()

    if None == m :
        return None

    f = getattr(m, attr)
    return f


def build_player(s):
    playername, path, modulename, attr = split_playername(s)
    p = make_player(playername, path, modulename, attr)
    return p


def play_games(options, player_names, seed, n):
    players = {}
    names = {}
    wins = {}
    for i in player_names:
        player_id = chr(ord('A') + len(players))
        names[player_id] = i
        logging.info('building player %s (%s) partner #1 ...' % (player_id, i))
        p1 = build_player(i)
        logging.info('building player %s (%s) partner #2 ...' % (player_id, i))
        p2 = build_player(i)
        players[player_id] = (p1, p2)
        wins[player_id] = 0
    for i in range(n):
        logging.info('playing round #%d of %d ...' % (i, n))
        for player_a in players.keys():
            for player_b in players.keys():
                if player_a == player_b:
                    continue
                result1 = play_game(options, players[player_a][0], players[player_b][0], players[player_a][1], players[player_b][1])
                result2 = play_game(options, players[player_b][0], players[player_a][0], players[player_b][1], players[player_a][1])
                if result1:
                    wins[player_a] += 1
                else:
                    wins[player_b] += 1
                if result1:
                    wins[player_b] += 1
                else:
                    wins[player_a] += 1
    a = []
    for i in wins.items():
        a.append((names[i[0]], i[1]))
    a.sort(key = lambda x: x[1], reverse = True)
    return a


def main(argv):
    if 1 == len(argv):
        print HELP
        sys.exit()

    c = argv[0]

    if 0:
        pass

    elif 'help' == c:
        print HELP
        sys.exit()

    elif 'game' == c:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s', stream=sys.stdout)
        options = {}
        player_names = argv[1:]
        seed = int(time.time() * 1000)
        play_games(options, player_names, seed, 1)

    elif 'tournament' == c:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-7s %(message)s', stream=sys.stdout)
        n = int(argv[1])
        player_names = argv[2:]
        seed = ''.join(argv)
        play_games(options, player_names, seed, 1)

    else :
        logging.error('i don\'t know how to "%s". look at the source' % c)
        print HELP
        sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
