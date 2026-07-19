# Personal order tracker

`Student_Order_Tracker.xlsx` — a workbook for tracking who's ordered this project,
what they paid, and where each delivery stands.

## Sheets

**Orders Tracker** — one row per student. Yellow cells are for you to fill in;
gray cells (Balance Due, Payment Status) calculate automatically from what you
enter in Price Charged and Amount Paid. Summary totals (orders, revenue, collected,
pending) are at the top and update automatically as you add rows.

**Delivery Checklist** — the same 13 steps every order needs, from confirming
price through to the post-viva follow-up. Mark each "Done?" column as you go;
use Notes for anything specific to that order.

## Regenerating

If you want to tweak columns, colors, or the checklist steps, edit
`build_tracker.py` and rerun:
```bash
pip install openpyxl --break-system-packages   # if not already installed
python3 build_tracker.py
```
This will overwrite `Student_Order_Tracker.xlsx` — copy your existing data out
first if you've already been using it, since regenerating starts from the
example row again.
