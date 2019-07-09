# Fall of the Dragon: A roguelike-inspired strategy game

They say that which falls apart for a long time must reunite, and that which units for a long time must fall apart. The kingdom has fallen. You seek to reunite it.

* dynamically generated world and officers, with their own personalities and relationships
* strategic (fewer decisions, no micromanagement) design choice of both the strategy (kingdom-building) and tactical (battle) layers
* poker-like situation-dependent play, rewarding bluffing/outwitting opponents in a mechanically simple option space

## Inspirations

Fall of the Dragon is a nod to the officer-based strategy titles I enjoyed as a kid, mainly inspired by KOEI's Romance of the Three Kingdoms (ROTK) series. Compared to those games, FOTD removes the static world and complex systems in exchange for procedural generation and simple but tactical choices. Its other main inspirations are:
* Fighting games de-emphasizing complex combos and execution: Dive Kick, Nidhogg, Smash Brothers
* Games based on outwitting with simple systems: Poker, Yomi, Coup, Love Letter, Go
* Roguelikes with small decision spaces but are tactically interesting: Dream Quest, Slay the Spire
* Roguelikes with dynamic worlds: Dwarf Fortress, Gearhead, Caves of Qud
* Strategy/tactical games with emergent stories from a squad of characters: XCOM
* Other KOEI games: Nobunaga's Ambition, Gemfire, Royal Blood 2, Celtic Tales: Balor of the Evil Eye 

The goal is not to include all the good things from all of these games -- that would probably be an unplayable kitchen sink -- but to have a tight design that captures the main good things from these categories.

## Design Manifesto / Critique of KOEI Games

From a design perspective, the main aspect of KOEI's strategy games that I wish to capture is that the fundamental unit of your kingdom is an *officer* (as opposed to nameless military units). Officers are more than military units: they also run your kingdom, make stuff, do diplomacy, etc., so your kingdom feels much more like it is comprised of people as opposed to being a single abstract intelligence, and successes/failures of individual tasks depend on who is doing them. This is also why I think the word "officer" is better than "hero," which typically limits the role of the unit to warlike activities.

Master of Orion 2, Endless Legend, etc. all have these types of officers/heroes, but they do not feel as ``alive'' to me as the KOEI games, mostly because KOEI officers generate dynamic stoies: they go on quests, have feelings/tendencies, ignore your orders, betray you, were a spy all along, were totally not spying so you should have trusted them, get stronger, get permanently injured, etc. This sets up for dynamic relationships between the characters: in one game, Xiahou Dun may be on the same team as Zhang Fei, in another story, they may be bitter rivals. This feature is echoed by games like Civilization (India can be your friend in one but foe the other, etc.), but in KOEI games this also happens on the level of your officers instead of the macro-level kingdoms. 

This means you get stories _unique_ to you (as opposed to setpiece stories in games like Fire Emblem, which could be great stories but are scripted). In one of my games, Lu Bu, true to his historical / literature designation as a strong but disloyal warrior, switched masters 2-3 times (including being recruited by and subsequently betraying myself) before ending his life at my guillotine. However, in a different game, he was one of my best helpers all along and remained a loyal general to the end (there was proabably still a high *chance* of disloyalty, but the key was that it was not a scripted event that he would act on it, giving him a semblance of free will). These stories really take center piece in KOEI games with a lot of dialogue, dynamic interactions, and events. XCOM (I prefer the remake) is the closest game I can think that does this well. As a much cheaper but still endearing example, I have always loved the advisors in Civilization 2 (and how they may squabble with each other), even if I didn't care for their recommendations to sheathe my swords in the hearts of my enemies.

