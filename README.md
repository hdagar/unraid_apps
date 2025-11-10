# SWAMI - Unraid App Development

This repo contains all files for developing SWAMI as an Unraid template and Docker app.

- `Dockerfile` and `requirements.txt` define the container.
- `swami.py` is the main application script.
- `templates/swami.xml` is the Unraid XML template (with variable for public promotion).
- `icons/swami-icon.png` is the app icon for Unraid templates.
- `promote_to_public.sh` automates preparing a public-ready version of the template.

## Workflow

- Develop and build locally in this repo.
- When ready, use `promote_to_public.sh` to update/copy public assets to `unraid-apps` with correct DockerHub reference.