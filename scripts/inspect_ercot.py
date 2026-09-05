from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw"

supported_extensions = {".xlsx", ".xls", ".csv"}

available_files = [
    path
    for path in RAW_DATA_DIRECTORY.iterdir()
    if path.is_file() and path.suffix.lower() in supported_extensions
]

ercot_candidates = [
    path
    for path in available_files
    if "ercot" in path.name.lower()
    or "damlzhbspp" in path.name.lower()
]

print("Available raw data files:")

for path in available_files:
    print(f"- {path.name}")

if not ercot_candidates:
    raise FileNotFoundError(
        "No ERCOT workbook was found. "
        "Make sure its filename contains 'ercot' or 'DAMLZHBSPP'."
    )

ercot_path = ercot_candidates[0]

print(f"\nInspecting: {ercot_path.name}")

if ercot_path.suffix.lower() in {".xlsx", ".xls"}:
    workbook = pd.ExcelFile(ercot_path)

    print("\nWorkbook sheet names:")

    for sheet_name in workbook.sheet_names:
        print(f"- {sheet_name}")

    first_sheet = workbook.sheet_names[0]

    print(f"\nFirst eight rows of sheet: {first_sheet}")
    print("(Read without assuming which row contains the headers.)\n")

    preview = pd.read_excel(
        ercot_path,
        sheet_name=first_sheet,
        header=None,
        nrows=8,
    )

    print(preview.to_string(index=False, header=False))

else:
    print("\nFirst eight rows of CSV:\n")

    preview = pd.read_csv(
        ercot_path,
        header=None,
        nrows=8,
    )

    print(preview.to_string(index=False, header=False))