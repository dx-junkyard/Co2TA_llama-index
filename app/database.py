import sqlite3
import os
import pandas as pd
import PyPDF2

DB_PATH = 'application_forms.db'

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

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
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
        cursor.execute('INSERT OR IGNORE INTO forms (id, name, markdown) VALUES (?, ?, ?)',
                       (i, pdf_file, markdown_content))

    conn.commit()
    conn.close()

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