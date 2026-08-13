# Balamonis Creator Workspace v1

The first Creator contract comes directly from the founding Original. Its job is to preserve creative intent and move one story safely from brief to master and derivatives.

## Core objects

| Object | Purpose | Founding-project evidence |
|---|---|---|
| Brief | Audience, goal, promise, formats, and rights ambition | Research brief and proposal |
| Story bible | Logline, theme, characters, locations, objects, and continuity rules | Script development |
| Scene | Dramatic purpose, planned shots, status, and dependencies | Scene plan |
| Asset | Source/generation record and production status | Asset manifest |
| Approval | Human decision at each creative and spend gate | Checkpoints and decision log |
| Rights record | License, consent, territory, term, and permitted uses | Buyer-readiness workflow |
| Authorship entry | Meaningful human writing, selection, direction, edit, and sound choices | Human-authorship journal |
| Delivery | Master, trailer, vertical, caption, audio, QC, and provenance outputs | Publish package |
| Metric | Cost per approved second, accepted shots, completion, and derivative performance | Studio and Creator learning loop |

The machine-readable contract is [workspace.schema.json](../schemas/creator/workspace.schema.json).

## Product principles

- Approvals are first-class data, not comments that can be lost.
- Story and continuity come before generation.
- Rights and consent fields exist before an asset is created.
- Estimated spend is shown before a batch; actual spend is written afterward.
- Human creative contribution is recorded throughout the process.
- One approved master can produce many derivatives without fragmenting the story world.
- Provider and model adapters are replaceable; the story, rights, and decision history remain durable.

## First application flow

```text
Create project
→ guided brief
→ concept approval
→ script approval
→ story/continuity bible
→ scene plan and cost
→ asset approval
→ generation or footage ingest
→ edit and continuity review
→ rights/QC review
→ master and derivative delivery
```

The first web implementation should expose this flow with mocked/local project data before adding billing or multiple generation providers. That validates the product's advantage without coupling the interface to an unstable model catalog.
