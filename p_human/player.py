# p_human.py


def serialize_hand(hand):
    s = []
    for a in hand:
        s.append('%d%d' % (a[0], a[1]))
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


def get_play(whoami, my_hand, legal_plays, table, tile_counts, scores):
    print('=' * 50)
    rows = render_table_simple(table)
    for i in rows:
        print(serialize_hand(i))
    print('-' * 50)
    print('You are %s. Tile counts for NESW are: %d, %d, %d, %d. There are %d tile(s) in the boneyard. The score is %d to %d, NS to EW.' % (['NORTH', 'EAST', 'SOUTH', 'WEST'][whoami], tile_counts[0], tile_counts[1], tile_counts[2], tile_counts[3], tile_counts[4], scores[0], scores[1]))
    print('Your tiles: %s' % serialize_hand(my_hand))
    for i in range(len(legal_plays)):
        p = legal_plays[i]
        if None == p[1]:
            print('    %s)  %d%d' % (chr(ord('A') + i), p[0][0], p[0][1]))
        else:
            print('    %s)  %d%d on the %d%d' % (chr(ord('A') + i), p[0][0], p[0][1], p[1][0], p[1][1]))
    print('Your play:')
    s = raw_input()
    s = s.upper()
    while 1:
        play = -1
        try:
            play = ord(s[0]) - ord('A')
        except:
            pass
        if play >= 0 and play < len(legal_plays):
            return legal_plays[play]

