# ttnt-ue5 Placeholder

`ttnt-ue5` should be added as a sibling submodule under the workspace root once the repository exists.

Planned role:

- Unreal Engine plugin or module host
- UObject or Actor bindings for TTNT runtime concepts
- UE rendering and editor bridge code
- UE-specific samples and debug assets

Rules:

- Keep engine-agnostic logic in `ttnt-runtime`
- Keep Unreal-specific bridging in `ttnt-ue5`
- Do not make `ttnt-runtime` depend on Unreal headers, build tools, or runtime types

Recommended add command when the repository is ready:

```bash
git submodule add <ttnt-ue5-remote-url> ttnt-ue5
```