The main weaknesses of KOEI games are:
* complexity: there are lots of attributes, commands, and systems, which means that there is a lot of micromanagement and complexity. Navigating complex systems is fun when a player first learns the game (like optimizing workers in Civilization), but they eventually become chores in ROTK, since there's usually one way to do something correctly (strategically always buy soldiers on your strongest officers near the borders, tactically always use fire/arrows to weaken enemy, charge low-health units to capture them, always initiate duels with Lu Bu, etc.). To summarize: I never felt particularly smart or accomplished, even when I was successful in the game.
* predictable world: much of the game after the first playthrough becomes knowing which officers are overpowered and using the static knowledge of the game to snipe those officers (for example, if you know Zhao Yun has the overpowered "Break Tactics" skill, and you know he appears in a city on the northeast at year XXX, then you go to that place and snipe him before Gongsun Zan does, etc.). The *first* time you experience all of this, it is very fun because it is exploratory; but afterwards the magic slowly disappears as everything becomes execution-oriented. I personally believe it is extremely impressive on KOEI's part that considering that tactics against Zhuge Liang always fail, Lu Bu is always Lu Bu, and Cao Cao will always be your Pain in the North, that each new game in the series feels fun at all; 
* non-semblance of AI: in general, when game rules are complex, the AI becomes very bad at exploiting the complexity. Without lots of design hours and stress-testing, it is very easy for AI to do obviously bad things or just be repeatedly trumped by the player by trivial-looking actions. This is extremely immersion breaking. For example, in ROTK 4 repeatedly luring enemy officers with reliable pathfinding algorithms to burn them with fire tactics will consistently destroy a whole army of AI, whereas humans would fall for such tricks at most once. This allowed me to basically beat the game on hard mode with just 1-2 officers with the "Fire" and "Weather" skills (the latter to keep the fire going) and basically no soldiers for the entire game. I emphasize that the *semblance of AI* is actually more important than the *strength* of the AI for me, since lack of difficulty can (usually) be ameliorated by finding human opponents or making the AI artificially stronger. If a Civilization player complains about AI, it is (usually) not because the game is too easy on Deity difficulty. Instead, it is usually that the AI will do weird things like send 1 weak unit at a time to attack a strong position, or have units walk back and forth unnecessarily where they are not needed, and that is when the player feels like they are bullying a child instead of successfully meeting a challenge.

All of these weaknesses lead to tedium and thus lack of replayability. Finding the right "If X, then Y" heuristics, learning about a particular special event that unlocks a certain character, or finding an AI exploit for the first time is always fun and often takes ingenuity; however, they lose most of their magic in a second playthrough. 

In all, KOEI games have a lot of flavor and are tons of fun (especially if you are into the source material; I loved seeing my knowledge of the Three Kingdoms play out and learning about Irish mythology after playing Celtic Tales), but after a couple of plays they become very "game-like" and not interesting at all strategically (against the AI; it is still possible to find challenging PVP experiences in, say, China), and under high-level competition very few strategies are viable. This is not a problem with just KOEI games - all strategic games, if not all games, fall into the same pattern, and even the "perfect" imaginary version of FOTD would eventually, if placed into the hands of a competent and experienced gamer. The point is that knowing these defects allow us to try to design a game that faces these pain-points head on.

## Interesting choices

More than a decade later after playing (and loving to death) KOEI games, I now have a general approach to the 2 layers of FOTD: 

* the strategy layer will be a "phase selection" simultaneous-turn game inspired by Race for the Galaxy (and somewhat by Diplomacy);
* the battle layer will be a single-selection simultaneous-turn game inspired by rock-paper-scissors (and related games like Yomi). 

The goal is to make the choices in FOTD "interesting." To show what this means, I use Slay the Spire as an example; in particular, I mean the choices of 1-out-of-3 cards to add to your deck. The testament that these choices are interesting is that quite often, a player who is very good at the game (for example, joiNrbs) will pause and think about which of 3 cards to pick, often giving reasons and counter-reasons to defend his/her decision, in a place where less skilled players would pick the card automatically with a less nuanced heuristic. (and also, said players can consistently win at some level, say Ascension 20, where lesser players repeatedly lose Ascension 3, so there is clearly a skill difference)

