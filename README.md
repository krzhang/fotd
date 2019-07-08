# Fall of the Dragon

## A roguelike-inspired take on KOEI's officer-based strategy games

Fall of the Dragon is a nod to the officer-based strategy titles I enjoyed as a kid, mainly inspired by KOEI's Romance of the Three Kingdoms (and also in increasing obscurity: Nobunaga's Ambition, Gemfire, Taikou Risshinden, Celtic Tales: Balor of the Evil Eye...) series. Its main features are:

* dynamically generated world and officers, with their own personalities and relationships
* strategic style (fewer decisions, no micromanagement) of both the strategy (kingdom-building) and tactical (battle) layers, driven by mechanically simple (rock-paper-scissors-like) option spaces but providing rich bluffing/outwitting situation-dependent play

## On KOEI Games and FOTD's Design

From a design perspective, the main strengths are:

* the fundamental unit of your kingdom is offers you can be attached to (as opposed to nameless military units), so you can live / tell your friends the stories you had with particular officers that feel real as they grow stronger, die, etc. In strategy games this feeling is also captured well in games like XCOM, and occasionally in small flashes such as heroes of Master of Orion 2, but they really take center field in KOEI games with a lot of dialogue, dynamic interactions, and events.
* officers are more than military units; they also run your kingdom, go on quests, have feelings, ignore your orders, betray you, etc. this sets up for dynamic relationships between the characters: in one game, Lu Bu may be on the same team as Zhang Fei, in another story, they may be bitter rivals. This feature is echoed by games like Civilization (India can be your friend in one but foe the other, etc.), but in KOEI games this also happens on the level of your officers instead of the macro-level kingdoms.

Their main weaknesses are
* complexity / tedium: there is a lot of micromanagement and complexity, which is fun when a player first learns the game (like optimizing workers in Civilization, or timing when to farm), but after learning the skills they feel like chores, since there's usually one way to do something correctly (strategically always buy soldiers on your strongest officers near the borders, tactically always use fire/arrows to weaken enemy, charge low-health units, etc.).
* predictability/replayability: much of the game after the first playthrough becomes knowing which officers ar eoverpowered and using the static knowledge of the game to snipe those officers (for example, if you know Zhao Yun has the overpowered "Break Tactics" skill, and you know he appears in a city on the northeast at year XXX, then you go to that place and snipe him before Gongsun Zan does, etc.). The *first* time you experience all of this, it is very fun because it is exploratory; but afterwards the magic slowly disappears as everything becomes execution-oriented.
* semblance of AI: entangled with *tedium* above; what happens with a lot of *complexity* in game rules is that the AI becomes very bad at exploiting the complexity. With out lots of design hours, it is very easy for AI to do obviously bad things or just be repeatedly trumped by the player by trivial-looking actions that can be theme/immersion breaking (for example, repeatedly luring enemy officers with reliable pathfinding algorithms to burn them with fire tactics; this allows the player to basically beat RTK 4 with just 1-2 officers with the "Fire" and "Weather" skills (the latter to keep the fire going). Finding these tricks is really fun the first time, but later just becomes AI-bullying, and the computer can never learn from this the way a human might. I wish to point out that the semblance of AI is actually more important than AI for me, since it's not the difficulty that's mainly lacking (one can theoretically find human opponents, or just make the AI artificially stronger), but the breaking of immersion that comes when one realizes an opponent cannot see simple things or fall for the same tricks over and over again.

What this makes for are games with a lot of flavor, fun, but after a while becomes "game-like" and not interesting at all from a strategic perspective against the AI. It is still possible to have tactically interesting PVP experiences (and lots of people, mostly in Asia, do play these games still in this way), but that limits the tactical space as well (while the game offers so much complexity, only a couple of tactics become viable in high-level play; this is a common bane of games with any strategic choice that can only be fixed by lots of stress-testing). 

This is not a bash against KOEI games in particular - many strategic games, if not many games, fall into the same pattern. Even the perfect version of this game I am trying to design probably would, especially when placed into the hands of a strategic-minded gamer. However, knowing the defects allow us to try to design a game that faces these pain-points head on, and that makes this an interesting personal project (as opposed to just designing another version of these games).

Years later, I think I have designs around all 3 flaws mentioned. It's exciting that some games/genres offer design choices that attack multiple angles at once.

* complexity / tedium: I am inspired by games that cut away a lot of artificial complexity but leave a kernel of something interesting and focusing entirely on that. In Slay the Spire, we abstract away moving physically though a dungeon, and instead just focus on the deck-building and (to a smaller but still fun extent, deck-playing). In Divekick/Yomi/Nidhogg, we abstract away a lot of combo knowledge and execution to the main aspects of space control and psychological battles in fighting games. Perhaps the best example is Go, where we abstract away *movement* of armies, HP, etc. to have a game that looks nothing like war but captures a grand swath of strategy and tactics. My mantra to myself is: *every type of choice should be sometimes meaningful, else it should not be a choice.*
* predictability/replayability: roguelikes shine here, focusing on randomized starts and procedural generation on the nose, both in the tactical situations (Slay the Spire, etc.) and the worldbuilding (Caves of Qud, Gearhead, etc.) While I love the historical/literature origins of the KOEI games, I think a game that trades that part away for the exploration of a new world in each game is a stronger overall experience (this is what makes every early game of Civilization very fun). My mantra to myself is: *every new game should feel like joyfully exploring a new world.*
* semblance of AI: it is really, really hard to make a good AI for strategy games, mostly because it is very hard for AI to abstract the kind of info the players have access to, and to explore a huge space of options, including many boundary options that humans can find that hand-programmed AI cannot (stuff like "can I go to battle with only 1 soldier and just duel everyone to death?"). While I can e.g. try to write another neural net (which is interesting in its own), I think one free way to get the semblance of AI is to *limit the player strategy space* (which combos with former ideas), because it is easier for the AI to think about fewer things. Poker, for example, creates lots of interesting situations with just a few options (raise/fold/call), and is much more amenable to creating a semblance of AI than something like Starcraft. My mantra to myself is: *make it feel like you are outwitting and/or being outwitted.*

And that is (the grand vision of) Fall of the Dragon. 
