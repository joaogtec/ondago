# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

Activate the virtual environment and start the dev server:

```powershell
.venv\Scripts\Activate.ps1
python app.py
```

The app runs at `http://127.0.0.1:5000` with `debug=True`. The SQLite database (`instance/ondago.db`) is created automatically on first run via `db.create_all()`.

There are no tests and no linter configured.

## Architecture

**OndaGo** is a Portuguese-language surf carpool/rideshare app. Surfers can publish rides ("barcas") to the beach, and other users can book spots ("reservar").

Everything lives in two files:

- `models.py` — SQLAlchemy models + Flask-SQLAlchemy `db` instance
- `app.py` — all Flask routes, login setup, and image upload logic

**Data model:**
- `Usuario` — registered user with surf level (`nivel`), optional profile photo (`foto_url`), and werkzeug password hash
- `Carona` — a ride offer with origin/destination, date (`dd/mm/yyyy` string), time, total seats, and board type (`tipo_prancha`). The `expirada` property computes expiry by comparing `datetime.now()` against the stored date+time
- `Reserva` — join table between `Usuario` and `Carona`
- `Avaliacao` — model defined in `models.py` but not yet wired to any route

**Templates** (`templates/`) are standalone HTML files with inline CSS — there is no base layout/template inheritance and no separate stylesheet. Each page carries its own full `<head>` and styles.

**Profile photos** are uploaded to `static/uploads/`, resized to 200×200 via Pillow, and stored as `user_<id>.<ext>`.

## Key conventions

- The codebase is in **European Portuguese** — variable names, flash messages, route names, and UI copy are all in PT-PT (e.g., `carona`, `barca`, `vagas`, `motorista`).
- Dates are stored as `dd/mm/yyyy` strings in the `Carona.data` column, not as `Date`/`DateTime` types. Forms submit `yyyy-mm-dd` (HTML date input) and `app.py` converts on save.
- Flash message categories are `'sucesso'` and `'erro'` (not Flask's default `'message'`). Templates match with `.flash-sucesso` / `.flash-erro` CSS classes.
- `Carona.expirada` silently returns `False` on parse errors — be careful when changing the date format.
- The `SECRET_KEY` is hardcoded in `app.py`. Do not commit real secrets.
