import pandas as pd
import streamlit as st
import datetime
from decimal import Decimal
import sqlite3
import csv
import os

st.set_page_config(
    page_title="日常收入支出管理系统",
    initial_sidebar_state="auto",
)

if "main_page" not in st.session_state:
    st.session_state["main_page"] = "add_expense_income"
    folder_data = "./data"
    if not os.path.exists(folder_data):
        os.makedirs(folder_data)
    folder_data_db = "./data/db"
    if not os.path.exists(folder_data_db):
        os.makedirs(folder_data_db)
    folder_backup = "./backup"
    if not os.path.exists(folder_backup):
        os.makedirs(folder_backup)
    folder_backup_csv = "./backup/csv"
    if not os.path.exists(folder_backup_csv):
        os.makedirs(folder_backup_csv)

with st.sidebar:
    in_button = st.button("添加收入/支出", use_container_width=True)
    if in_button:
        st.session_state["main_page"] = "add_expense_income"
    query_button = st.button("查询/删除|收入/支出", use_container_width=True)
    if query_button:
        st.session_state["main_page"] = "query_expense_income"
    setting = st.button("设置", use_container_width=True)
    if setting:
        st.session_state["main_page"] = "setting"
db_root_path = "./data/db/"
csv_path = "./backup/csv/"
db_name = "my_life_RMB_amount"
db_path = db_root_path + db_name + ".db"

downloads_csv_name = 'my_life_RMB_amount'
downloads_csv_path = csv_path + downloads_csv_name + ".csv"


def csv_re_to_db(csv_file):
    re_creat()

    with open(csv_file, mode='r', newline='', encoding='gbk') as file:
        reader = csv.DictReader(file)
        data_to_insert = [
            (row['id'], row['date'], row['up_date'], row['type_to_amount'], row['description'], row['amount']) for row
            in reader]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for row in data_to_insert:
        cursor.execute(
            "INSERT INTO expenses (id, date, up_date, type_to_amount, description, amount) VALUES (?, ?, ?, ?, ?, ?)",
            row)

    conn.commit()
    conn.close()


def save_csv(db_path, downloads_csv_path, downloads_csv_name):
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    i_csv = 1
    while True:
        time_date = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        if os.path.exists(downloads_csv_path):
            downloads_csv_path = csv_path + downloads_csv_name + "_" + str(i_csv) + "_" + str(time_date) + ".csv"
            i_csv = i_csv + 1
        else:
            downloads_csv_path = csv_path + downloads_csv_name + "_" + str(time_date) + ".csv"
            break

    with open(downloads_csv_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        cursor.execute("SELECT * FROM expenses")
        rows = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]
        csv_writer.writerow(column_names)

        csv_writer.writerows(rows)

    conn.close()


def re_creat():
    if os.path.exists(db_path):
        save_csv(db_path, downloads_csv_path, downloads_csv_name)

        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            date DATE NOT NULL,
            up_date DATE NOT NULL,
            type_to_amount TEXT NOT NULL,
            description TEXT NOT NULL,
            amount DECIMAL(10, 2) NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


if "auto_save" not in st.session_state:
    st.session_state["auto_save"] = True
    new_name = "auto_backup"
    downloads_csv_path_new_name = csv_path + new_name + ".csv"
    if os.path.exists(db_path):
        save_csv(db_path, downloads_csv_path_new_name, new_name)
    else:
        re_creat()


def setting_path():
    st.title("该页页面可以保存数据库信息到csv文件\n也可以充值数据库，注意重置数据库会丢失所有信息请谨慎操作")
    new_name = st.text_input("请输入保存文件名")
    if st.button("保存到csv文件"):
        if new_name:
            downloads_csv_path_new_name = csv_path + new_name + ".csv"
            save_csv(db_path, downloads_csv_path_new_name, new_name)
        else:
            save_csv(db_path, downloads_csv_path, downloads_csv_name)
    current_directory = os.getcwd()
    loc = "backup\csv\\"
    st.text(os.path.join(current_directory, loc))
    if st.button("删除并备份数据库到csv"):
        re_creat()
    st.text("请选择需要回复的备份，注意回复备份会删除当前数据库")

    file_list = os.listdir(csv_path)

    csv_files = [file for file in file_list if file.endswith(".csv")]

    for csv_file in csv_files:
        xiangdui_path = os.path.join(csv_path, csv_file)
        st.button(label=csv_file, key=csv_file, on_click=csv_re_to_db, args=(xiangdui_path,))


