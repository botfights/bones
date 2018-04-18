# main.py -- harness for playing dominoes


import random, sys, getopt, imp, logging, time

import bones


HELP = '''\
main.py -- botfights harness for dominoes

to play against the computer

    $ python main.py game p_human p_computer

to play a game between two bots

    $ python main.py game p_bot1 p_bot2

to play a round robin tournament of 100 games between each bot

    $ python main.py tournament 100 p_bot1 p_bot2 p_bot3

'''

from signal import (signal,
                    SIGPIPE,
                    SIG_DFL)

signal(SIGPIPE, SIG_DFL)


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
        logging.info('playing round #%d of %d ...' % (i + 1, n))
        for player_a in players.keys():
            for player_b in players.keys():
                if player_a >= player_b:
                    continue
                seats = (player_a, player_b)
                if 0 == (i % 2):
                    seats = (player_b, player_a)
                logging.info('playing game between %s and %s ...' % (names[seats[0]], names[seats[1]]))
                result = bones.play_game(options, players[seats[0]][0], players[seats[1]][0], players[seats[0]][1], players[seats[1]][1])
                logging.info('%s beat %s.' % (names[seats[result]], names[seats[1 - result]]))
                wins[seats[result]] += 1
                logging.info('BOTFIGHTS\t%s' % ('\t'.join(map(lambda x: '%s:%d' % (names[x], wins[x]), wins.keys()))))
    a = []
    for i in wins.items():
        a.append((names[i[0]], i[1]))
    a.sort(key = lambda x: x[1], reverse = True)
    return a


def main(argv):
    if 0 == len(argv):
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
        options = {}
        play_games(options, player_names, seed, n)

    else :
        logging.error('i don\'t know how to "%s". look at the source' % c)
        print HELP
        sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
