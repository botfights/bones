Bones
=====

Dominoes for bots.

To implement a bot, first get a copy of the game:

    $ git clone https://github.com/botfights/bones.git
    $ cd bones

To play against the computer:

    $ python bones.py human

To play a game between computer and random:

    $ python bones.py game p_computer p_random

Next, make a directory called `mybot` and copy over `p_computer/bot.py`,
edit the `play()` function, and play your bot against the computer:

    $ mkdir mybot
    $ cp p_computer/bot.py mybot/
    $ python bones.py game mybot p_computer

To play a tournament of 100 games:

    $ python bones.py tournament --num-games=100 mybot p_random p_computer

The winner of the tournament is the player who wins the most games,
in total. Note that `player_id` is consistent across games.

Once your ready, upload your bot to http://botfights.io to challenge other
coders. See http://botfights.io/how-to-play for more information.

Have fun!

colinmsaunders@gmail.com
