# app/services/auto_mode.py
'''
このスクリプトからextract_info_from_pdf.pyを呼び出し、
OCR済みテキストから抽出した住所リストを取得し、
そのリストを使用して登記情報取得サイトに一度ログインし、
各住所の登記PDFを自動ダウンロードする。

営業時間外や重複住所は除外され、全処理後に自動でログアウトする。
'''

from app.services.extract_info import get_cleaned_addresses
from datetime import datetime, time as dtime
import holidays
import time
from playwright.sync_api import Playwright, sync_playwright
from pathlib import Path
import os
from typing import List

JP_HOLIDAYS = holidays.Japan()

def is_within_service_hours(now: datetime) -> bool:
    # 年末年始は終日NG
    if datetime(now.year, 12, 29) <= now <= datetime(now.year + 1, 1, 3):
        return False
    
    is_holiday_or_weekend = now.weekday() >= 5 or now.date() in JP_HOLIDAYS
    
    if is_holiday_or_weekend:
        return dtime(8, 30) <= now.time() < dtime(18, 0)
    else:
        return dtime(8, 30) <= now.time() < dtime(23, 0)

def download_owner_info(page, address: str) -> str:
    now = datetime.now()
    if not is_within_service_hours(now):
        print(f"⚠️ 登記情報取得不可時間帯のためスキップ: {now.strftime('%Y-%m-%d %H:%M')} / {address}")
        return None

    page.get_by_role("gridcell", name="不動産登記情報取得").locator("span").click()
    time.sleep(1)

    frame = page.frame(name="touki_search-iframe-frame")
    frame.locator("#check_direct_enable-inputEl").click()
    frame.locator("#direct_txt-inputEl").fill(address)
    time.sleep(1)
    frame.get_by_role("button", name="直接入力取込").click()
    frame.get_by_role("button", name="確定").click()
    frame.locator("img").click()
    time.sleep(1)

    frame.get_by_role("button", name="登記情報取得（オンライン）").click()
    time.sleep(1)
    frame.get_by_role("button", name="はい").click()
    time.sleep(1)
    frame.locator("#button-1005-btnEl").click()
    time.sleep(1)

    frame2 = page.frame(name="mypage_list-iframe-frame")
    frame2.locator("#ext-gen1323").get_by_role("button", name="PDF").click()

    with page.expect_download() as download_info:
        frame2.get_by_role("button", name="はい").click()
    download = download_info.value

    # 環境変数から保存ディレクトリを取得するか、デフォルト値を使用
    save_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / f"{address.replace(' ', '_').replace('/', '-')}.pdf"
    download.save_as(str(save_path))
    print(f"✅ Downloaded PDF for: {address}")
    return str(save_path)


def login_and_download_all(playwright, address_list):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    page.goto("https://xn--udk1b673pynnijsb3h8izqr1a.com/login.php")
    time.sleep(1)

    # 環境変数から認証情報を取得
    username = os.getenv("REGISTRY_USERNAME")
    password = os.getenv("REGISTRY_PASSWORD")

    page.locator("input[name=\"id\"]").fill(username)
    page.locator("input[name=\"id\"]").press("Tab")
    time.sleep(1)
    page.locator("input[name=\"pass\"]").fill(password)
    time.sleep(1)
    page.get_by_role("button", name="利用規約に同意してログイン").click()
    time.sleep(1)

    saved_paths = []
    for idx, address in enumerate(address_list):
        print(f"\n▶️ ({idx+1}/{len(address_list)}) 処理開始: {address}")
        try:
            path = download_owner_info(page, address)
            if path:
                saved_paths.append(path)
        except Exception as e:
            print(f"❌ エラー発生: {address}\n{e}")
        print("⏳ 次の住所まで10秒待機中...\n")
        time.sleep(10)

    # ログアウト処理
    context.close()
    browser.close()
    
    return saved_paths

def run_auto_mode(pdf_path) -> List[str]:
    cleaned_addresses = get_cleaned_addresses(pdf_path)
    address_list = sorted(set(cleaned_addresses))

    saved_paths = []

    with sync_playwright() as playwright:
        saved_paths = login_and_download_all(playwright, address_list)

    return saved_paths