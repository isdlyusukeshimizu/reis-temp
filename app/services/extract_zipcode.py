# app/services/extract_zipcode.py
'''
このスクリプトは、不動産登記PDFから最新の「相続」または「遺贈」による所有権移転情報を抽出し、
所有者の住所から郵便番号を自動的に取得して表示する処理を行う。
'''

import pandas as pd
import re
import unicodedata
import os
from typing import Dict

# 環境変数からKEN_ALL.CSVのパスを取得
ken_all_path = os.getenv("KEN_ALL_CSV_PATH", "./data/KEN_ALL.CSV")

# 日本郵便KEN_ALL.CSV読み込み
def load_postal_code_data():
    df = pd.read_csv(
        ken_all_path,
        encoding="shift_jis",
        header=None
    )
    df.columns = [
        "地域コード", "変更フラグ", "郵便番号", 
        "都道府県カナ", "市区町村カナ", "町域カナ",
        "都道府県", "市区町村", "町域", 
        "フラグ1", "フラグ2", "フラグ3", 
        "フラグ4", "フラグ5", "フラグ6"
    ]
    return df

# 漢数字をアラビア数字に変換するマップ
KANJI_NUM_MAP = {
    '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
    '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'
}

def kanji_to_arabic(text):
    for kanji, num in KANJI_NUM_MAP.items():
        text = text.replace(kanji + '丁目', num + '丁目')
    return text

def get_zipcode(address: str) -> str:
    """
    住所文字列から郵便番号を検索して返す
    """
    df = load_postal_code_data()
    
    address = unicodedata.normalize("NFKC", address)
    address = kanji_to_arabic(address)
    address = re.sub(r"字", "", address)

    m = re.match(r"(..[都道府県])(.+?[市区町村])(.+)", address)
    if not m:
        raise ValueError("住所の形式が不正です: " + address)
    pref, city, rest = m.groups()
    rest = rest.split()[0]
    town = re.split(r"[\d\-－ー0-9]", rest)[0]

    result = df[
        (df["都道府県"] == pref) &
        (df["市区町村"] == city) &
        (df["町域"] == town)
    ]
    if result.empty:
        result = df[
            (df["都道府県"] == pref) &
            (df["市区町村"] == city) &
            (df["町域"].str.contains(town))
        ]
    if not result.empty:
        zip7 = str(result.iloc[0]["郵便番号"]).zfill(7)
        return f"{zip7[:3]}-{zip7[3:]}"
    return "該当なし"