Note that for a game to "have interesting decisions", it is not important for every situation, or even many situations, to be interesting -- usually, the right move in Poker (a pretty interesting game) is simply folding and ending the game -- as long as that *at least once in a while* the situation is different enough to warrant thinking. What gives Slay the Spire even more points is that even the less tactically-interesting portion, the actual playing of the cards in the deck, is "interesting" by this definition.

We now give an idealized example of an interesting choice in the battle layer of FOTD (which is also representative of the strategic layer, both being simultaneous-turn). The context is that there is roughly a rock < paper < scissors < rock relationship of the form Attacking < Defending < Indirect Tactics < Attacking (though the choices have other effects as well).

Visualization: you are deadlocked in an important battle. It is a rainy day, and the enemy has a slight army advantage, so Attacking is a good choice for the enemy. You do not have the Flood skill ready this turn (which you can activate if you pick Defense and the enemy picks Attack to do massive damage on rainy days). However, you know that the enemy is very likely to not attack because you used Flood previously and the AI knows it is raining, so the AI is likely to value Defending higher than Attacking. You decide the AI will never consider Attacking, so you use Indirect Attack. Indeed, the AI Defends, and you do free damage using your Indirect Attack. 

What will (hopefully) make this much more interesting than straight rock-paper-scissors (which already has quite a bit of complexity when it comes to humans) is the different conditions (weather, available tactics, available tactics to the opponents) and diverse officer skills, with the structural goal that each potential battle condition / skill's existence on the field is something that can potentially change a good player's decision in a nontrivial fraction of the space of possibilities.

I now address the 3 flaws mentioned, mentioning other games with relevant strengths. At the end of each section is a mantra that I would like to apply (as a type of mission statement) to FOTD and a visualization (like the above) of how I envision something to play out in the game.

### complexity

I am inspired by games that cut away a lot of artificial complexity but leave kernels of interesting gameplay and going all in on them. 

* In a traditional hack-and-slash RPG you may have the player control many things from equipping items in different slots, arranging items physically in an inventory, moving through the dungeon in different ways (running/walking/stealthily/searching for traps), doing different things based on distance from the enemies, or targetting different body parts during combat. In Slay the Spire, we abstract away *all* of the above, focusing on just building a deck of actions, a set of potions, and a couple of attributes. 
* In many traditional fighting games, we have a lot of *knowledge* about movesets, combos, and action types from which seasoned players can create skillful displays of ability and rich gameplay experiences. In Divekick/Nidhogg/Smash Brothers, we abstract away a lot of combo knowledge and execution associated with many fighting games to the main concepts of space control and psychological battles. 
* In many games associated with war, such as RTS's, MOBA's, etc. we have abstractions of agents hitting each other, having different healths, speed, movement resolution rules, etc. In the board game of Go, we abstract away health, types, even the idea of movement (which a priori sounds absolutely essential to war and conflict) to have a game that looks nothing like war but captures a lot of emergent richness often associated with war games.

This type of design removes attention away from many aspects of the game, logically removing some complexity and decision-making that could (and often) contain interest to the player. However, in return, more attenion is spent on a smaller part of the game. This makes the game more fun for "chooser" players that like making a smaller number of meaningful decisions, and less fun for "tweaker" players who like to have control over many knobs and things. In FOTD,  I decide to favor "choosers," acknowledging full well that one can get lots of interesting complexity and gameplay from tweaking.

My mantra to myself is (Strunk and White may agree): *if a type of choice usually has just 1 right answer, remove it.*

Visualization: inverted, as this item is defined by what I do not want to see. In traditional officer-based strategy games, there are things that any reasonable person / AI would want to do given the situation:

* any time a free officer appears in your territory, basically 100% of the time you should try to recruit them (as opposed to, say, ignore them)
* any time one of your stronger officers loses loyalty, basically 100% of the time your first priority should be to raise their loyalty 
* you always raise soldiers near the borders, or important cities/production centers, never a corner city somewhere

I visualize FOTD as *not* having any such decisions.

### predictable world

