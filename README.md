# ttnt-workspace

Top-level integration repository for the TTNT stack.

This repository exists to keep engine-specific adapters parallel instead of letting one engine workspace own the core runtime.

## Layout

- `ttnt/`: engine-agnostic core runtime, data model, services, and cross-engine interfaces
- `ttnt-godot/`: Godot GDExtension adapter, Godot rendering bridge, and Godot debug project
- `ttnt-ue5/`: reserved for the future UE5 adapter repository

## Why This Repo Exists

The workspace enforces the intended dependency direction:

- `ttnt` is the core
- `ttnt-godot` is an adapter
- `ttnt-ue5` will be another adapter

That keeps build tooling, CI, release flow, and repository ownership from drifting toward Godot-specific assumptions.

## Getting Started

Clone with submodules:

```bash
git clone --recursive <this-repo-url>
```

Or initialize after cloning:

```bash
./scripts/bootstrap.sh
```

The bootstrap script initializes the top-level sibling repositories only. Nested dependencies remain owned by each child repository, for example the Godot engine submodules inside `ttnt-godot`.

## VS Code

Open `ttnt.workspace.code-workspace` to load the core and Godot adapter together in one workspace.

## UE5 Placeholder

`ttnt-ue5` is intentionally not added yet because the repository does not exist. The expected contract is documented in `docs/ttnt-ue5.md`.