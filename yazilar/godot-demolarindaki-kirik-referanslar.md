---
title: Fifty broken references in 237 Godot projects
date: 2026-09-25
summary: The official demos, material-maker and godot-open-rpg, checked without opening the editor. Most of what turned up, Godot never mentions.
repo: godot-refcheck
---

# Fifty broken references in 237 Godot projects

*25 September 2026 · [godot-refcheck](https://github.com/Furkiozknn/godot-refcheck)*

Godot tells you a reference is broken when the scene holding it loads. If that
scene is a level nobody has opened this week, or a branch of a script that only
runs on one platform, you find out from a player. Some breakage it never tells
you about at all.

I wrote [godot-refcheck](https://github.com/Furkiozknn/godot-refcheck) to find
these without launching the engine. It is one Rust binary with no dependencies.
It reads `.tscn`, `.tres`, `project.godot`, GDScript and shader files, resolves
every reference the way the engine does, and reports the ones that cannot be
satisfied.

A checker like this is only worth running if it stays quiet on projects that
work. So before publishing it, I ran it over eleven real, maintained
repositories: the official demo projects (both the 4.x and the 3.x branch),
the official benchmarks, Pixelorama, material-maker, Lorien, godot-open-rpg,
two of Maaack's templates, Godots and beehave.

| | |
|---|---:|
| Godot projects | 237 |
| files | 19,305 |
| references resolved | 6,904 |
| signal connections checked | 2,741 |
| findings | 50 |

I checked all 50 by hand against the repository each came from, and all 50 are
real. None of the 2,741 signal connections was wrongly called broken. The full
list, with the evidence for each finding, is in
[docs/corpus.md](https://github.com/Furkiozknn/godot-refcheck/blob/main/docs/corpus.md).
I ran it again today against the current `master` of the three repositories
that had findings, and they are all still there.

## Connections that can never fire

The largest group was 16 findings in material-maker. Each one is a signal
connection written into a scene file, pointing at a node the scene doesn't
contain:

```
widgets/curve_edit/curve_dialog.tscn:163: error: broken-connection:
  signal "gui_input" is connected from
  "VBoxContainer/EditorContainer/CurveEditor/@Control@283287",
  which is not a node in this scene
```

`@Control@283287` is a name Godot makes up at run time for a node nobody named.
It changes on every run, so a connection saved against it can never match.
Godot drops a connection it cannot resolve without printing anything. The
editor won't warn you and there is no line in the log; the handler just never
gets called.

## Project icons pointing at nothing

Four of the official demos (`3d/soft_body_physics`,
`3d/tonemap_color_correction`, `audio/audio_effects` and `audio/rhythm_game`)
set `application/config/icon` to a `uid://` that no file in the project owns.
The engine does complain about this one: `ERROR: Unrecognized UID`. But it only
shows up if you open that project and read the output. Nearly every other demo
in the repository writes the icon as a path (`res://icon.svg`), and making these four
match is a one-line change each.

## Scripts reaching for nodes that moved

Nine findings are `$Some/Path` lookups into a scene that was reorganised after
the script was written. In `2d/finite_state_machine`, on both branches, the
player script reaches for `$States/Stagger`. The scene has
`StateMachine/Stagger`.

In `compute/heightmap`, a fallback label is written as
`…/HBoxContainer2/Label2` when the scene has `…/HBoxContainer/Label2`. That line
only runs when `RenderingDevice` is unavailable. That explains how it survives:
none of these lines are on the path a demo normally takes. When one of them
does run, the lookup returns `null` and the next line crashes.

## A shader include from Godot 3

Three brush shaders in material-maker start with
`#include "brush_common_decl.shader"`. The file is `brush_common_decl.gdshader`.
Godot 4 renamed the extension; these includes were never updated.

## The one the engine hides on purpose

This one isn't in the corpus count, but it's why uid checking matters. I took
`2d/dodge_the_creeps`, moved `art/` and `fonts/` under `assets/`, and loaded it.
The engine said nothing, because every reference also carries a `uid://` and
Godot quietly followed the uid instead of the path. Yet 13 paths in those scene
files were now wrong. They stay harmless until the day a `.uid` or `.import`
sidecar goes missing, and then they all break at once.

`godot-refcheck --fix` repaired all 13, because each had exactly one file that
could be the answer. A headless Godot run before and after agreed. It only
repairs what it can prove, and across the whole 237-project corpus
`--fix-dry-run` proposes nothing: unknown uids, dead connections and a missing
addon each need a person to decide.

## What I got wrong on the way

The node-path check first produced 15 findings on this corpus, and five of them
were wrong. Some children are added with `add_child(scene.instantiate())`, and
those carry their scene's *root* name, which a static read has to follow. And a
path the script guards with `has_node("…")` is optional by the author's own
statement. Both are now rules with named regression tests. An earlier version
was worse still: it ignored which object `get_node` was called on, and one of
my own games produced 132 findings from a test harness asking about a scene it
had just built.

## Try it

Binaries for Linux, macOS and Windows are on the
[releases page](https://github.com/Furkiozknn/godot-refcheck/releases), or:

```sh
cargo install --git https://github.com/Furkiozknn/godot-refcheck
godot-refcheck path/to/your/project
```

There is also a GitHub Action with SARIF output, so findings show up in code
scanning. Pin it to `@v0.3.0` or later: the Action in earlier tags fails on
projects that have nothing wrong with them. If it reports something in your project that isn't broken, please
[open an issue](https://github.com/Furkiozknn/godot-refcheck/issues) with the
file. Every rule in it exists because a false finding like that got reported.
