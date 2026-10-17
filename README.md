# Susu Group Tracker

A small Python command-line program for managing one rotating savings (susu) group.

## Requirements

- Python 3.10 or newer
- No third-party packages required

## Run the program

Open a terminal in this folder and run:

```bash
python susu.py
```

Enter the fixed weekly contribution, then register members in the order they should receive the pot. Use the menu to record full or partial contributions, close a week, and view the report.

## Run automated tests

```bash
python -m unittest -v
```

The test suite covers partial payments, a week that cannot close, payout order, duplicate and unknown members, invalid payments, late member registration, and amounts with more than two decimal places.

## Example

For three members contributing GHS 50.00 each, the pot is GHS 150.00. If Ama and Kofi pay GHS 50.00 and Esi pays GHS 30.00, closing the week reports that Esi owes GHS 20.00 and does not issue a payout. Once Esi pays the remaining GHS 20.00, closing the week pays GHS 150.00 to Ama.

## Limitations

This version keeps data in memory, so records are lost when the program exits. See `NOTES.md` for assumptions and possible improvements.
