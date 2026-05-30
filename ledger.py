import json
import os
from datetime import datetime

DATA_FILE = "ledger.json"

# ---------- 数据读写 ----------
def load_data():
    """从文件加载数据，如果文件不存在则返回空列表"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(records):
    """保存数据到文件"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

# ---------- 辅助函数 ----------
def generate_id(records):
    """生成新记录的ID（自增）"""
    if not records:
        return 1
    return max(r["id"] for r in records) + 1

def is_valid_date(date_str):
    """检查日期格式是否合法"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def print_separator():
    print("-" * 60)

def print_record(record):
    """打印单条记录"""
    print(f"{record['id']:4d} | {record['type']:2s} | {record['amount']:8.2f} | {record['category']:6s} | {record['date']:10s} | {record['note']}")

def show_all_records(records):
    """显示所有记录"""
    if not records:
        print("暂无任何记账记录。")
        return
    print_separator()
    print(" ID  | 类型 |   金额   | 类别   |   日期    | 备注")
    print_separator()
    for r in records:
        print_record(r)
    print_separator()

# ---------- 核心功能 ----------
def add_record(records):
    print("\n--- 添加记账记录 ---")
    rec_type = input("类型（收入/支出）：").strip()
    if rec_type not in ["收入", "支出"]:
        print("类型只能是“收入”或“支出”。")
        return

    try:
        amount = float(input("金额："))
        if amount <= 0:
            print("金额必须大于0。")
            return
    except ValueError:
        print("金额请输入数字。")
        return

    category = input("类别（如：餐饮、购物、交通、工资等）：").strip()
    if not category:
        category = "其他"

    while True:
        date_str = input("日期（格式：YYYY-MM-DD，直接回车则今天）：").strip()
        if date_str == "":
            date_str = datetime.now().strftime("%Y-%m-%d")
            break
        if is_valid_date(date_str):
            break
        else:
            print("日期格式错误，请重新输入。")

    note = input("备注（可不填）：").strip()

    new_record = {
        "id": generate_id(records),
        "type": rec_type,
        "amount": amount,
        "category": category,
        "date": date_str,
        "note": note
    }
    records.append(new_record)
    save_data(records)
    print("记录添加成功！")

def delete_record(records):
    if not records:
        print("没有记录可删除。")
        return
    show_all_records(records)
    try:
        rid = int(input("请输入要删除的记录ID："))
    except ValueError:
        print("ID必须是数字。")
        return

    for i, r in enumerate(records):
        if r["id"] == rid:
            records.pop(i)
            save_data(records)
            print(f"已删除ID为{rid}的记录。")
            return
    print(f"未找到ID为{rid}的记录。")

def modify_record(records):
    if not records:
        print("没有记录可修改。")
        return
    show_all_records(records)
    try:
        rid = int(input("请输入要修改的记录ID："))
    except ValueError:
        print("ID必须是数字。")
        return

    for rec in records:
        if rec["id"] == rid:
            print("当前记录：")
            print_record(rec)
            print("留空表示不修改。")
            # 修改类型
            new_type = input(f"新类型（收入/支出）[原：{rec['type']}]：").strip()
            if new_type in ["收入", "支出"]:
                rec["type"] = new_type
            # 修改金额
            new_amount = input(f"新金额 [原：{rec['amount']}]：").strip()
            if new_amount:
                try:
                    amt = float(new_amount)
                    if amt > 0:
                        rec["amount"] = amt
                    else:
                        print("金额无效，保持原值。")
                except ValueError:
                    print("金额格式错误，保持原值。")
            # 修改类别
            new_cat = input(f"新类别 [原：{rec['category']}]：").strip()
            if new_cat:
                rec["category"] = new_cat
            # 修改日期
            new_date = input(f"新日期 YYYY-MM-DD [原：{rec['date']}]：").strip()
            if new_date:
                if is_valid_date(new_date):
                    rec["date"] = new_date
                else:
                    print("日期格式错误，保持原值。")
            # 修改备注
            new_note = input(f"新备注 [原：{rec['note']}]：").strip()
            if new_note:
                rec["note"] = new_note

            save_data(records)
            print("修改完成！")
            return
    print(f"未找到ID为{rid}的记录。")

def query_records(records):
    if not records:
        print("暂无数据。")
        return
    print("\n--- 查询方式 ---")
    print("1. 按类别查询")
    print("2. 按日期范围查询")
    print("3. 按备注关键字查询")
    choice = input("请选择：").strip()
    results = []

    if choice == "1":
        cat = input("请输入类别（如餐饮、购物）：").strip()
        results = [r for r in records if r["category"] == cat]
    elif choice == "2":
        start = input("开始日期 YYYY-MM-DD：").strip()
        end = input("结束日期 YYYY-MM-DD：").strip()
        if is_valid_date(start) and is_valid_date(end):
            results = [r for r in records if start <= r["date"] <= end]
        else:
            print("日期格式错误。")
            return
    elif choice == "3":
        keyword = input("备注关键字：").strip()
        results = [r for r in records if keyword in r["note"]]
    else:
        print("无效选择。")
        return

    if not results:
        print("没有符合条件的记录。")
    else:
        print(f"共找到 {len(results)} 条记录：")
        show_all_records(results)

def statistics(records):
    if not records:
        print("没有数据，无法统计。")
        return

    total_income = sum(r["amount"] for r in records if r["type"] == "收入")
    total_expense = sum(r["amount"] for r in records if r["type"] == "支出")
    balance = total_income - total_expense

    print("\n========== 汇总统计 ==========")
    print(f"总收入：{total_income:.2f}")
    print(f"总支出：{total_expense:.2f}")
    print(f"结余：{balance:.2f}")

    # 按类别统计支出（只统计支出）
    expense_by_cat = {}
    for r in records:
        if r["type"] == "支出":
            cat = r["category"]
            expense_by_cat[cat] = expense_by_cat.get(cat, 0) + r["amount"]

    if expense_by_cat:
        print("\n--- 支出类别占比（简易条形图） ---")
        max_amt = max(expense_by_cat.values())
        for cat, amt in sorted(expense_by_cat.items(), key=lambda x: x[1], reverse=True):
            bar_length = int(amt / max_amt * 30) if max_amt > 0 else 0
            bar = "█" * bar_length
            print(f"{cat:8s} : {amt:8.2f}  {bar}")
    else:
        print("暂无支出记录。")

    # 月度统计
    print("\n--- 月度收支统计 ---")
    monthly = {}
    for r in records:
        month = r["date"][:7]  # YYYY-MM
        if month not in monthly:
            monthly[month] = {"收入": 0, "支出": 0}
        monthly[month][r["type"]] += r["amount"]

    for month in sorted(monthly.keys()):
        inc = monthly[month]["收入"]
        exp = monthly[month]["支出"]
        bal = inc - exp
        print(f"{month} : 收入 {inc:8.2f}  支出 {exp:8.2f}  结余 {bal:8.2f}")

def export_to_csv(records):
    """将当前所有记录导出为 ledger.csv"""
    if not records:
        print("没有记录可导出。")
        return

    import csv
    filename = "ledger.csv"
    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "类型", "金额", "类别", "日期", "备注"])
        for r in records:
            writer.writerow([
                r["id"], r["type"], r["amount"],
                r["category"], r["date"], r["note"]
            ])
    print(f"成功导出 {len(records)} 条记录到 {filename}，可用 Excel 直接打开。")

def show_menu():
    print("\n========== 个人记账本 ==========")
    print("1. 添加收支记录")
    print("2. 删除记录")
    print("3. 修改记录")
    print("4. 查询记录")
    print("5. 显示所有记录")
    print("6. 统计汇总")
    print("7. 导出为 CSV")
    print("8. 退出并保存")

# ---------- 主程序 ----------
def main():
    records = load_data()
    while True:
        show_menu()
        choice = input("请选择操作（1-8）：").strip()
        if choice == "1":
            add_record(records)
        elif choice == "2":
            delete_record(records)
        elif choice == "3":
            modify_record(records)
        elif choice == "4":
            query_records(records)
        elif choice == "5":
            show_all_records(records)
        elif choice == "6":
            statistics(records)
        elif choice == "7":
            export_to_csv(records)
        elif choice == "8":
            save_data(records)
            print("数据已保存，感谢使用！")
            break
        else:
            print("无效选项，请重新输入。")

if __name__ == "__main__":
    main()