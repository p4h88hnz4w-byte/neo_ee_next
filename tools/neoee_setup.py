#!/usr/bin/env python3
# Copyright (C) 2026 the neo_ee_next contributors
# SPDX-License-Identifier: GPL-3.0-only
"""Attach this NeoEE patch to an empire_earth_next checkout and build it for the host OS.

  python3 -I tools/neoee_setup.py
  python3 -I tools/neoee_setup.py --play ../EE-play
  py -3 -I tools/neoee_setup.py --play C:\\EE-play          (Windows)

The same command runs on Linux, macOS, and Windows. It uses the standard library only.

What it does, in order, skipping a step that is already done:

  1. Apply patches/neoee-on-ee-next.patch to the empire_earth_next checkout.
     The patch is NeoEE table data only. It does not contain that project's source.
  2. Copy random-map scripts from an extracted NeoEE Art of Conquest tree.
  3. Fetch the pinned media and 4x textures when data/ does not already have them.
  4. Build the game for this machine (xbuild.py on Linux and macOS, build.py on Windows).
  5. With --play, make a play folder, or refresh one that already exists.

Defaults look beside this repository:

  ../empire_earth_next
  extract/app/Empire Earth - The Art of Conquest
  ../empire-earth-gold/Empire Earth - The Art of Conquest/Data/Movies

--neoee and --movies may instead be the directory innoextract wrote. The
script finds the Art of Conquest movies and random-map scripts inside it.
A missing default is skipped. An existing play folder is not deleted.
--force-play replaces one that tools/make_play_dir.py created, which removes
its config and saves.

On Debian and Ubuntu the packages are listed in DEPENDENCIES.md. empire_earth_next
fetches media with the gh CLI. When that CLI cannot read a public release
without a login, this script puts tools/bin/gh first on PATH for that step.
"""

import argparse
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATCH = ROOT / "patches" / "neoee-on-ee-next.patch"
PIN = "7cc02da3aa036e7f87a6e7602a366adc2c086882"
MEDIA_TAG = "open-media-ddb67f1"
TEXTURES_TAG = "open-textures-4x-cb74e27"

DEFAULT_GAME = ROOT.parent / "empire_earth_next"
DEFAULT_NEEE = ROOT / "extract" / "app" / "Empire Earth - The Art of Conquest"
DEFAULT_MOVIES = (ROOT.parent / "empire-earth-gold" / "Empire Earth - The Art of Conquest"
                  / "Data" / "Movies")


def host():
    """'windows', 'macos', or 'linux'."""
    if sys.platform == "win32":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


def build_target():
    """empire_earth_next's name for this machine (tools/xbuild.py)."""
    machine = platform.machine().lower()
    arch = "arm64" if machine in ("arm64", "aarch64") else "x86_64"
    if host() == "macos":
        return f"macos-{arch}"
    if host() == "windows":
        return "windows-x86_64"
    return f"linux-{arch}"


PUBLIC_GH = ROOT / "tools" / "bin" / "gh"
UPSTREAM = "Protryon/empire_earth_next"


def run(cmd, cwd, dry_run, env=None):
    print(" ", " ".join(str(c) for c in cmd), flush=True)
    if dry_run:
        return
    result = subprocess.run([str(c) for c in cmd], cwd=cwd, env=env)
    if result.returncode:
        sys.exit(f"failed ({result.returncode}): {cmd[0]}")


