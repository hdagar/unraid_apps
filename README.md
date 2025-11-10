# unraid_apps

This repo contains the **public Unraid templates and resources** for SWAMI.

- `templates/swami.xml` – The Unraid App XML template (ready for end users)
- `icons/swami-icon.png` – App icon
- `README.md`, `Dockerfile`, `swami.py` – Public docs, Docker build, and source code

_If you are developing the app, use the `unraid_dev` repo. When ready to publish, run `promote_to_public.sh` in the dev repo to sync the latest template and assets here, ensuring DockerHub and all GitHub links point to the public versions._