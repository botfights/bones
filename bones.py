# bones.py

# see README.md for more dox

import os, random, sys, itertools, logging, imp, time, itertools, getopt

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

g_catch_exceptions = False
g_max_time = MAX_TIME


class Player():
    pass


def call_player(player, args):
    global g_catch_exceptions
    result = None
    start = time.clock()
    try:
        result = player.play(*args)
    except KeyboardInterrupt:
        raise
    except:
        logging.warn('caught exception "%s" calling %s (%s)'
                     % (sys.exc_info()[1], player.player_id, player.playername))
        if not g_catch_exceptions:
            raise
    elapsed = time.clock() - start
    player.elapsed += elapsed
    player.calls += 1
    return result


def make_player(player_id, dirname):
    global g_catch_exceptions
    m = None
    try:
        name = 'bot'
        (f, filename, data) = imp.find_module(name, [dirname, ])
        m = imp.load_module(name, f, filename, data)
    except:
        logging.error('caught exception "%s" loading %s' % \
                      (sys.exc_info()[1], dirname))
        if not g_catch_exceptions:
            raise
    p = Player()
    p.player_id = player_id
    p.playername = dirname
    z = p.playername.rfind('/')
    if -1 != z:
        p.playername = p.playername[z + 1:]
    p.play = None
    if None == m or not hasattr(m, 'play'):
        logging.error('%s has no function "play"; ignoring ...' % dirname)
    else:
        p.play = getattr(m, 'play')
    p.elapsed = 0.0
    p.calls = 0
    p.get_play = lambda x: call_player(p, (p.player_id, p.hand, x))
    return p


def play_game(players):
    pass

def play_tournament(games, players):
    """
    play many games, return map of player_id to wins
    """
    for i in players:
        i.wins = 0
    for i in range(games):
        winner.wins += 1
        t = ''
        players.sort(key = lambda x : x.wins,reverse = True)
        for j in players:
            t += '%s:%d\t' % (j.playername, j.wins)
        logging.info('BOTFIGHT\t%d\t%d\t%s' % (i, games, t))


def usage():
    print('''\
bones! see: http://github.com/botfights/bones for dox

usage:

    $ python bones.py <command> [<option> ...] [<arg> ...]

commands:

    human [<opponent>]

                        play against the computer

    game <player1> <player2>

                        play a single game between players

    tournament [<player1>] [<player2>] ...

                        play a tournament between players
options:

    -h, --help                      show this help
    --seed=<s>                      set seed for random number generator
    --catch-exceptions=<off|on>     catch and log exceptions
    --num-games=<n>                 set number of games for tournament
    --log-level=<n>                 set log level (10 debug, 20 info, 40 error)
''')


def main(argv):
    if 1 > len(argv):
        usage()
        sys.exit()
    command = argv[0]
    try:
        opts, args = getopt.getopt(argv[1:], "h", [
                                                    "help",
                                                    "seed=",
                                                    "catch-exceptions=",
                                                    "num-games=",
                                                    "log-level=",
                                                    ])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(1)
    seed = time.time()
    num_games = 1000
    log_level = logging.DEBUG
    global g_catch_exceptions
    g_catch_exceptions = False
    for o, a in opts:
        if 0:
            pass
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("--seed", ):
            seed = a
        elif o in ("--num-games", ):
            num_games = int(a)
        elif o in ("--log-level", ):
            log_level = int(a)
        elif o in ("--catch-exceptions", ):
            g_catch_exceptions = 'off' != a
        else:
            raise Exception("unhandled option")
    random.seed(seed)

    if 0:
        pass

    elif 'human' == command:
        logging.basicConfig(level=logging.INFO, format='%(message)s',
                        stream=sys.stdout)
        players = [make_player('human', 'p_human'), ]
        if 0 == len(args):
            players.append(make_player('computer', 'p_computer'))
        else:
            players.append(make_player(args[0], args[0]))
        winner = play_game(players)
        sys.exit()

    elif 'game' == command:
        logging.basicConfig(level=log_level, format='%(message)s',
                        stream=sys.stdout)
        players = []
        for player_id, playername in enumerate(args):
            player = make_player(chr(ord('a') + player_id), playername)
            if None == player.play:
                continue
            players.append(player)
        winner = play_game(players)
        sys.exit()

    elif 'tournament' == command:
        logging.basicConfig(level=log_level, format='%(message)s',
                        stream=sys.stdout)
        players = []
        for player_id, playername in enumerate(args):
            player = make_player(chr(ord('a') + player_id), playername)
            if None == player.play:
                continue
            players.append(player)
        play_tournament(num_games, players)
        sys.exit()

    else:
        print 'i don\'t know how to "%s".' % command
        usage()
        sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