def git(game, *args, check=True):
    result = subprocess.run(["git", "-C", str(game), *args], capture_output=True, text=True)
    if check and result.returncode:
        sys.exit(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result


def require_game(path):
    path = path.resolve()
    if not (path / "tools" / "xbuild.py").is_file() or not (path / "build.py").is_file():
        sys.exit(f"{path} is not an empire_earth_next checkout (tools/xbuild.py and build.py)")
    return path


def check_pin(game, require, dry_run):
    result = git(game, "rev-parse", "HEAD", check=False)
    if result.returncode:
        print("pin: this checkout has no commit yet; the patch is against", PIN)
        if require:
            sys.exit(1)
        return
    head = result.stdout.strip()
    if head == PIN:
        print("pin:", head)
        return
    print(f"pin: checkout is {head}")
    print(f"     the patch was made against {PIN}")
    if require and not dry_run:
        sys.exit("pass a checkout of that commit, or drop --require-pin")


def apply_patch(game, dry_run):
    if not PATCH.is_file():
        sys.exit(f"missing {PATCH}")
    forward = git(game, "apply", "--check", str(PATCH), check=False)
    if forward.returncode == 0:
        print("patch: applying", PATCH.name)
        if not dry_run:
            git(game, "apply", str(PATCH))
        return
    reverse = git(game, "apply", "--check", "--reverse", str(PATCH), check=False)
    if reverse.returncode == 0:
        print("patch: already applied")
        return
    sys.exit("patch: does not apply. The checkout is not the pinned commit, "
             "or data/db was edited by hand.\n"
             + (forward.stderr or reverse.stderr))


def find_named(root, dirname, suffix):
    """A directory named dirname that contains suffix. Prefer Art of Conquest.

    innoextract 1.9 writes a GOG Inno Setup 5 tree without an app/ directory,
    and a NeoEE Inno Setup 6 tree under app/. Either one may be passed.
    """
    if root is None or not root.is_dir():
        return None
    hits = []
    if root.name == dirname and any(root.rglob(f"*{suffix}")):
        hits.append(root)
    for path in root.rglob(dirname):
        if path.is_dir() and path not in hits and any(path.rglob(f"*{suffix}")):
            hits.append(path)
    if not hits:
        return None

    def rank(path):
        text = str(path).lower()
        return (0 if "art of conquest" in text else 1, len(path.parts))

    hits.sort(key=rank)
    return hits[0]


def gh_can_read_releases():
    """True when `gh` on PATH can view the public media release without prompting."""
    env = os.environ.copy()
    env["GH_PROMPT_DISABLED"] = "1"
    try:
        result = subprocess.run(
            ["gh", "release", "view", MEDIA_TAG, "--json", "assets", "-R", UPSTREAM],
            capture_output=True, text=True, timeout=25, env=env)
    except (OSError, subprocess.TimeoutExpired):
        return False
    if result.returncode:
        return False
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return False
    return isinstance(data.get("assets"), list)


def release_env():
    """PATH for fetch_data.py. Fall back to tools/bin/gh when the system CLI needs a login."""
    env = os.environ.copy()
    env["GH_PROMPT_DISABLED"] = "1"
    if gh_can_read_releases():
        return env
    if not PUBLIC_GH.is_file():
        sys.exit(f"media: gh cannot read public releases, and {PUBLIC_GH} is missing")
    env["PATH"] = str(PUBLIC_GH.parent) + os.pathsep + env.get("PATH", "")
    print("media: the gh CLI cannot read public releases without a login; using tools/bin/gh")
    return env


def copy_tree_files(source, dest, suffix, dry_run):
    """Copy files whose bytes differ. Returns (copied, unchanged)."""
    copied = unchanged = 0
    for src in sorted(source.rglob(f"*{suffix}")):
        if not src.is_file():
            continue
        rel = src.relative_to(source)
        dst = dest / rel
        data = src.read_bytes()
        if dst.is_file() and dst.read_bytes() == data:
            unchanged += 1
            continue
        copied += 1
        if dry_run:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_name(dst.name + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, dst)
    return copied, unchanged


def install_maps(game, neoee, dry_run):
    if neoee is None:
        print("maps: no NeoEE tree found; the 115 extra scripts are not copied")
        return
    source = find_named(neoee, "Random Map Scripts", ".rmv")
    if source is None:
        sys.exit(f"maps: no .rmv scripts under {neoee}")
    dest = game / "data" / "Random Map Scripts"
    copied, unchanged = copy_tree_files(source, dest, ".rmv", dry_run)
    verb = "would copy" if dry_run else "copied"
    print(f"maps: {copied} {verb}, {unchanged} already matched, from {source}")


def media_ready(game, textures):
    manifest = game / "data" / ".fetched.json"
    root = game / "build" / "data-root" / "Data"
    if not manifest.is_file() or not root.is_dir():
        return False
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if data.get("media", {}).get("tag") != MEDIA_TAG:
        return False
    if textures and data.get("textures-4x", {}).get("tag") != TEXTURES_TAG:
        return False
    return True


def fetch_media(game, textures, allow_fetch, dry_run):
    if media_ready(game, textures):
        extra = f" and {TEXTURES_TAG}" if textures else ""
        print(f"media: {MEDIA_TAG}{extra} already in data/")
        return
    if not allow_fetch:
        sys.exit("media: the pinned releases are not in this checkout. "
                 "Re-run without --no-fetch (needs the gh CLI and a network).")
    cmd = [sys.executable, "-I", str(game / "tools" / "fetch_data.py"),
           "--tag", f"media={MEDIA_TAG}"]
    if textures:
        cmd += ["--tag", f"textures-4x={TEXTURES_TAG}"]
    else:
        cmd += ["--without", "textures-4x"]
    print("media: fetching the pinned releases")
    run(cmd, game, dry_run, None if dry_run else release_env())


def built_exe(game):
    if host() == "windows":
        return game / "build" / "clang" / "exe" / "EE-AOC.exe"
    return game / "build" / "xbuild" / build_target() / "game" / "ee-aoc"


def build_game(game, jobs, dry_run):
    if host() == "windows":
        print("build: Windows", build_target())
        run([sys.executable, "-I", str(game / "build.py"), "-j", str(jobs)], game, dry_run)
    else:
        print("build:", build_target())
        run([sys.executable, "-I", str(game / "tools" / "fetch_posix.py"), "wgpu", "sdl3", "fonts"],
            game, dry_run)
        run([sys.executable, "-I", str(game / "tools" / "xbuild.py"), "game",
             "-j", str(jobs), "--incremental", "--target", build_target()], game, dry_run)
    exe = built_exe(game)
    if not dry_run and not exe.is_file():
        sys.exit(f"build: {exe} was not produced")
    print("build:", exe)


def replace_file(src, dst):
    """Replace dst with src. An existing dst is unlinked by name, so a running program keeps its old file."""
    if dst.is_file() and dst.read_bytes() == src.read_bytes():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".tmp")
    shutil.copy2(src, tmp)
    os.replace(tmp, dst)
    return True


