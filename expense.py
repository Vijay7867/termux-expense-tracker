#!/usr/bin/env python3
"""Offline INR expense ledger. Python 3.10+, standard library only."""
import argparse
import csv
import os
import sqlite3
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


def money(value):
    try:
        amount = Decimal(value)
        if not amount.is_finite() or amount <= 0 or amount > Decimal('1000000000'):
            raise ValueError
        if amount * 100 != (amount * 100).to_integral_value():
            raise ValueError
        return int(amount * 100)
    except (ValueError, InvalidOperation):
        raise argparse.ArgumentTypeError('Use a positive INR amount with at most two decimals.')


def day(value):
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError('Use a valid YYYY-MM-DD date.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', type=Path, default=Path.home()/'.local/share/termux-expenses/expenses.sqlite3')
    sub = p.add_subparsers(dest='cmd', required=True)
    add = sub.add_parser('add')
    add.add_argument('amount', type=money)
    add.add_argument('category')
    add.add_argument('--note', default='')
    add.add_argument('--date', type=day, default=date.today().isoformat())
    show = sub.add_parser('list')
    show.add_argument('--limit', type=int, default=30)
    sub.add_parser('summary')
    export = sub.add_parser('export')
    export.add_argument('file', type=Path)
    a = p.parse_args()
    if a.cmd == 'add' and not a.category.strip():
        p.error('Category cannot be empty.')
    if a.cmd == 'list' and not 1 <= a.limit <= 10000:
        p.error('Limit must be 1–10000.')
    a.db.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with sqlite3.connect(a.db) as c:
        os.chmod(a.db, 0o600)
        c.execute('CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, day TEXT NOT NULL, paise INTEGER NOT NULL, category TEXT NOT NULL, note TEXT NOT NULL)')
        if a.cmd == 'add':
            row = c.execute('INSERT INTO expenses(day,paise,category,note) VALUES (?,?,?,?)', (a.date,a.amount,a.category.strip(),a.note))
            print(f'Saved expense #{row.lastrowid}: INR {a.amount/100:.2f}')
        elif a.cmd == 'list':
            for ident,d,paise,cat,note in c.execute('SELECT * FROM expenses ORDER BY day DESC,id DESC LIMIT ?', (a.limit,)):
                print(f'{ident}\t{d}\tINR {paise/100:.2f}\t{cat}\t{note!r}')
        elif a.cmd == 'summary':
            total = 0
            for cat,paise in c.execute('SELECT category,SUM(paise) FROM expenses GROUP BY category ORDER BY SUM(paise) DESC'):
                total += paise
                print(f'{cat}: INR {paise/100:.2f}')
            print(f'Total: INR {total/100:.2f}')
        else:
            # Exclusive create avoids overwriting an existing export.
            with a.file.open('x', newline='', encoding='utf-8') as out:
                os.chmod(a.file, 0o600)
                w = csv.writer(out)
                w.writerow(['id','date','amount_inr','category','note'])
                for ident,d,paise,cat,note in c.execute('SELECT * FROM expenses ORDER BY day,id'):
                    # Prefix formula-like text before opening in a spreadsheet.
                    safe = lambda text: "'"+text if text.lstrip().startswith(('=','+','-','@')) else text
                    w.writerow([ident,d,f'{paise/100:.2f}',safe(cat),safe(note)])
            print(f'Exported: {a.file}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, sqlite3.Error) as exc:
        raise SystemExit(f'Error: {exc}')
