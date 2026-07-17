#!/usr/bin/env python3
"""
pdf_ops.py — the "swiss-army knife" for manipulating existing PDFs.

Pure-python, no LaTeX / ML dependencies. Uses pypdf for structural ops and
pikepdf for robust compression / repair / linearisation.

Subcommands:
  info         Show page count, size, encryption, metadata
  merge        Concatenate several PDFs into one
  split        Split into one file per page (or fixed-size chunks)
  pages        Extract / reorder a page selection into a new PDF
  rotate       Rotate pages (90/180/270)
  watermark    Stamp one PDF (e.g. "CONFIDENTIAL") over another
  encrypt      Password-protect (AES-256)
  decrypt      Remove password (you must know it)
  meta         Get or set document metadata (title/author/subject/keywords)
  images       Extract embedded raster images
  compress     Rewrite with stream compression + linearise (pikepdf)
  fields       List AcroForm form fields
  fill         Fill AcroForm fields from a JSON mapping

Page ranges use 1-based, inclusive syntax:  "1-3,5,8-10"  or  "all".

Exit codes: 0 ok, 1 usage/runtime error, 2 missing dependency.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# --------------------------------------------------------------------------- #
# dependency helpers
# --------------------------------------------------------------------------- #
def _need(module: str, pip_name: str | None = None):
    """Import a module or exit(2) with an actionable install hint."""
    pip_name = pip_name or module
    try:
        return __import__(module)
    except ImportError:
        sys.stderr.write(
            f"error: '{module}' is required for this operation.\n"
            f"       install it with:  pip install {pip_name}\n"
        )
        sys.exit(2)


def _parse_ranges(spec: str, n_pages: int) -> list[int]:
    """'1-3,5' + n_pages -> [0,1,2,4] (0-based). 'all' -> every page."""
    spec = (spec or "all").strip().lower()
    if spec == "all":
        return list(range(n_pages))
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a), int(b)
        else:
            start = end = int(part)
        if start < 1 or end > n_pages or start > end:
            raise ValueError(
                f"page range '{part}' out of bounds (document has {n_pages} pages)"
            )
        out.extend(range(start - 1, end))  # to 0-based, inclusive
    return out


def _open_reader(path: str, password: str | None = None):
    """Open a PdfReader, transparently decrypting if a password is supplied."""
    pypdf = _need("pypdf")
    reader = pypdf.PdfReader(path)
    if reader.is_encrypted:
        if password is None:
            sys.stderr.write(
                f"error: '{path}' is encrypted. Re-run with --password.\n"
            )
            sys.exit(1)
        if reader.decrypt(password) == 0:
            sys.stderr.write("error: wrong password.\n")
            sys.exit(1)
    return reader


def _validate_input(path: str) -> None:
    p = Path(path)
    if not p.is_file():
        sys.stderr.write(f"error: input file not found: {path}\n")
        sys.exit(1)


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def cmd_info(args):
    # info never hard-fails on encryption: it reports what it can without a
    # password (encrypted flag + size), and full metadata once unlocked.
    _validate_input(args.input)
    pypdf = _need("pypdf")
    reader = pypdf.PdfReader(args.input)
    encrypted = reader.is_encrypted
    unlocked = True
    if encrypted:
        unlocked = reader.decrypt(args.password or "") != 0  # empty pw often works
    info = {
        "file": args.input,
        "encrypted": encrypted,
        "size_kb": round(Path(args.input).stat().st_size / 1024, 1),
    }
    if unlocked:
        md = reader.metadata or {}
        info.update({
            "pages": len(reader.pages),
            "title": md.get("/Title"),
            "author": md.get("/Author"),
            "subject": md.get("/Subject"),
            "creator": md.get("/Creator"),
            "producer": md.get("/Producer"),
        })
    else:
        info["pages"] = None
        info["note"] = "locked; supply --password for page count and metadata"
    print(json.dumps(info, indent=2, default=str))


def cmd_merge(args):
    pypdf = _need("pypdf")
    writer = pypdf.PdfWriter()
    for f in args.inputs:
        _validate_input(f)
        writer.append(_open_reader(f, args.password))
    _write(writer, args.output)
    print(f"OK: merged {len(args.inputs)} files -> {args.output}")


def cmd_split(args):
    _validate_input(args.input)
    pypdf = _need("pypdf")
    reader = _open_reader(args.input, args.password)
    n = len(reader.pages)
    stem = Path(args.input).stem
    outdir = Path(args.outdir or ".")
    outdir.mkdir(parents=True, exist_ok=True)
    chunk = max(1, args.chunk)
    written = []
    for start in range(0, n, chunk):
        writer = pypdf.PdfWriter()
        for i in range(start, min(start + chunk, n)):
            writer.add_page(reader.pages[i])
        end = min(start + chunk, n)
        label = f"{start + 1}" if chunk == 1 else f"{start + 1}-{end}"
        out = outdir / f"{stem}_p{label}.pdf"
        _write(writer, str(out))
        written.append(str(out))
    print(f"OK: wrote {len(written)} file(s) to {outdir}/")


def cmd_pages(args):
    _validate_input(args.input)
    pypdf = _need("pypdf")
    reader = _open_reader(args.input, args.password)
    idxs = _parse_ranges(args.range, len(reader.pages))
    writer = pypdf.PdfWriter()
    for i in idxs:
        writer.add_page(reader.pages[i])
    _write(writer, args.output)
    print(f"OK: extracted {len(idxs)} page(s) -> {args.output}")


def cmd_rotate(args):
    _validate_input(args.input)
    pypdf = _need("pypdf")
    reader = _open_reader(args.input, args.password)
    idxs = set(_parse_ranges(args.range, len(reader.pages)))
    writer = pypdf.PdfWriter()
    for i, page in enumerate(reader.pages):
        if i in idxs:
            page.rotate(args.degrees)
        writer.add_page(page)
    _write(writer, args.output)
    print(f"OK: rotated {len(idxs)} page(s) by {args.degrees}° -> {args.output}")


def cmd_watermark(args):
    _validate_input(args.input)
    _validate_input(args.stamp)
    pypdf = _need("pypdf")
    reader = _open_reader(args.input, args.password)
    stamp = _open_reader(args.stamp, None).pages[0]
    writer = pypdf.PdfWriter()
    for page in reader.pages:
        page.merge_page(stamp)  # overlays stamp on top of page content
        writer.add_page(page)
    _write(writer, args.output)
    print(f"OK: watermarked -> {args.output}")


def cmd_encrypt(args):
    _validate_input(args.input)
    pypdf = _need("pypdf")
    reader = _open_reader(args.input, args.password)
    writer = pypdf.PdfWriter()
    writer.append(reader)
    owner = args.owner_password or args.user_password
    writer.encrypt(
        user_password=args.user_password,
        owner_password=owner,
        algorithm="AES-256",
    )
    _write(writer, args.output)
    print(f"OK: encrypted (AES-256) -> {args.output}")


def cmd_decrypt(args):
    _validate_input(args.input)
    pypdf = _need("pypdf")
    reader = _open_reader(args.input, args.password)  # requires --password
    writer = pypdf.PdfWriter()
    writer.append(reader)
    _write(writer, args.output)
    print(f"OK: decrypted -> {args.output}")


def cmd_meta(args):
    _validate_input(args.input)
    pypdf = _need("pypdf")
    reader = _open_reader(args.input, args.password)
    if not args.set:
        print(json.dumps({k: str(v) for k, v in (reader.metadata or {}).items()},
                         indent=2))
        return
    writer = pypdf.PdfWriter()
    writer.append(reader)
    updates = {}
    for pair in args.set:
        if "=" not in pair:
            sys.stderr.write(f"error: --set expects key=value, got '{pair}'\n")
            sys.exit(1)
        k, v = pair.split("=", 1)
        key = k if k.startswith("/") else "/" + k[:1].upper() + k[1:]
        updates[key] = v
    writer.add_metadata(updates)
    _write(writer, args.output or args.input)
    print(f"OK: metadata updated -> {args.output or args.input}")


def cmd_images(args):
    _validate_input(args.input)
    reader = _open_reader(args.input, args.password)
    outdir = Path(args.outdir or "images")
    outdir.mkdir(parents=True, exist_ok=True)
    count = 0
    for pno, page in enumerate(reader.pages, start=1):
        for img in page.images:  # pypdf ImageFile objects
            name = f"p{pno}_{Path(img.name).name}"
            (outdir / name).write_bytes(img.data)
            count += 1
    print(f"OK: extracted {count} image(s) -> {outdir}/")


def cmd_compress(args):
    _validate_input(args.input)
    pike = _need("pikepdf")
    with pike.open(args.input, password=args.password or "") as pdf:
        pdf.save(
            args.output,
            compress_streams=True,
            object_stream_mode=pike.ObjectStreamMode.generate,
            linearize=True,
        )
    before = Path(args.input).stat().st_size
    after = Path(args.output).stat().st_size
    pct = (1 - after / before) * 100 if before else 0
    print(f"OK: {before // 1024} KB -> {after // 1024} KB ({pct:.0f}% smaller) "
          f"-> {args.output}")


def cmd_fields(args):
    _validate_input(args.input)
    reader = _open_reader(args.input, args.password)
    fields = reader.get_fields()
    if not fields:
        print("no AcroForm fields found")
        return
    out = {name: {"type": str(f.get("/FT")), "value": str(f.get("/V"))}
           for name, f in fields.items()}
    print(json.dumps(out, indent=2))


def cmd_fill(args):
    _validate_input(args.input)
    _validate_input(args.data)
    pypdf = _need("pypdf")
    reader = _open_reader(args.input, args.password)
    values = json.loads(Path(args.data).read_text())
    writer = pypdf.PdfWriter()
    writer.append(reader)
    for page in writer.pages:
        writer.update_page_form_field_values(page, values, auto_regenerate=False)
    _write(writer, args.output)
    print(f"OK: filled {len(values)} field(s) -> {args.output}")


def _write(writer, output: str) -> None:
    out = Path(output)
    if out.parent and not out.parent.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as fh:
        writer.write(fh)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pdf_ops.py", description="Swiss-army knife for manipulating PDFs."
    )
    p.add_argument("--password", help="password for an encrypted input")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("info", help="show page count / metadata / encryption")
    s.add_argument("input")
    s.set_defaults(func=cmd_info)

    s = sub.add_parser("merge", help="concatenate PDFs")
    s.add_argument("inputs", nargs="+")
    s.add_argument("-o", "--output", required=True)
    s.set_defaults(func=cmd_merge)

    s = sub.add_parser("split", help="split into per-page or fixed chunks")
    s.add_argument("input")
    s.add_argument("--outdir")
    s.add_argument("--chunk", type=int, default=1, help="pages per file (default 1)")
    s.set_defaults(func=cmd_split)

    s = sub.add_parser("pages", help="extract/reorder a page selection")
    s.add_argument("input")
    s.add_argument("range", help='e.g. "1-3,5,8-10"')
    s.add_argument("-o", "--output", required=True)
    s.set_defaults(func=cmd_pages)

    s = sub.add_parser("rotate", help="rotate pages")
    s.add_argument("input")
    s.add_argument("-o", "--output", required=True)
    s.add_argument("--degrees", type=int, choices=[90, 180, 270], default=90)
    s.add_argument("--range", default="all")
    s.set_defaults(func=cmd_rotate)

    s = sub.add_parser("watermark", help="stamp one PDF over another")
    s.add_argument("input")
    s.add_argument("--stamp", required=True, help="single-page PDF to overlay")
    s.add_argument("-o", "--output", required=True)
    s.set_defaults(func=cmd_watermark)

    s = sub.add_parser("encrypt", help="password-protect (AES-256)")
    s.add_argument("input")
    s.add_argument("-o", "--output", required=True)
    s.add_argument("--user-password", required=True)
    s.add_argument("--owner-password")
    s.set_defaults(func=cmd_encrypt)

    s = sub.add_parser("decrypt", help="remove password (needs --password)")
    s.add_argument("input")
    s.add_argument("-o", "--output", required=True)
    s.set_defaults(func=cmd_decrypt)

    s = sub.add_parser("meta", help="get or set metadata")
    s.add_argument("input")
    s.add_argument("--set", nargs="*", help='key=value, e.g. Title="My Doc"')
    s.add_argument("-o", "--output", help="default: overwrite input")
    s.set_defaults(func=cmd_meta)

    s = sub.add_parser("images", help="extract embedded raster images")
    s.add_argument("input")
    s.add_argument("--outdir")
    s.set_defaults(func=cmd_images)

    s = sub.add_parser("compress", help="rewrite with compression + linearise")
    s.add_argument("input")
    s.add_argument("-o", "--output", required=True)
    s.set_defaults(func=cmd_compress)

    s = sub.add_parser("fields", help="list AcroForm form fields")
    s.add_argument("input")
    s.set_defaults(func=cmd_fields)

    s = sub.add_parser("fill", help="fill form fields from JSON")
    s.add_argument("input")
    s.add_argument("--data", required=True, help="JSON file: {field: value}")
    s.add_argument("-o", "--output", required=True)
    s.set_defaults(func=cmd_fill)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
        return 0
    except ValueError as e:
        sys.stderr.write(f"error: {e}\n")
        return 1
    except Exception as e:  # noqa: BLE001 - surface a clean message, not a traceback
        sys.stderr.write(f"error: {type(e).__name__}: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
