# Rhodochrosite Swing

Full-colour **Python 3** neon grappling-swing arcade for ElbowOS.

Featured: **https://x.com/ElbowOS**

Reel (Google Drive): https://drive.google.com/file/d/1LhLnaoFheSKgl3AGZvO-d6yjIoZkgSWl/view?usp=drivesdk

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 rhodochrosite_swing.py
```

- **Space / W / Up** — fire or release the hook
- **A / D or arrows** — pump the swing
- **Esc** — quit

## Record a 9:16 reel

```bash
ELBOWOS_RECORD=1 python3 rhodochrosite_swing.py
```

Writes a 15s 1080×1920 H.264 MP4 (dummy SDL video driver + ffmpeg).

Needs Python 3.10+ and pygame.
