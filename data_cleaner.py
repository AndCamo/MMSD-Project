import pandas as pd

def clean_excel_data(input_file, output_file):
    df = pd.read_excel(input_file)

    # Ensure the first 4 columns are kept intact
    cleaned_df = df.iloc[:, :4].copy()

    # Extract the 5th column
    fifth_column = df.iloc[:, 4]

    # Identify unique features in the 5th column
    unique_features = set()
    for entry in fifth_column.dropna():
        features = [item.strip() for item in re.split(r'[;,\s]+', str(entry)) if item]
        unique_features.update(features)

    # Create a new DataFrame to store organized data
    for feature in sorted(unique_features):
        cleaned_df[feature] = fifth_column.apply(lambda x: 1 if pd.notna(x) and feature in str(x) else 0)

    cleaned_df.to_excel(output_file, index=False)

    print(f"Data cleaning complete. Cleaned file saved as: {output_file}")

if __name__ == "__main__":
    import re
    import os

    input_file = r"Data\Raw Data\Elenco Aule - Unito.it.xlsx"
    output_file = r"Data\Elenco Aule - Clean.xlsx"


    if os.path.exists(input_file):
        clean_excel_data(input_file, output_file)
    else:
        print(f"Input file '{input_file}' not found.")