def link_textures(play, game, dry_run):
    """Point the play folder's Textures-4x at the checkout, matching this install."""
    source = game / "data" / "Textures-4x"
    dest = play / "Data" / "Textures-4x"
    if not source.is_dir():
        return
    if dest.is_symlink() and dest.resolve() == source.resolve():
        print("textures: play folder already uses", source)
        return
    print("textures: linking play Data/Textures-4x to", source)
    if dry_run:
        return
    if dest.is_symlink() or dest.exists():
        if dest.is_dir() and not dest.is_symlink():
            shutil.rmtree(dest)
        else:
            dest.unlink()
    if host() == "windows":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(dest), str(source)], check=True)
    else:
        dest.symlink_to(source, target_is_directory=True)


def seed_config(play, dry_run):
    config = play / "config.yaml"
    if config.exists():
        return
    print("config: writing", config, "with texture_resolution 4")
    if dry_run:
        return
    config.write_text(
        "# Created by neoee_setup.py. The game fills anything left out and rewrites this file.\n"
        "graphics:\n"
        "  texture_resolution: 4\n"
        "  texture_filtering: 2\n"
        "  model_detail: 2\n"
        "  effect_detail: 2\n",
        encoding="utf-8")


def create_play(game, play, movies, dry_run):
    exe = built_exe(game)
    if not dry_run and not exe.is_file():
        sys.exit(f"play: {exe} does not exist. Build first, or drop --no-build.")
    data = game / "build" / "data-root"
    if not dry_run and not data.is_dir():
        sys.exit(f"play: {data} does not exist. Fetch the media first, or drop --no-fetch.")
    cmd = [sys.executable, "-I", str(game / "tools" / "make_play_dir.py"), str(play),
           "--data", str(data)]
    if host() == "windows":
        cmd += ["--exe", str(exe)]
    else:
        cmd += ["--posix-exe", str(exe)]
    if movies is not None and movies.is_dir():
        cmd += ["--movies", str(movies)]
    print("play: creating", play)
    run(cmd, game, dry_run)
    link_textures(play, game, dry_run)
    seed_config(play, dry_run)


def refresh_play(game, play, dry_run):
    """Update the program, the tables, and the map scripts. Leave config.yaml and saves."""
    print("play: refreshing", play, "(config and saves stay)")
    exe = built_exe(game)
    if exe.is_file():
        name = "EE-AOC.exe" if host() == "windows" else "ee-aoc"
        if dry_run:
            print("  exe", exe)
        elif replace_file(exe, play / name):
            print("  exe updated")
        else:
            print("  exe already matched")
    copied = unchanged = 0
    for suffix in (".csv", ".yaml"):
        c, u = copy_tree_files(game / "data" / "db", play / "Data" / "db", suffix, dry_run)
        copied += c
        unchanged += u
    verb = "would update" if dry_run else "updated"
    print(f"  tables: {copied} {verb}, {unchanged} already matched")
    map_src = game / "data" / "Random Map Scripts"
    if map_src.is_dir():
        c, u = copy_tree_files(map_src, play / "Data" / "Random Map Scripts", ".rmv", dry_run)
        print(f"  maps: {c} {verb}, {u} already matched")
    link_textures(play, game, dry_run)


