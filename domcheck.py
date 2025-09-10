import asyncio
from playwright.async_api import async_playwright
import os 

async def main():
    file_path = "as"

    if not os.path.exists(file_path):
        print(f"오류: '{file_path}' 파일이 같은 디렉터리에 존재하지 않습니다.")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
    except Exception as e:
        print(f"오류: 파일 '{file_path}'를 읽는 중 문제가 발생했습니다. ({e})")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.set_content(file_content)
        print("...")
        input() 
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())