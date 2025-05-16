# app/services/merge_data.py
import pandas as pd

def merge_data(owner_info_path: str, zipcode_info_path: str, output_path: str):
    """
    所有者情報CSVと郵便番号CSVを結合して、最終的なCSVを出力する
    """
    df_owner = pd.read_csv(owner_info_path)
    df_zip   = pd.read_csv(zipcode_info_path)

    df_merged = pd.merge(
        df_owner,
        df_zip,
        on='所有者住所',
        how='left'
    )

    df_merged.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 結合完了: {output_path}")
    
    return df_merged