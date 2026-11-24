# Credits

Empire Earth and Empire Earth: The Art of Conquest were made by Stainless
Steel Studios and published by Sierra Entertainment. Mad Doc Software worked
on Art of Conquest. The games remain the property of their rights holders.

## This attachment

The notes, the setup script, the public-release helper, and the NeoEE table
patch are the neo_ee_next work. They are GPL-3.0. They do not include
`empire_earth_next` source.

## empire_earth_next

[Protryon/empire_earth_next](https://github.com/Protryon/empire_earth_next)
is the native build, and its author keeps it. Link that repository. Give him
credit. Send a bug there as a pull request. Do not redistribute his code from
this repository. The pin used here is
`7cc02da3aa036e7f87a6e7602a366adc2c086882`. It starts from the `empire_earth`
reconstruction's `fixes-all` branch. Third-party libraries under its
`src/ThirdParty/` keep their own licenses.
The Age of AI computer player in `data/ai/ageofai/` is a Lua port of Grille's
work, GPL-3.0, used with the author's permission. This patch does not change
those files.

Media and the optional 4x textures come from that project's GitHub releases
`open-media-ddb67f1` and `open-textures-4x-cb74e27`.

## NeoEE

[NeoEE](https://www.neoee.net/) is the community project that restored Empire
Earth multiplayer after the original Sierra servers were shut down. The NeoEE
about page names Ghost and Omega (servers and Save-EE), RealForce (installer
and patches), and Jodocus (the lobby). The current Windows installer is
maintained as
[EE-modders/Empire-Earth-Setup](https://github.com/EE-modders/Empire-Earth-Setup)
by EnergyCube and the EE-modders. That setup script is GPL-3.0.

The table changes in `patches/neoee-on-ee-next.patch` are NeoEE's data for
Art of Conquest, converted to the text form this native build reads. They
are not a new design.

Random-map scripts added by that install and signed in the file header:

- Kazter, "By Kazter", 14 scripts.
- RealForce/Cobra, 8 scripts.

Other added scripts have no by-line in the first lines of the file. Retail
scripts in the same folder often carry `$Author: Scott Marison $`. Those are
the original game's scripts.

## dreXmod

dreXmod was created by yukon (drex888), with EnergyCube, for the Empire Earth
community. The DLL in the NeoEE install used here is 3.4.0.0. It is a Windows
overlay: camera, lobby theme, ranking, in-game player list, and menu
resolution. Since the 2017 builds, a successful load prints the dreXmod name
and version at the top left of the main menu. This repository does not ship
that DLL, and it does not patch the native menu source to imitate it.

## Later

EE Reborn model and unit swaps are not in this patch. They are the community
replacements discussed for a later pass. A same-named `.glb` or `.gltf` on
the data path is how this build replaces a retail model.
