import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import base64

def processing():
    # ファイル読み込み
    data = pd.read_csv("data.csv")
    name = pd.read_csv("name.csv")
    result = pd.read_csv("result.csv")

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
    result_data = pd.merge(data_sum, data_mean, on='本名')
    result_data = pd.merge(result_data, result_merge, on='本名')
    result_data = result_data.rename(columns={"問題レベル": "アップロード点数", "点数": "平均点数"})
    return result_data
    
# 実行部分
result_data = processing()

# 表示部分
st.subheader("生徒ごとの成績")
st.table(result_data)

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

    












