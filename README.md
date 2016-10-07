## Donut Simulator

Welcome to *Donut Simulator*, the program that completely fails to live up to its name.

#### If it doesn't simulate donuts, then what does it do?

This is a population simulator! It creates a bunch of circles which can observe their environment, move around, eat, and reproduce, and simulates them living in an environment with randomly-generated "trees" which they can eat. Successful ones live to reproduce and have children, and eventually become the masters of the technicolor forest. It's loads of fun (and loads of processor-melting floating-point operations!) To use the terms of art, it's pretty much a genetic algorithm for neural networks.

#### Why is it called Donut Simulator?

The world that these organisms inhabit wraps at the edges. This means that their world is shaped like a *toroid*, aka approximately a donut.

#### What do I need to experience this simulationy goodness?

You'll need **Python 3**, as well as the **pygame** library for displaying graphics and the **noise** library for generating the terrain. I think that's it?

#### Is it finished?

No!!

## Screenshots

![Spoiler: the trees always win.](images/treeswin.png)

*In the beginning, the trees are winning. But their lead isn't safe for long...*

![How do you even pronounce "Uteu"?](images/uteu.png)

*Here, a species calling themselves 'Uteu' have appeared and learned that trees taste good.*

![The red species is named 'bkuz' bkuz why not.](images/vuir_bkuz.png)

*Sometimes multiple species find each other and have to compete for resources. Exciting!*

!["Arlyu" could almost be a real name?](images/arlyu.png)

*Creatures who are especially good at tree-eating pull ahead of the rest.*

![what kind of name is "ooyn-ihub"](images/vying.png)

*At the peak of the creature population, many different species will start vying for control.*

![When will they learn that clear-cutting isn't a long-term viable strategy?](images/dentbetter.png)

*The creatures make a big dent in the tree population, but that kind of growth isn't sustainable.*

![Well, they're all dead. I guess they'll never learn their lesson.](images/sordid_history.png)

*Looks like they didn't survive the ensuing fallout from their greed. Oh well.*

![They live among the trees.](images/ihub.png)

*Sometimes, a species will learn to live in harmony with nature, and survive the boom-and-bust cycle.*

![I'm so proud of them.](images/stableish.png)

*If they manage to reach a stable equilibrium, you get to see some cool population dynamics.*

![The green trees' species is named "sir." That's pretty awesome.](images/region.png)

*Often you get to see regional variation, which is pretty interesting as well.*

Since this thing is highly dependent on random chance, I recommend leaving this running for a long time and then coming back to it later if you want to see more interesting stuff happen.
