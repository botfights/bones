# p_human.py

import bones


def get_play(whoami, my_hand, legal_plays, table, tile_counts, scores):
    print('=' * 50)
    rows = bones.render_table_simple(table)
    for i in rows:
        print(bones.serialize_hand(i))
    print('-' * 50)
    print('You are %s. Tile counts for NESW are: %d, %d, %d, %d. There are %d tile(s) in the boneyard. The score is %d to %d, NS to EW.' % (['NORTH', 'EAST', 'SOUTH', 'WEST'][whoami], tile_counts[0], tile_counts[1], tile_counts[2], tile_counts[3], tile_counts[4], scores[0], scores[1]))
    print('Your tiles: %s' % bones.serialize_hand(my_hand))
    for i in range(len(legal_plays)):
        p = legal_plays[i]
        if None == p[1]:
            print('    %s)  %d%d' % (chr(ord('a') + i), p[0][0], p[0][1]))
        else:
            print('    %s)  %d%d on the %d%d' % (chr(ord('a') + i), p[0][0], p[0][1], p[1][0], p[1][1]))
    while 1:
        try:
            s = raw_input('Your play: ')
        except:
            s = input('Your play: ')
        s = s.lower()
        play = -1
        try:
            play = ord(s[0]) - ord('a')
        except:
            pass
        if play >= 0 and play < len(legal_plays):
            return legal_plays[play]

