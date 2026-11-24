# Dependencies

`tools/neoee_setup.py` is the cross-platform entry point. It calls the tools
below. Versions are the ones this tree was built and played with.

```
python3 -I tools/neoee_setup.py --play ../EE-play
```

## Game

A legal copy of *Empire Earth Gold* (*Empire Earth* and *The Art of
Conquest*). This repository does not contain the game.

The native build does not read `data.ssa`. It reads the loose `Data` folder
from `empire_earth_next`: tables from git, media from that project's
releases. Follow that project's README. The releases used here are
`open-media-ddb67f1` and, optionally, `open-textures-4x-cb74e27`.

Intro movies are optional. They are converted from the retail `.bik` files
with ffmpeg (`tools/convert_movies.py` or `tools/make_play_dir.py --movies`).

## empire_earth_next

Commit `7cc02da3aa036e7f87a6e7602a366adc2c086882`.

Build requirements, from that project's README and
`.github/workflows/posix.yml`:

- Python 3.12, standard library only (`python3 -I`)
- clang and lld
- CMake and Ninja
- pkg-config
- SDL3's X11 and Wayland development packages: libx11, libxext, libxrandr,
  libxcursor, libxi, libxss, libxfixes, libxtst, libxkbcommon, libwayland,
  wayland-protocols, libegl, libgl, libdbus, libibus, libdecor
- A Vulkan adapter to play. Mesa RADV is enough on AMD. Headless smoke tests
  can use lavapipe (`mesa-vulkan-drivers`).

Fetch and build from that checkout:

```
python3 -I tools/fetch_posix.py wgpu sdl3 fonts
python3 -I tools/xbuild.py game -j 8 --incremental
```

`tools/fetch_posix.py` downloads pinned wgpu-native, SDL3, and Liberation
fonts with the Python standard library. `fetch_data.py` downloads the media
releases through the `gh` command. Ubuntu 24.04's `gh` package asks for
`gh auth login` even when the release is public. `tools/neoee_setup.py`
switches to `tools/bin/gh` in that case. That helper only lists and downloads
public releases. A token is optional. Set `GH_TOKEN` or `GITHUB_TOKEN` if
GitHub rate-limits the anonymous calls.

Apply `patches/neoee-on-ee-next.patch` for the NeoEE tables. Those files are
data. The game reads them without a rebuild. The patch does not contain
`empire_earth_next` source. Clone that project and build it. A bug in the
game is a pull request there, not a copy of its source in this repository.

## NeoEE, only when re-extracting

The patch file already contains the table changes. A NeoEE installer is
needed only to copy the 115 extra random-map scripts, or to regenerate the
tables.

The install this patch was taken from is the community NeoEE setup. Its
base-game version file (`Empire Earth/zzWONVersion.cfg`) reads `2.0.0.5`.
The Art of Conquest Windows client of that patch reports `1.0.0.7590` on the
main menu. dreXmod in that install is `3.4.0.0`.

Unpacking the installer takes innoextract (the NeoEE setup is Inno Setup 6).
Converting its `.dat` tables takes `empire_earth_next`'s `tools/eedata`.
`dbstartingresources.dat` from that install has one trailing `0` byte after
the last record. Drop that byte before export. The other three Art of
Conquest tables (`dbworld`, `dbgamevariant`, `dbuicontrols`) already match
their record counts.

## Debian and Ubuntu

Tested on Ubuntu 24.04. Python there is 3.12.3. Install:

```
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  python3 git clang lld cmake ninja-build pkg-config ffmpeg innoextract \
  libx11-dev libxext-dev libxrandr-dev libxcursor-dev libxi-dev libxss-dev \
  libxfixes-dev libxtst-dev libxkbcommon-dev libwayland-dev wayland-protocols \
  libegl1-mesa-dev libgl1-mesa-dev libdbus-1-dev libibus-1.0-dev libdecor-0-dev \
  mesa-vulkan-drivers libvulkan1
```

`innoextract` unpacks both installers. `ffmpeg` converts the intro movies.
Mesa's Vulkan driver is enough to play on AMD. The `gh` package is not
required. Arch and Omarchy use different package names and are not part of
this version.

## Not required

dreXmod.dll, neoee.dll, Language.dll, and WONLobby.cfg are not loaded by
this build. Wine is not required. The original Windows executables are not
required.
