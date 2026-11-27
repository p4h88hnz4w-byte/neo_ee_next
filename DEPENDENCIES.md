# Dependencies

`tools/neoee_setup.py` is the cross-platform entry point. It calls the tools
below. Versions are the ones this tree was built and played with.

```
python3 -I tools/neoee_setup.py --play ../EE-play
```

On macOS, use Homebrew's Python 3.12 (`python3.12 -I`). See the macOS section.

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

Shared build requirements, from that project's README:

- Python 3.12, standard library only (`python3 -I` on Linux, `python3.12 -I` on macOS)
- clang, CMake, and Ninja
- ffmpeg, when converting intro movies
- innoextract, when unpacking the GOG and NeoEE installers

Linux also needs lld, pkg-config, SDL3's X11 and Wayland development
packages, and a Vulkan adapter. Those package names are in the Debian
section. macOS uses the Command Line Tools SDK, Apple's linker, and Metal.
Those package names are in the macOS section. `tools/neoee_setup.py` runs
the fetch and the build.

Fetch and build from that checkout, when doing it by hand:

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
needed only to copy the 115 extra random-map scripts, to copy the
`bkg_title_1_4` title tile, or to regenerate the tables.

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

## macOS

Apple Silicon (`macos-arm64`) and Intel (`macos-x86_64`). The setup script
picks the target from the machine. `empire_earth_next`'s `tools/xbuild.py`
sets the deployment target to macOS 11.0 on Apple Silicon and macOS 10.15
on Intel. Install Command Line Tools, then Homebrew's packages:

```
xcode-select --install
brew install cmake ninja python@3.12 ffmpeg innoextract git
```

Homebrew's prefix is `/opt/homebrew` on Apple Silicon and `/usr/local` on
Intel. Add `"$(brew --prefix)/bin"` to `PATH` so the build finds
`python3.12`, `cmake`, and `ninja`.

clang and the SDK come from Command Line Tools (`xcrun --show-sdk-path`).
`tools/fetch_posix.py` downloads wgpu-native for `macos-aarch64` or
`macos-x86_64`, and the SDL3 sources. `tools/xbuild.py` builds SDL3 as a
static library and links it with Cocoa, Metal, and the other Apple
frameworks. The game draws with that Metal device. Linux's `lld`,
`pkg-config`, X11, Wayland, and Vulkan packages are not part of this build.

`innoextract` unpacks both installers. `ffmpeg` converts the intro movies.
The compile reads neither installer. Tables come from this repository's
patch, and models, textures, sounds, and music come from the pinned
`empire_earth_next` releases. The GOG tree supplies `.bik` movies. The
NeoEE tree supplies the 115 extra random-map scripts and the title tile.

The `gh` package is not required. `tools/bin/gh` is a Python script. The
setup script puts it first on `PATH` when the GitHub CLI is missing or
cannot read a public release without a login. A token is optional.

The setup script completed on an Apple Silicon Mac running macOS 26, with
Command Line Tools and Homebrew's Python 3.12, CMake, and Ninja. It
compiled `macos-arm64`, fetched both pinned releases, and wrote a play
folder. A finished game is not recorded here. The Intel packages are the
same names. That target was not built on the Apple Silicon machine. The
setup script passes `--incremental` to `xbuild.py`. A header-only change
needs `python3.12 -I tools/xbuild.py game -j 8` from the game checkout,
without `--incremental`, and then another setup run to refresh `ee-aoc`.

## Not required

dreXmod.dll, neoee.dll, Language.dll, and WONLobby.cfg are not loaded by
this build. Wine is not required. The original Windows executables are not
required.
