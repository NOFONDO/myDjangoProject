#!/usr/bin/env python
# ============================================================
# AgriConnect — Django Management Entry Point
# backend/manage.py
# ============================================================

import os
import sys


def main():
    # Use development settings by default.
    # In production, set: DJANGO_SETTINGS_MODULE=config.settings.production
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'config.settings.development'
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and that "
            "your virtual environment is activated."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
