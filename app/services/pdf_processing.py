# app/services/pdf_processing.py
import pandas as pd
from openai import OpenAI
from pathlib import Path
import os
import re
from typing import List, Dict
from datetime import datetime

from app.services.extract_info import get_cleaned_addresses
from app.services.auto_mode import run_auto_mode
from app.services.extract_zipcode import get_zipcode
from app.services.merge_data import merge_data

def extract_owner_info(pdf_paths: List[str]) -> pd.DataFrame:
    """
    ダウンロード済みの所有者情報PDFを解析し、氏名・所有者住所・不動産所在地を抽出してDataFrameを返す
    """
    # 環境変数からAPIキーを取得
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    records = []

    for pdf_path in pdf_paths:
        # PDFをテキストに変換
        with open(pdf_path, 'rb') as f:
            response = client.files.create(
                file=f,
                purpose="assistants"
            )
            file_id = response.id
        
        # GPTにプロンプト送信
        prompt = f"""
以下は登記簿のOCRテキストです。この中から以下の情報を抽出してください。

1. 「原因」が「相続」または「遺贈」である所有権移転に関して、**最も新しい**氏名とその所有者住所（共有者の住所）。
2. その相続によって取得された不動産の所在地（住所）。

- 出力形式:
  氏名: ○○○○
  所有者住所: ○○県○○市○○…
  不動産所在地: ○○県○○市○○…
"""
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that extracts information from real estate registry documents."},
            {"role": "user", "content": prompt}
        ]
        
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.0,
            file_ids=[file_id]
        )
        
        output = completion.choices[0].message.content.strip()
        
        # ファイルを削除
        client.files.delete(file_id)

        # 正規表現で抽出
        name_m = re.search(r"氏名:\s*(.+)", output)
        addr_m = re.search(r"所有者住所:\s*(.+)", output)
        prop_m = re.search(r"不動産所在地:\s*(.+)", output)
        if name_m and addr_m and prop_m:
            records.append({
                "PDFファイル": pdf_path,
                "氏名": name_m.group(1).strip(),
                "所有者住所": addr_m.group(1).strip(),
                "不動産所在地": prop_m.group(1).strip()
            })

    return pd.DataFrame(records)

def run_pipeline(ledger_pdf: str, task_id: str = None) -> Dict:
    """
    不動産相続情報パイプラインを実行する
    """
    # 出力ディレクトリの取得
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    Path(output_dir).mkdir(exist_ok=True)
    
    # タスクIDがある場合はサブディレクトリを作成
    if task_id:
        output_dir = os.path.join(output_dir, task_id)
        Path(output_dir).mkdir(exist_ok=True)
    
    # 出力ファイルパスの設定
    owner_out = f"owner_info_{task_id}.csv" if task_id else "owner_info.csv"
    zipcode_out = f"zipcode_info_{task_id}.csv" if task_id else "zipcode_info.csv"
    final_out = f"final_output_{task_id}.csv" if task_id else "final_output.csv"
    
    owner_out_path = os.path.join(output_dir, owner_out)
    zipcode_out_path = os.path.join(output_dir, zipcode_out)
    final_out_path = os.path.join(output_dir, final_out)
    
    # ステップ1: 地番抽出 & PDFダウンロード
    print("▶️ 地番抽出とPDFダウンロード開始")
    pdf_paths = run_auto_mode(ledger_pdf)
    print(f"✅ PDFダウンロード完了: {len(pdf_paths)} 件")

    # ステップ2: 所有者情報抽出
    print("▶️ 所有者情報抽出開始")
    df_owner = extract_owner_info(pdf_paths)
    df_owner.to_csv(owner_out_path, index=False, encoding='utf-8-sig')
    print(f"✅ 所有者情報CSV出力: {owner_out_path}")

    # ステップ3: 郵便番号取得
    print("▶️ 郵便番号検索開始")
    zip_records = []
    for addr in df_owner['所有者住所'].unique():
        zipcode = get_zipcode(addr)
        zip_records.append({'所有者住所': addr, '郵便番号': zipcode})
    df_zip = pd.DataFrame(zip_records)
    df_zip.to_csv(zipcode_out_path, index=False, encoding='utf-8-sig')
    print(f"✅ 郵便番号CSV出力: {zipcode_out_path}")

    # ステップ4: CSV結合
    print("▶️ CSV結合開始")
    merge_data(owner_out_path, zipcode_out_path, final_out_path)
    print(f"✅ 最終CSV出力: {final_out_path}")
    
    return {
        "task_id": task_id,
        "pdf_count": len(pdf_paths),
        "owner_count": len(df_owner),
        "output_files": {
            "owner_info": owner_out_path,
            "zipcode_info": zipcode_out_path,
            "final_output": final_out_path
        }
    }