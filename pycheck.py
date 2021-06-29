import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import base64

check = False

def processing(data, name, result):
    # ファイル読み込み
    data = pd.read_csv(data)
    name = pd.read_csv(name)
    result = pd.read_csv(result)

    # マージしていらないカラムを削除
    data_merge = pd.merge(data, name, on='ユーザー名')
    data_merge = data_merge.drop(["pk", "問題番号", "回答時間", "タイムスタンプ", "ユーザー名"], axis=1)

    result_merge = pd.merge(result, name, on='ユーザー名')
    result_merge = result_merge.drop(["pk", "タイムスタンプ", "ユーザー名"], axis=1)

    # 並び替え
    data_merge = data_merge[["本名", "問題レベル", "点数"]]
    result_merge = result_merge[["本名", "提出数", "合計点", "平均点"]]

    # 数値に直す
    change_level = {
        "D": 1,
        "C": 2,
        "B": 3,
        "A": 4
    }

    data_merge["問題レベル"] = data_merge["問題レベル"].map(change_level)

    # 集計
    data_sum = data_merge[["本名", "問題レベル"]].groupby(by=["本名"], as_index=False).sum()
    data_mean = data_merge[["本名", "点数"]].groupby(by=["本名"], as_index=False).mean()

    # 結合
    result_std = pd.merge(data_sum, data_mean, on='本名')
    result_data = pd.merge(result_std, result_merge, on='本名')
    result_data = result_data.rename(columns={"問題レベル": "アップロード点数", "点数": "平均点数"})
    result_std = result_std.rename(columns={"問題レベル": "アップロード点数", "点数": "平均点数"})
    return result_data, result_std

# 表示部分

# アップロードフィールド
st.subheader("name.csv")
name = st.file_uploader("name.csvアップロード", type='csv')

st.subheader("data.csv")
data = st.file_uploader("data.csvアップロード", type='csv')

st.subheader("result.csv")
result = st.file_uploader("result.csvアップロード", type='csv')

# 実行部分
if name and data and result:
    result_data, result_std = processing(data, name, result)
    check = True

if check:

    # ファイル出力
    def get_download_link(result_data, file_name):
        """Generates a link allowing the data in a given panda dataframe to be downloaded
        in:  dataframe
        out: href string
        """
        if file_name == "csv":
            file = result_data.to_csv()
            b64 = base64.b64encode(file.encode()).decode()
        else:
            file = pd.ExcelWriter('result.xlsx')
            result_data.to_excel(file)
            file.save()

            with open(file,'rb') as f:
                b64 = base64.b64encode(f.read()).decode()

        href = f'<a href="data:file/{file_name};base64,{b64}" download="result.{file_name}">Download {file_name} file</a>'
        return href

    st.subheader("csv 出力")
    st.markdown(get_download_link(result_data, "csv"), unsafe_allow_html=True)

    st.subheader("Excel 出力")
    st.markdown(get_download_link(result_data, "xlsx"), unsafe_allow_html=True)

    # 検索
    name = st.text_input("名前を入力してください。", "")
    btn = st.button('検索')
    reset = False
    if btn:
        result_data = result_data[result_data["本名"].str.contains(name)]
        reset = st.button('リセット')

    if reset:
        result_data = processing(data, name, result)
        reset = False


    st.subheader("生徒ごとの成績")
    st.table(result_data)

    st.subheader("生徒ごとのデータ集計")
    st.table(result_std)

    












