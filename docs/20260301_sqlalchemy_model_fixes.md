# SQLAlchemy Model Bug Fixes

**Date**: 2026-03-01
**Affected files**: `db/model/girl_group.py`, `db/model/track.py`, `jobs/job_spotify_export_tracks_csv.py`

---

## Summary

Three issues causing red highlights and strikethrough in the editor (Pylance).

---

## Fix 1 — Missing `back_populates` targets on `GirlGroup`

### Root cause

`relationship(back_populates="X")` requires the referenced model to also define a relationship named `X`.
`GirlGroup` was missing both `ranks` and `track_list`, so Pylance flagged the references as errors.

| Model | `back_populates` value | Exists on `GirlGroup`? |
|-------|------------------------|------------------------|
| `GirlGroupRank.girl_group` | `"ranks"` | No |
| `tracks.girl_group` | `"track_list"` | No |

### Fix (`db/model/girl_group.py`)

Added reverse relationships to `GirlGroup`:

```python
ranks: Mapped[list[GirlGroupRank]] = relationship(back_populates="girl_group")
track_list: Mapped[list[tracks]] = relationship(back_populates="girl_group")
```

---

## Fix 2 — `relationship()` missing `Mapped` type annotations

### Root cause

All columns used SQLAlchemy 2.0 style (`Mapped[...]`), but `relationship()` attributes were
declared without type annotations (legacy 1.x style), causing Pylance to flag them as deprecated.

```python
# Before (1.x legacy style)
girl_group = relationship("GirlGroup", back_populates="ranks")

# After (2.0 style)
girl_group: Mapped[GirlGroup] = relationship(back_populates="ranks")
```

### Changed attributes

| File | Attribute | Before | After |
|------|-----------|--------|-------|
| `girl_group.py` | `GirlGroupRank.girl_group` | no type | `Mapped[GirlGroup]` |
| `track.py` | `tracks.girl_group` | no type | `Mapped[GirlGroup]` |
| `track.py` | `TrackListeningSnapshot.track` | no type | `Mapped[tracks]` |

### Circular import handling

`girl_group.py` references `tracks`, and `track.py` references `GirlGroup`.
To avoid a runtime circular import, used `TYPE_CHECKING` guard with `from __future__ import annotations`:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .track import tracks  # in girl_group.py
```

`from __future__ import annotations` makes all annotations lazily evaluated strings.
SQLAlchemy 2.0 resolves model references at runtime via its own registry, so there is no
functional impact.

---

## Fix 3 — Built-in `id` used instead of `artist_id`

### Root cause (`jobs/job_spotify_export_tracks_csv.py:70`)

```python
# Before — inserts Python built-in id() (memory address)
export_artist_tracks_csv(artist_id, output_path=f"exports/tracks/{id}.csv")

# After — correct variable
export_artist_tracks_csv(artist_id, output_path=f"exports/tracks/{artist_id}.csv")
```

`id` is a Python built-in function. In the f-string it produces a path like
`exports/tracks/<built-in function id>.csv` instead of the intended artist ID.

---

## Note — Potential improvement (not fixed)

`Date` columns are typed as `Mapped[str]` but the accurate Python type is `Mapped[datetime.date]`:

```python
# Current (works but inaccurate)
snapshot_month: Mapped[str] = mapped_column(Date, ...)

# Accurate
from datetime import date
snapshot_month: Mapped[date] = mapped_column(Date, ...)
```

No code currently performs date arithmetic on these columns, so the fix was deferred.
Recommended to address if date operations are added in the future.
