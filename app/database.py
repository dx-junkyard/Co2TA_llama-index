import sqlite3
import os
import pandas as pd
import PyPDF2
from openai import AzureOpenAI
import tiktoken


DB_PATH = 'application_forms.db'
MAX_TOKENS=15000

client = AzureOpenAI(
  api_key = os.getenv("AZURE_OPENAI_KEY"),  
  api_version = "2023-03-15-preview",
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
)

def pdf_to_markdown(pdf_file_path):
    # PDFファイルを開いてテキストを抽出
    with open(pdf_file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        # 全てのページからテキストを取得
        for page in reader.pages:
            text += page.extract_text()
    # 簡単にMarkdownに変換
    markdown_text = f'# {os.path.basename(pdf_file_path)}\n\n{text}'
    return markdown_text

def split_text_into_chunks(text, max_tokens=MAX_TOKENS):
    """
    テキストをトークン数に基づいてチャンクに分割します。
    """
    encoder = tiktoken.get_encoding("cl100k_base")  # 使用するエンコーディングに応じて変更
    tokens = encoder.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk = encoder.decode(tokens[i:i + max_tokens])
        chunks.append(chunk)
    return chunks

def process_markdown_with_llm(markdown_text):
    """
    Markdownテキストをチャンクに分割し、LLMで整形します。
    """
    chunks = split_text_into_chunks(markdown_text, max_tokens=MAX_TOKENS)
    formatted_chunks = []

    for chunk in chunks:
        formatted = format_markdown_with_llm(chunk)
        # print("整形前...........")
        # print(chunk)
        # print("整形後...........")
        # print(formatted) 
        formatted_chunks.append(formatted)

    # log_file='output.log'
    # with open(log_file, 'a', encoding='utf-8') as f:
    #     for chunk in chunks:
    #         formatted = format_markdown_with_llm(chunk)
            
    #         # ファイルに直接書き込む
    #         f.write("整形前...........\n")
    #         f.write(f"{chunk}\n")
    #         f.write("整形後...........\n")
    #         f.write(f"{formatted}\n\n")  # 空行を追加
            # formatted_chunks.append(formatted)

    return formatted_chunks

def format_markdown_with_llm(chunk):
    """
    LLMを使用してMarkdownを整形します。
    """
    prompt = f"""以下の条件に従ってmarkdownを整形してください
    - 勝手に要約せずできるだけ文章をそのまま使用してください
    - 文章の順番などは文脈が通るように調整してください

{chunk}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはMarkdownの整形アシスタントです。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=MAX_TOKENS,
        temperature=0.3
    )
    formatted_markdown = response.choices[0].message.content.strip()
    return formatted_markdown

def initialize_database():
    print("データベースを更新中...")
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()

    # テーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS forms (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        markdown TEXT NOT NULL
    )
    ''')

    # PDFファイルがあるディレクトリを指定
    pdf_dir = './pdf'

    # フォルダ内の全てのPDFファイルを処理
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]

    cursor.execute('DELETE FROM forms')

    # データベースに格納する
    for i, pdf_file in enumerate(pdf_files, start=1):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        markdown_content = pdf_to_markdown(pdf_path)
        if not markdown_content:
                logger.warning(f"Markdownコンテンツが空です: {pdf_file}")
                continue
        formatted_chunks = process_markdown_with_llm(markdown_content)

        # チャンクを合成する
        combined_markdown = "\n\n".join(formatted_chunks)
        cursor.execute('INSERT OR IGNORE INTO forms (id, name, markdown) VALUES (?, ?, ?)',
                        (i, pdf_file, combined_markdown))
    conn.commit()
    conn.close()
    print("データベースを更新が完了しました")

def get_markdown_by_id(form_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT markdown FROM forms WHERE id=?", (form_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None