This is the trump suit of roguelikes, with their randomization and procedural generation. Roguelikes optimized for randomized worldbuilding are really great at what they do: Caves of Qud, ADOM, Dwarf Fortress, Gearhead, Dwarf Fortress, Elona, Dwarf Fortress (did I mention Dwarf Fortress?), etc.

While I love the historical/literature origins of the KOEI games, I think a game that trades that part away for the exploration of a new world in each game is a stronger overall experience (this is what makes every early game of Civilization very fun, as a game where you start on an island is very different from a game where you start in a desert sandwiched between 2 aggressive AI's). 

My mantra to myself is: *every once in a while, the player should find him/herself in a unique situation because of the way this particular world is built.*

Visualization: you recruit Mulan "Blood Flower" Yu, a valiant officer that earned her in-game title from her being observed in a battle by a famous passer-by (who bestows titles). You take her into combat and she defeats Shang Li, an officer that she Bonded with from being in the same battles several times under Samuwan Else, a rival king. You fail to recruit Shang Li (since he has the Loyal trait and doesn't want to defect from his liege) and imprison him instead. In prison, he dies. Mulan becomes Saddened (because they were Bonded) and wouldn't perform her tasks well. In a couple of months, she retires voluntarily from her service (and permanently from the game), leaving her sword "Earthpiercer" to Xiahou Skywalker, who has the relationship "Protege" with Mulan.
 
### non-semblance of AI

Well-resourced projects like AlphaGo aside, it is really hard to make good AIs for strategy games, since in general it is hard for AI to abstract the kind of info the players have access to, and to explore a huge space of options, including many boundary options that humans can find that hand-programmed AI cannot (stuff like "can I go to battle with only 1 unit, shoot a bunch of arrows and retreat, and repeat this month after month and destroy a larger army?") 

While I can theoretically try to write another neural net (which would be fun and interesting in its own), one free way to get the semblance of AI is to *limit the player strategy space* (which combos with former ideas), simply because it is easier for the AI to think about fewer things. Poker, for example, creates lots of interesting situations with just a few options (raise/fold/call), and is much more amenable to creating a semblance of AI than something like Starcraft. 

Finally, to add insult to injury, even when the AI *does* outthink you, opaqueness and ignorance leads our fragile human egos to not find the beauty of that. If a neural network beats a human at chess, even though in some abstract sense it is doing some amazing type of thinking, people are seldom impressed. They are likely to attribute the win to something like "oh it is supposed to win because it just calculates all the moves" (which is typically mathematically impossible). 

This leads to a solution which I think is extremely underutilized, and that is to explain the AI's thinking process. We often treat the AI as a black box, but if we can have it explain its thinking on why it made a move, it would make you feel that you just won (or lost) against a real opponent. What better genre to do that than in a strategy game where we have colorful dialogues of officers? [1] 

My mantra to myself is: *when you win (resp. lose) against the AI, make it feel like you are outwitting the AI (resp. being outwitted), as opposed to the AI being simply dumb (resp. unfairly buffed).*

Visualization: right after you make your orders for the day, deciding to attack because you just defended twice, and you want to psych out the AI, the screen cuts to the enemy's camp an hour prior as they were strategizing on their own orders. After weighing different options, Alexander "Military Genius" Ingram says ``the enemy Defended twice, so they are likely to not Defend a third time. Conditioned on that, the enemy has been mostly playing Indirect Attacks, and Attack. I think we should lay a Trap for them." (and behind the scenes, this is actually a function call that was selected randomly to decide the outcome choice). You sit back, dismayed, as the unchangeable orders of your attack from the previous day plays into the enemy's trap, exactly as they planned.

By the way, the simultaneous-turn structure makes the game feel more "fair" (and thus have more semblance of AI) and adds the important elements of bluffing instead of simply reacting to information. This is another benefit of the proposed design.

[1]: For chess developers: I personally think it would be amazing if a chess AI would just say something like "if you make that move it would destroy the use of your queen" rather than "if you move that way my probability of winning goes up to 61%;" this is a meta - machine learning problem, where the output features are human descriptions and the input features are neural network decisions.
