# neo_ee_next

NeoEE's Art of Conquest data, on the native
[empire_earth_next](https://github.com/Protryon/empire_earth_next) build.

This repository links to
[Protryon/empire_earth_next](https://github.com/Protryon/empire_earth_next)
and credits its author. He keeps that project, including the right to accept
or reject changes. A bug in the game goes to him as a pull request. This
repository does not contain his source.

The attachment is NeoEE table data for that build. It is not a fork of the
game. A new machine is expected to bring its own GOG installer and its own
NeoEE installer. This repository does not contain those files.

## Pin

| Piece | Value |
| --- | --- |
| Game | [Protryon/empire_earth_next](https://github.com/Protryon/empire_earth_next) `7cc02da3aa036e7f87a6e7602a366adc2c086882` |
| Media | `open-media-ddb67f1` |
| 4x textures | `open-textures-4x-cb74e27` (optional) |
| NeoEE | community patch whose base-game version file reads `2.0.0.5` |
| Windows AoC version for that patch | `1.0.0.7590` (retail Art of Conquest is `1.0.0.2657`) |
| dreXmod in that install | `3.4.0.0` (yukon / drex888, with EnergyCube) |

`empire_earth_next` reads text tables from `data/db`. Copying NeoEE's
`EE-AOC.exe` onto this build does nothing useful.

## Setup

`tools/neoee_setup.py` does the attachment on Linux, macOS, and Windows. It
uses the Python standard library only. From this repository:

```
python3 -I tools/neoee_setup.py --play ../EE-play
```

On Windows the launcher is `py -3 -I tools/neoee_setup.py --play C:\EE-play`.

The script applies the patch, copies NeoEE random-map scripts when that tree
is available, fetches the pinned media when `data/` does not already have it,
and builds with `tools/xbuild.py` on Linux and macOS or `build.py` on Windows.
On macOS, run it with Homebrew's `python3.12`. The system `python3` is older
than the 3.12 the game's tools expect. Apple Silicon and Intel use the same
script. It selects `macos-arm64` or `macos-x86_64` from the machine.
`--play` creates a play folder, or refreshes the program and the tables in one
that already exists. It does not delete a play folder's config or saves unless
`--force-play` is passed.

Paths default to the layout next to this repository (`../empire_earth_next`,
an extracted NeoEE tree, and a GOG movie folder). Pass `--game`, `--neoee`,
and `--movies` when the assets live somewhere else. Each of those may be the
extractor output or the folder inside it. The script looks for the Art of
Conquest movies and random-map scripts. `--dry-run` prints the steps and
writes nothing.

## Debian and Ubuntu

Tested on Ubuntu 24.04. The package names are Debian's. Arch and Omarchy are
a later pass and are not part of this version.

Bring the GOG *Empire Earth Gold* installer and `NeoEE_Setup.exe`. Install
the packages in [DEPENDENCIES.md](DEPENDENCIES.md), then:

```
mkdir -p ~/games/ee
cd ~/games/ee
git clone https://github.com/Protryon/empire_earth_next.git
git -C empire_earth_next checkout 7cc02da3aa036e7f87a6e7602a366adc2c086882
git clone https://github.com/p4h88hnz4w-byte/neo_ee_next.git
innoextract -d gog /path/to/the-gog-installer.exe
innoextract -d neoee /path/to/NeoEE_Setup.exe
cd neo_ee_next
python3 -I tools/neoee_setup.py \
  --game ../empire_earth_next \
  --neoee ../neoee \
  --movies ../gog \
  --play ../EE-play \
  --require-pin
```

innoextract 1.9 writes the GOG installer (Inno Setup 5) as
`gog/Empire Earth - The Art of Conquest/`, with no `app/` directory. The
NeoEE installer is Inno Setup 6, so its tree is
`neoee/app/Empire Earth - The Art of Conquest/`. Either shape is accepted.
The Art of Conquest intros are `MadDocSoftware.bik` and `Sierra.bik`. The
script does not copy `EE-AOC.exe`, `dreXmod.dll`, `neoee.dll`, `Language.dll`,
or `WONLobby.cfg`.

The first run downloads the media (about 330 MB) and the optional 4x textures
(about 1.3 GB), then compiles. Pass `--no-textures-4x` to skip that pack, or
`--jobs N` to cap the compile. Launch `../EE-play/run.sh`. A later run
refreshes the program, the tables, and the map scripts, and leaves
`config.yaml` and saves alone.

Compiling does not read the installers. `empire_earth_next` builds from its
source, and the media come from that project's releases. The GOG installer
is the movie source. The NeoEE installer is the source of the extra
random-map scripts and the title tile. With neither tree present, the script
still applies the table patch, fetches the media, and builds.

The version check sums the executable and the data. Two machines built from
this pin and this patch agree. A private edit of the game source changes the
executable, and that build will not accept a LAN game from this one.

The patch by itself, on a clean checkout of the pin:

```
git checkout 7cc02da3aa036e7f87a6e7602a366adc2c086882
git apply /path/to/neo_ee_next/patches/neoee-on-ee-next.patch
```

| File | Change |
| --- | --- |
| `data/db/dbworld.csv` | Unit cap range 50–1200 becomes 50–4000. The default limit stays 500. |
| `data/db/dbstartingresources.csv` | Adds Unlimited Resources and a zero-resource row. NeoEE's binary table had one trailing zero byte. The text form drops it. |
| `data/db/dbgamevariant.csv` | Adds Hyperion, DeathMatch, and Medium. Their name ids are 4084, 4086, and 4085. This build's string table still uses those ids for Einstein, Isaac Newton, and Leonardo da Vinci. |
| `data/db/dbuicontrols.csv` | 93 of 1,372 controls differ, mostly resource-button type and a few positions. |

The patch does not edit C++. On the Windows client, dreXmod.dll paints its
name and version at the top left of the main menu. A native label that
repeats that text would be a change to `empire_earth_next`, so it is not
shipped here.

NeoEE also adds 115 random-map scripts under `Data/Random Map Scripts`
(Common, Dryterranean, Drytinental, Large Oases, Neo Continental, Neo Large
Islands, Neo Mediterranean, and others). Scripts that already existed were
byte-identical. Those scripts are not in this repository. Copy them from a
NeoEE install of the same patch. Fourteen of the added scripts are signed
"By Kazter". Eight are signed "RealForce/Cobra".

NeoEE also replaces one title-screen tile, `Data/Textures/bkg_title_1_4`.
On the retail screen that tile is sky at the top right. The NeoEE tile
paints "NeoEE Edition" on it. The installer ships that tile as a 256×256
TGA. The setup script writes the PNG this build loads, and a 4× copy when
`Data/Textures-4x` is present. Texture resolution 4 would otherwise keep
the retail tile from that pack. The image stays in the NeoEE install and
is not part of the network checksum.

After the patch, build and play the way `empire_earth_next` documents.
`tools/make_play_dir.py` can assemble a play folder. Set `EE_DATA_ROOT` to
that folder. Optional 4x textures go in `Data/Textures-4x` with
`texture_resolution: 4` in `config.yaml`.

## macOS

Apple Silicon and Intel. The package names are Homebrew's. The steps match
the Debian layout above, including how innoextract lays the two installers
out. Command Line Tools provide clang and the macOS SDK. Install the
packages in [DEPENDENCIES.md](DEPENDENCIES.md), then:

```
mkdir -p ~/games/ee
cd ~/games/ee
git clone https://github.com/Protryon/empire_earth_next.git
git -C empire_earth_next checkout 7cc02da3aa036e7f87a6e7602a366adc2c086882
git clone https://github.com/p4h88hnz4w-byte/neo_ee_next.git
innoextract -d gog /path/to/the-gog-installer.exe
innoextract -d neoee /path/to/NeoEE_Setup.exe
cd neo_ee_next
python3.12 -I tools/neoee_setup.py \
  --game ../empire_earth_next \
  --neoee ../neoee \
  --movies ../gog \
  --play ../EE-play \
  --require-pin
```

If `python3.12` is not on `PATH`, call `"$(brew --prefix)/bin/python3.12"`.
That prefix is `/opt/homebrew` on Apple Silicon and `/usr/local` on Intel.
Build on the Mac that will run the game. An Apple Silicon checkout produces
`build/xbuild/macos-arm64/game/ee-aoc`. An Intel checkout produces
`build/xbuild/macos-x86_64/game/ee-aoc`. `xbuild.py` also writes
`Empire Earth AoC.app` next to that binary. The play folder launches with
`../EE-play/run.sh`.

The minimum system version is macOS 11.0 on Apple Silicon and macOS 10.15
on Intel, which is what `empire_earth_next` passes to the compiler. Drawing
goes through Metal and the pinned wgpu-native library for that architecture
(`macos-aarch64` or `macos-x86_64`). CI for that project runs the Apple
Silicon target. The Intel target is the same source and the same commands
on an Intel Mac.

`tools/neoee_setup.py` passes `--incremental` to `xbuild.py`. That
rebuilds a `.cpp` newer than its object and does not notice a header-only
edit. After one of those, from the game checkout:

```
python3.12 -I tools/xbuild.py game -j 8
```

Run the setup script again so the play folder picks up the new `ee-aoc`.
Drop `--require-pin` when that checkout has commits after the pin. The
NeoEE table edits stay uncommitted in the game tree.

The setup script completed on an Apple Silicon Mac running macOS 26, with
Command Line Tools and Homebrew's Python 3.12, CMake, and Ninja. It
compiled 1384 units for `macos-arm64`, unpacked `open-media-ddb67f1` and
`open-textures-4x-cb74e27`, and converted `MadDocSoftware.bik` and
`Sierra.bik`. Launch is `../EE-play/run.sh`. A finished game is not
recorded here. The Intel target was not built on that machine.

## What it leaves out

These files are in the NeoEE install and are not applied:

- `WONLobby.cfg`. The copy in this install sets the language to Chinese, points the directory servers at `titan.neoee.net` and `neoee.4dq.com`, and turns the CD key check on.
- `Language.dll`, `EE-AOC.exe`, `neoee.dll`, and `dreXmod.dll`.
- EE Reborn model swaps. A same-named `.glb` or `.gltf` on the data path replaces the retail `.cem`. That work is later.

The checksum of this native build will not equal Windows NeoEE `1.0.0.7590`.
Lobby play against stock NeoEE clients is out of scope.

## Bugs in the game

Report a bug in `empire_earth_next` as a pull request on
[Protryon/empire_earth_next](https://github.com/Protryon/empire_earth_next).
Do not carry a copy of his source in this repository.

## What this repository holds

Notes, credits, the setup script, a public-release helper at `tools/bin/gh`,
and the NeoEE table patch. It does not hold `empire_earth_next` source, the
game, a GOG installer, or a NeoEE installer.
`extract/` and `work/` on a machine that has unpacked those installers are
gitignored, along with executables, DLLs, and archives.

## Related projects

These are related. None of them is this attachment.

- [Protryon/empire_earth_next](https://github.com/Protryon/empire_earth_next) is the game this data attaches to. Its author retains it. This repository only links there.
- [EE-modders/Empire-Earth-Setup](https://github.com/EE-modders/Empire-Earth-Setup) installs NeoEE for the original Windows game. Its setup script is GPL-3.0.
- [Grille/Empire-Earth-Age-of-AI](https://github.com/Grille/Empire-Earth-Age-of-AI) documents how the NeoEE executable differs from retail. The Lua port of that AI already ships inside `empire_earth_next` under GPL-3.0. This patch does not change it.
- [maxgraf96/ee-macos](https://github.com/maxgraf96/ee-macos) and [00xJS/Empire-Earth](https://github.com/00xJS/Empire-Earth) run a GOG copy. Both leave NeoEE unsupported.

## License

See [LICENSE](LICENSE). The notes, the setup script, and the NeoEE table
patch are GPL-3.0, the license of the Empire Earth Community Setup that
publishes NeoEE and dreXmod. Empire Earth remains the property of its rights
holders. `empire_earth_next` stays its author's, and this repository does
not relicense it.
