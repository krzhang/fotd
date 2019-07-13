import random

INSULTS_PAIRS = [
("You fight like a Dairy Farmer!","How appropriate! You fight like a cow!"),
("I've spoken with apes more polite than you!","I'm glad to hear you attended your family reunion!"),
("Soon you'll be wearing my sword like a shish kebab!","First you better stop waving it about like a feather duster."),
("People fall at my feet when they see me coming!","Even BEFORE they smell your breath?"),
("I'm not going to take your insolence sitting down!","Your hemorroids are flaring up again eh?"),
("I once owned a dog that was smarter than you.","He must have taught you everything you know."),
("Nobody's ever drawn blood from me and nobody ever will.","You run THAT fast?"),
("Have you stopped wearing diapers yet?","Why? Did you want to borrow one?"),
("There are no words for how disgusting you are.","Yes there are. You just never learned them."),
("You make me want to puke.","You make me think somebody already did."),
("My handkerchief will wipe up your blood!","So you got that job as janitor, after all."),
("I got this scar on my face during a mighty struggle!","I hope now you've learned to stop picking your nose."),
("You're no match for my brains, you poor fool.","I'd be in real trouble if you ever used them."),
("You have the manners of a beggar.","I wanted to make sure you'd feel comfortable with me."),
("Now I know what filth and stupidity really are.","I'm glad to hear you attended your family reunion."),
("Every word you say to me is stupid.","I wanted to make sure you'd feel comfortable with me."),
("My wisest enemies run away at the first sight of me!","Even BEFORE they smell your breath?"),
("Only once have I met such a coward!","He must have taught you everything you know."),
("There are no clever moves that can help you now.","Yes there are. You just never learned them."),
("Every enemy I've met I've annihilated!","With your breath, I'm sure they all suffocated."),
  ("You're the ugliest monster ever created!","If you don't count all the ones you've dated."),
  ("I don't know whether you'll die upon the gallows, or of syphilis.", "That will depend on whether I embrace your principles, or your mistress.")]

INSULTS_SINGLE = [
  "You know nothing, {ctarget}.",
  
]

INSULTS_ADJ = [
  "rambunctious",
  "spoony",
  "incessant",
  "blistering",
  "preposterous",
  "cowardly",
  "idiotic",
  "neophyte",
  "sophmoric",
  "soporific",
  "wack",
  "dopey",
  "soporific",
]

INSULTS_NOUNS = [
  "trogolodyte",
  "barnacles",
  "elephant",
  "cow",
  "cantaloupe",
  "oaf",
  "buffoon",
  "sore",
  "deadweight",
  "wight",
  "zombie",
  "furniture",
]

def random_diss():
  return "{} {}".format(random.choice(INSULTS_ADJ), random.choice(INSULTS_NOUNS))
