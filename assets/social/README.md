# Social preview images

1280×640, one per public repository. GitHub shows this image whenever a
repository link is shared on X, LinkedIn, Slack or Discord; without one,
it shows a generic card with the owner's avatar.

GitHub has no API for this setting, so each one is uploaded by hand:
**repository → Settings → General → Social preview → Edit → Upload an image**.

The cards are drawn, not designed one by one: [`kart.py`](kart.py) renders
every entry in [`kartlar.json`](kartlar.json) from one template. Change a
line there and run `python3 assets/social/kart.py <repo>` to redraw it.
The accent colour is the repository's area on the profile — blue for
tools that check other work, gold for agent infrastructure, green for MCP
servers, teal for apps, pink for games.

Every figure on a card is one the repository itself states. A card
carries no test counts, because those change and an uploaded image
does not.

| Repository | File |
|---|---|
| ai-job-gateway | [ai-job-gateway.png](ai-job-gateway.png) |
| ai-workflow-engine | [ai-workflow-engine.png](ai-workflow-engine.png) |
| ajans-os | [ajans-os.png](ajans-os.png) |
| asset-provenance-toolkit | [asset-provenance-toolkit.png](asset-provenance-toolkit.png) |
| buradane | [buradane.png](buradane.png) |
| claude-code-intelligence | [claude-code-intelligence.png](claude-code-intelligence.png) |
| derin-kazi | [derin-kazi.png](derin-kazi.png) |
| Furkiozknn.github.io | [Furkiozknn.github.io.png](Furkiozknn.github.io.png) |
| godot-2d-sablon | [godot-2d-sablon.png](godot-2d-sablon.png) |
| godot-refcheck | [godot-refcheck.png](godot-refcheck.png) |
| kanca | [kanca.png](kanca.png) |
| local-notes-search-mcp | [local-notes-search-mcp.png](local-notes-search-mcp.png) |
| masal | [masal.png](masal.png) |
| mcp-census | [mcp-census.png](mcp-census.png) |
| mcp-vet | [mcp-vet.png](mcp-vet.png) |
| mini-creative-toolkit | [mini-creative-toolkit.png](mini-creative-toolkit.png) |
| model-comparison-harness | [model-comparison-harness.png](model-comparison-harness.png) |
| nova-drift | [nova-drift.png](nova-drift.png) |
| nvidia-nim-mcp | [nvidia-nim-mcp.png](nvidia-nim-mcp.png) |
| prompt-template-manager | [prompt-template-manager.png](prompt-template-manager.png) |
| repo-ratchet | [repo-ratchet.png](repo-ratchet.png) |
| repo-vet | [repo-vet.png](repo-vet.png) |
| tek-tus-kosu | [tek-tus-kosu.png](tek-tus-kosu.png) |
| turkce-ajanlar | [turkce-ajanlar.png](turkce-ajanlar.png) |
| voice-io-mcp | [voice-io-mcp.png](voice-io-mcp.png) |
| yercekimi-cevir | [yercekimi-cevir.png](yercekimi-cevir.png) |
