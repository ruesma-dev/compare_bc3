# main.py
from pathlib import Path
import argparse
import sys

from config import settings
from interface_adapters.controllers.compare_controller import run as run_compare


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="compare-bc3",
        description="Compara dos presupuestos BC3, imprime sus DataFrames, guarda CSV y detecta cambios en 'descripcion_larga'",
    )
    p.add_argument(
        "old",
        nargs="?",
        default=settings.OLD_BC3_DEFAULT,
        type=Path,
        help="BC3 original",
    )
    p.add_argument(
        "new",
        nargs="?",
        default=settings.NEW_BC3_DEFAULT,
        type=Path,
        help="BC3 revisado",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        run_compare(args.old, args.new)
    except FileNotFoundError as exc:
        print(f"[ERROR] No se encontró el fichero: {exc.filename}", file=sys.stderr)
        sys.exit(2)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
