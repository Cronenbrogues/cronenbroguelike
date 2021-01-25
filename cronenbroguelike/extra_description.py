from bisect import bisect_left

# way to put this stuff into a namespace? just do a class? then don't have to import tons of things

def get_interval(value, intervals):
    if not intervals:
        return None
    keys = sorted([key for (key, _) in intervals])
    idx = min(bisect_left(keys, value), len(intervals)-1)
    return intervals[idx][1]

# (sanity, description) pairs: should use description for player sanity <= description sanity (save for last one, which fills in the rest)
gary_jokes = [
    # Dad jokes
    (10, ['"So I tried to patent a pencil with two erasers for poor spellers like me, but I was told it was \'pointless\'!"',
          '"Have you heard of Murphy\'s Law? well, have you heard of Cole\'s Law?"\n'
          'Gary doesn\'t wait for you to respond.\n"It\'s sliced cabbage!"',
          '"Do you think glass coffins will be a success?"\nGary doesn\'t wait for you to respond.\n"Remains to be seen!"',
          '"Why do you never see elephants hiding in trees?"\nGary doesn\'t wait for you to respond.\n"Because they\'re so good at it!"',
          '"Did you hear about the restaurant on the moon?"\nGary doesn\'t wait for you to respond.\n"Great food, but no atmosphere!"',
          '"Two goldfish are in a tank. One says to the other - \'Do you know how to drive this thing?\'"',
    ]),

    # Dark
    (20, ['"What’s the last thing to go through a fly’s head as it hits the windshield of a car going 70 mph? Its ass!"',
          '"Why was the guitar teacher arrested? For fingering a minor!"',
          '"Why does Dr. Pepper come in a bottle? Because his wife died!"',
          '"What’s the difference between your wife and your job? After five years, your job will still suck!"',
          '"If you donate a kidney, everybody loves you and you’re a total hero. But try donating five kidneys – people start yelling, police gets called... Sheesh!"', ]),

    # Nonsensical
    (25, ['"Ha! Hahaha! Ha! Ha ha ha ha ha ha   ha     ha          ha..." Gary trails off.',
          'Gary goes through the facial and body movements of telling a great joke, but only a guttural moaning escapes his lips.',
          'Gary doubles over with coarse laughter. Actually, it sounds like he\'s in a good deal of pain.',]),

    # Ending
    (29, ['Gary is silent, his eyes pleading, his mouth fixed in a gruesome rictus.', 'Black foam drips slowly from Gary\'s mouth.']),
    (30, ['YOU MUST END IT!', 'FLENSE MY CURSED FLESH, TRAVELER', 'CONSUME ME']),
]

gary_descriptions = [
    (0, "Your co-worker Gary vibrates garrulously in the corner."),
    (5, "Gary vibrates garrulously in the corner."),
    (10, "Gary vibrates in the corner."),
    (20, "Gary vibrates ominously in the corner."),
    (30, "The liminal blur of Gary hums ominously in the corner."),
]

coffee_machine_descriptions = [
    (5, "A coffee machine gurgles pleasantly on the counter."),
    (10, "The coffee machine gurgles angrily on the counter, which seems even wetter than usual."),
    (15, "Sleep! Work! Sleep, Work! You've done neither! Strange thoughts come unbidden to your head. Is the coffee machine glaring at you? Time for another cup!"),
    (20, "From just beyond the edge of your vision, you swear you see gleaming, arachnid legs delicately manipulating a strange bundle. You turn to look, but it's just the coffee machine! You really need to get more sleep! Time for another cup."),
    (29, "Something strange is on the counter. You try not to look at it."),
    (30, "A wicked machine leers hungrily from its perch on the fresh corpse of a co-worker. You have interrupted its feeding. From its fangs drips a putrid, steaming ichor."),
]

# coffee_machine_use = [
#     (10, ''),
# ]

coffee_descriptions = [
    (10, 'A nice, warm cup of shitty black coffee'),
    (20, 'Good ol\' coffee. Nothing weird about that!'),
    (29, 'Coffee. There\'s something a bit off about it...'),
    (30, 'Steaming ichor'),
]

breakroom_descriptions = [
    (10, 'You are in the drab company breakroom. One of the fluorescent lights is flickering a bit.'),
    (20, 'You are in the break room. There\'s a strange, faint veining on the walls now...'),
    (30, 'You seem to be in some kind of bio-mechanical womb. A dense convergence of fleshy, pulsing cables wrap the walls, terminating at where the coffee machine once was.'),
]

your_desk_descriptions = [
    (10, 'Your boring old desk. Someday you\'ll clean up the coffee stains.'),
    (20, 'Your boring old desk. You\'re pretty sure one of the coffee stains just blinked at you.'),
    (30, 'There is a strange organic growth where your desk once was. It seems to be breathing.'),
]

office_computer_descriptions = [
    (10, 'Your computer hums gently in front of you.'),
    (15, 'Your computer hums gently in front of you. It looks a bit... sharper than usual?'),
    (20, 'Your computer hums gently in front of you. Well, not a hum, really - more of a gurgling growl.'),
    (30, 'A fleshy tentacle undulates gently where your computer once was, a single wicked claw emerging at the level of your forehead.'),
]

meeting_room_descriptions = [
    (10, 'You are in the meeting room. It smells like sweat and coffee.'),
    (20, 'You are in the meeting room. It smells like blood, sweat, and tears. Must be some weird motivational scent?'),
    (25, 'You are in the meeting room. It smells of shit and putrid flesh.'),
    (30, 'You think this must have been the meeting room. There\'s a heap of twisted bodies, viscous with some kind of pale ooze, writhing orgiastically on the floor.'),
]

copy_room_descriptions = [
    (10, 'You are in the copy room. The copier is broken.'),
    (20, 'You are in the copy room. What\'s that smell?'),
    (30, 'You think this was once the copy room. There is a bin full of bodies. They all seem to be Gary.'),
]
