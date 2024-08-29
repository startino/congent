import os
import pandas as pd

def parquet_to_csv(input_dir: str):
    for file in os.listdir(input_dir):
        if file.endswith('.parquet'):
            input_file = os.path.join(input_dir, file)
            output_file = os.path.join(input_dir, file.replace('.parquet', '.csv'))
            df = pd.read_parquet(input_file)
            df.to_csv(output_file, index=False)

if __name__ == '__main__':
    parquet_to_csv(r'C:\Users\antop\Documents\Development\congent\ragtest\output\20240829-012312\artifacts')