def add_expense_income():
    date = st.date_input("日期")
    type_to_amount = st.radio("类型", ("支出", "收入"))
    description = st.text_input("描述")
    amount = st.number_input("金额", min_value=0.0)

    if st.button("添加"):
        if amount > 0:
            insert_data(date, type_to_amount, description, amount)
            st.success("记录已添加")
        else:
            st.error("请输入正确金额")


def delete_data(id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:

        cursor.execute("SELECT * FROM expenses WHERE id=?", (id,))
        deleted_data = cursor.fetchone()

        cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
        conn.commit()

        if deleted_data:
            conn.close()
            return (True, deleted_data)
        else:
            conn.close()
            return (False, "无该ID的数据")

    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return (False, f"删除数据时发生错误: {str(e)}")


def insert_data(date, type_to_amount, description, amount):
    up_date = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (date, up_date, type_to_amount, description, amount) VALUES (?, ?, ?, ?, ?)",
                   (date, up_date, type_to_amount, description, amount))
    conn.commit()
    conn.close()


def calculate_totals(data):
    daily_expenses = {}
    daily_income = {}
    daily_balance = {}
    total_expenses = Decimal('0.00')
    total_income = Decimal('0.00')
    total_balance = Decimal('0.00')

    all_dates = set(row[1] for row in data)

    for date in all_dates:
        daily_expenses[date] = Decimal('0.00')
        daily_income[date] = Decimal('0.00')

    for row in data:
        date = row[1]
        amount = Decimal(str(row[5]))
        type_to_amount = row[3]

        if type_to_amount == "支出":

            daily_expenses[date] += amount
            total_expenses += amount
        elif type_to_amount == "收入":

            daily_income[date] += amount
            total_income += amount

    for date in all_dates:
        daily_balance[date] = daily_income[date] - daily_expenses[date]

    total_balance = total_income - total_expenses

    return daily_expenses, daily_income, daily_balance, total_expenses, total_income, total_balance


def query_expense_income():
    start_date = st.date_input("起始日期")
    stop_date = st.date_input("结束日期")
    if st.toggle('查询全部日期', value=True):
        start_date = ""
        stop_date = ""
    select_description = st.text_input("请输入要查询的关键词")
    type_to_amount = st.radio("选择类型", ("所有", "支出", "收入"))
    if st.button("查询"):
        data = select_data(start_date, stop_date, type_to_amount, select_description)
        df = pd.DataFrame(data=data, columns=["主键", "日期", "写入日期", "类型", "描述", "金额"])

        st.table(df)
        daily_expenses, daily_income, daily_balance, total_expenses, total_income, total_balance = calculate_totals(
            data)

        for date in daily_expenses:
            st.write(
                f"日期: {date}, 当日总支出: {daily_expenses[date]}, 当日总收入: {daily_income[date]}, 当日结余: {daily_balance[date]}")

        st.write(f"总支出: {total_expenses}, 总收入: {total_income}, 总结余: {total_balance}")

    st.header("删除收入/支出")
    del_id = st.number_input("请输入要删除的记录的主键", min_value=0)
    if st.button("删除"):
        if del_id > 0:
            loc = delete_data(int(del_id))
            if loc[0]:
                st.success("删除成功：" + str(loc[1]))
            else:
                st.error("删除识别：" + loc[1])
        else:
            st.error("请输入正确主键")


def select_data(start_date="", stop_date="", type_to_amount="所有", select_description=""):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 构建SQL查询的基本模板
    query = "SELECT id, date, up_date, type_to_amount, description, amount FROM expenses WHERE 1=1"

    # 定义参数列表
    params = []

    if start_date and stop_date:
        query += " AND date BETWEEN ? AND ?"
        params.extend((start_date, stop_date))

    if type_to_amount in ("支出", "收入"):
        query += " AND type_to_amount = ?"
        params.append(type_to_amount)

    if select_description:
        query += " AND description LIKE ?"
        params.append(f"%{select_description}%")

    query += " ORDER BY date ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    conn.close()

    return rows


def main():
    st.title("收入支出记录管理系统")

    if st.session_state["main_page"] == "add_expense_income":
        st.header("添加收入/支出")
        add_expense_income()
    elif st.session_state["main_page"] == "query_expense_income":

        st.header("查询删除|收入/支出")
        query_expense_income()
    elif st.session_state["main_page"] == "setting":
        st.header("设置界面")
        setting_path()


if __name__ == "__main__":
    main()
