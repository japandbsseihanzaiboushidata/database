import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import csv
import datetime
import streamlit as st
import pandas as pd
import spacy
#subprocess.run([f"{sys.executable}", "-m","spacy","download","ja_core_news_md"])
import sqlite3
   
st.title("Japan_DBS_Seihanzai_Boushi_Dataset")
st.title("☆事件情報")
st.text("spacyと呼ばれる自然言語処理を利用し、ニュース記事から情報化しています。")
st.text("関係者氏名/記事タイトル/記事URL/記事内容/投稿時間")

# CSVファイルを読み込む# データフレームを表示
#df = pd.read_csv("dataset.csv")
#st.write(df)

# SQLite データベースファイルのパスを指定
db_file_path = "dataset.db"
# SQLite データベースファイルを読み込む
conn = sqlite3.connect(db_file_path)
# データベースからデータを読み込み# データフレームを表示
df = pd.read_sql(f"SELECT * FROM news_table", conn)
st.write(df)


# 検索窓を追加
search_term = st.text_input("事件情報から検索")
if search_term:
    # 検索処理を実行
    search_query = f"SELECT * FROM news_table WHERE Content LIKE ?"
    df = pd.read_sql_query(search_query, conn, params=('%'+search_term+'%',))
    st.write(df)
# データベースとの接続を閉じる
conn.close()

st.title("☆投稿方法")
# テキスト入力ウィジェットを使用して文字列を受け取る
input_text = st.text_input("YahooニュースのURLを入力してください。//news.yahoo.co.jp/articles/を含むURLです。")
st.text("spacyと呼ばれる自然言語処理を利用し、自動的に情報化され共有されます。")

if input_text:
    link = input_text
    
    # 記事本文のURLから記事本文のページ内容を取得する
    news_body = requests.get(link)
    # 取得した記事本文のページをBeautifulSoupで解析できるようにする
    news_soup = BeautifulSoup(news_body.text, "html.parser")
    # 記事本文のタイトルを取得する
    title = news_soup.title.text
    # 記事本文の本文を取得する
    content = news_soup.find(class_=re.compile("Direct")).text.replace('\n', '')
    # 現在の日時を取得する
    time = datetime.datetime.now()
    # DataFrameを作成する
    df = pd.DataFrame({"Title": [title], "URL": [link], "Content": [content],"Time":[time]})
    # 新しいCSVファイルにDataFrameを保存
    csv_file_path = "df_row_data.csv"
    df.to_csv(csv_file_path, index=False)
    # Load the Japanese language model
    nlp = spacy.load("ja_core_news_md")
    # Read the existing CSV file into a DataFrame
    existing_df = pd.read_csv("df_row_data.csv")
    # Process the article text and extract person names
    person_names = []
    with open('df_row_data.csv', 'r', encoding='UTF-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc = nlp(row["Content"])
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    person_names.append(ent.text)

    # Remove duplicate names
    person_names = list(set(person_names))
    # If person_names is empty, replace it with "Nothing"
    if not person_names:
        person_names = ["Nothing"]
    # Create a new DataFrame with the extracted person names
    new_df = pd.DataFrame({"Names": person_names})
    # Concatenate the two DataFrames along the columns axis
    concatenated_df = pd.concat([new_df, existing_df], axis=1)
    # Fill NaN values in the "Title", "URL", "Content", and "Time" columns with forward fill method
    concatenated_df["Title"] = concatenated_df["Title"].fillna(method='ffill')
    concatenated_df["URL"] = concatenated_df["URL"].fillna(method='ffill')
    concatenated_df["Content"] = concatenated_df["Content"].fillna(method='ffill')
    concatenated_df["Time"] = concatenated_df["Time"].fillna(method='ffill')
    # Save the concatenated DataFrame to a new CSV file
    concatenated_df.to_csv("df_data.csv",  index=False)
    df = pd.read_csv("df_data.csv")
    st.write(df)

    # Open the "df_data.csv" file and read its contents row by row
    #with open('df_data.csv', 'r', encoding='UTF-8') as f:
    #    reader = csv.reader(f)
        # Iterate over each row in the file
    #    for row in reader:
    #        # Append the row to the "data.csv" file
    #        with open('dataset.csv', 'a', newline='', encoding='utf-8') as csvfile:
    #            writer = csv.writer(csvfile)
    #            writer.writerow(row)


    # データベースに接続し、カーソルを作成する
    conn = sqlite3.connect('dataset.db')
    cursor = conn.cursor()
    # テーブルを作成するクエリ
    create_table_query = f"CREATE TABLE IF NOT EXISTS news_table (Name TEXT, Title TEXT, URL TEXT, Content TEXT, Time TEXT)"  
    # テーブルを作成する
    cursor.execute(create_table_query)
    # CSVファイルを開いて内容を1行ずつ読み込んでテーブルに挿入する
    with open('df_data.csv', 'r', encoding='UTF-8') as f:
        reader = csv.reader(f)
        for row in reader:
            # 各行をテーブルに挿入するクエリ
            insert_query = f"INSERT INTO news_table(Name,Title, URL,Content,Time) VALUES (?, ?, ?, ?, ?)"  
            cursor.execute(insert_query, row)

    # 変更を保存
    conn.commit()

    # CSVファイルを読み込む
    #df = pd.read_csv('dataset.csv')
    # 重複する行を削除する
    #df = df.drop_duplicates()
    # 時間列がある場合、その列を指定して降順で並び替える
    #df = df.sort_values(by='Time', ascending=False)
    # 変更を保存する
    #df.to_csv('dataset.csv', index=False)

    # SQLite データベースファイルのパスを指定
    db_file_path = 'dataset.db'
    # SQLite データベースファイルを読み込む
    conn = sqlite3.connect(db_file_path)
    # データベースからデータを読み込む
    df = pd.read_sql_query("SELECT * FROM news_table", conn)
    # 重複する行を削除する
    df = df.drop_duplicates()
    # 時間列がある場合、その列を指定して降順で並び替える
    df = df.sort_values(by='Time', ascending=False)
    # 変更を保存する
    df.to_sql('news_table', conn, if_exists='replace', index=False)
    # データベースとの接続を閉じる
    conn.close()


else:
    st.write("")
