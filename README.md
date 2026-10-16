# Offline Expense Tracker

Record daily INR expenses, see category totals and export CSV. Amounts are stored as integer paise to avoid floating-point accumulation.

Built for Android + Termux; also runs on Linux with Python 3.10+. Uses only the Python standard library. No API key, pip package or paid service is needed. Installing Python/Git requires internet; normal tool operation is local.

## Install

```bash
pkg install python git -y
git clone https://github.com/Vijay7867/termux-expense-tracker.git
cd termux-expense-tracker
python expense.py --help
```

If using the delivered ZIP instead, extract it and open this project directory directly.

## Examples

```bash
python expense.py add 45.50 food --note "Lunch"
python expense.py add 20 travel --date 2026-10-17
python expense.py list
python expense.py summary
python expense.py export expenses.csv
```

## Data and limitations

Default database: `~/.local/share/termux-expenses/expenses.sqlite3`. Use `python expense.py --db /path/to/file.sqlite3 summary` to select another database. CSV export refuses to overwrite existing files and prefixes formula-like text. This is a manually entered ledger, without bank sync, automatic currency conversion, editing or refunds.

Local data is not encrypted. Keep personal records out of Git. Database tools create their data outside the repository by default. For backups, copy the database after commands have exited; protect exported CSV files yourself. Android shared storage may not enforce Unix file modes.

## Verify

```bash
python -m unittest discover -s tests -v
```

Automated tests run in temporary directories and do not touch real phone data. Cloud Python tests are not a substitute for testing on your Android device.

## Contributing

Open an issue with the command, expected/actual output, Python version and platform; remove personal records. Small PRs should include a relevant test. Current scope is a small local CLI, not a cloud service.

## Licence

No project licence has been selected yet. Public visibility alone does not grant reuse rights; contact the maintainer before redistribution.