def install_play(game, play, movies, force, dry_run):
    if play.exists() and not force:
        refresh_play(game, play, dry_run)
        return
    if play.exists():
        print("play: replacing", play)
        print("  this deletes that folder, including config.yaml and saves")
        if not dry_run and not (play / "play.json").is_file():
            sys.exit(f"{play} was not made by make_play_dir.py (no play.json); refusing to delete it")
        exe = built_exe(game)
        data = game / "build" / "data-root"
        cmd = [sys.executable, "-I", str(game / "tools" / "make_play_dir.py"), str(play),
               "--data", str(data), "--force"]
        if host() == "windows":
            cmd += ["--exe", str(exe)]
        else:
            cmd += ["--posix-exe", str(exe)]
        if movies is not None and movies.is_dir():
            cmd += ["--movies", str(movies)]
        run(cmd, game, dry_run)
        link_textures(play, game, dry_run)
        seed_config(play, dry_run)
        return
    create_play(game, play, movies, dry_run)
    launcher = play / ("EE-AOC.exe" if host() == "windows" else "run.sh")
    print("play: run", launcher)


def resolve(path, default, label):
    if path is not None:
        path = path.resolve()
        if not path.exists():
            sys.exit(f"{label}: {path} does not exist")
        return path
    if default.exists():
        return default.resolve()
    print(f"{label}: {default} is not there; pass --{label} if you have it")
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=__doc__)
    parser.add_argument("--game", type=pathlib.Path, help=f"empire_earth_next checkout (default {DEFAULT_GAME})")
    parser.add_argument("--neoee", type=pathlib.Path,
                        help="extracted NeoEE Art of Conquest folder, for the random-map scripts")
    parser.add_argument("--movies", type=pathlib.Path, help="a folder of retail .bik movies")
    parser.add_argument("--play", type=pathlib.Path, help="play folder to create or refresh")
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    parser.add_argument("--no-build", action="store_true")
    parser.add_argument("--no-fetch", action="store_true")
    parser.add_argument("--no-textures-4x", action="store_true")
    parser.add_argument("--no-maps", action="store_true")
    parser.add_argument("--no-movies", action="store_true")
    parser.add_argument("--no-play", action="store_true")
    parser.add_argument("--force-play", action="store_true",
                        help="replace an existing play folder made by make_play_dir.py")
    parser.add_argument("--require-pin", action="store_true",
                        help=f"stop unless the checkout is {PIN}")
    parser.add_argument("--dry-run", action="store_true", help="print the steps and change nothing")
    args = parser.parse_args()

    game = args.game.resolve() if args.game else DEFAULT_GAME
    if not game.exists():
        sys.exit(f"game: {game} does not exist. Pass --game PATH to the empire_earth_next checkout.")
    game = require_game(game)
    neoee = None if args.no_maps else resolve(args.neoee, DEFAULT_NEEE, "neoee")
    if args.no_movies:
        movies = None
    else:
        movies = resolve(args.movies, DEFAULT_MOVIES, "movies")
        if movies is not None:
            found = find_named(movies, "Movies", ".bik")
            if found is not None:
                if found != movies:
                    print("movies: using", found)
                movies = found
            elif not any(movies.rglob("*.bik")):
                print("movies: no .bik files under", movies, "; the game skips its intro movies")
                movies = None
        if movies is None:
            print("movies: none given; the game skips its intro movies")

    print("host:", host(), build_target())
    check_pin(game, args.require_pin, args.dry_run)
    apply_patch(game, args.dry_run)
    if not args.no_maps:
        install_maps(game, neoee, args.dry_run)
    fetch_media(game, not args.no_textures_4x, not args.no_fetch, args.dry_run)
    if not args.no_build:
        build_game(game, args.jobs, args.dry_run)
    else:
        print("build: skipped")
    if args.play and not args.no_play:
        install_play(game, args.play.resolve(), movies, args.force_play, args.dry_run)
    else:
        print("play: skipped (pass --play DIR to create or refresh a play folder)")
    print("done")


if __name__ == "__main__":
    main()
