import os
import csv
import pymysql
from tqdm import tqdm   # 进度条，如果没有 pip install tqdm

# ------------------------------
# 连接 ShardingSphere-Proxy
# ------------------------------
conn = pymysql.connect(
    host="192.168.88.131",
    port=3307,
    user="traffic",
    password="050214@Proxy",
    database="traffic",
    charset="utf8mb4"
)

cursor = conn.cursor()

# ------------------------------
# 数据源目录
# ------------------------------
BASE_DIR = "./data_all"

# ------------------------------
# 需要插入的字段（严格按顺序）
# ------------------------------
FIELDS = [
    "GCXH",
    "XZQHMC",
    "ROAD_ID",
    "K_INDEX",
    "BOUNDARY_LEVEL",
    "BOUNDARY_DETAIL",
    "BOUNDARY_LABEL",
    "CLEAN_KKMC",
    "FXLX",
    "GCSJ",
    "GCSJ_TS",
    "HPZL",
    "HPZL_LABEL",
    "HPHM",
    "BRAND"
]

# 构建 SQL
SQL = f"""
INSERT INTO etc_records (
    {", ".join(FIELDS)}
) VALUES ({", ".join(['%s'] * len(FIELDS))})
"""


# ------------------------------
# 遍历所有子目录、所有 csv
# ------------------------------
def import_csv_files():
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                print(f"\n开始导入文件：{file_path}")

                with open(file_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)

                for row in tqdm(rows, desc=f"导入中 {file}", ncols=90):
                    try:
                        data = [row[field] for field in FIELDS]
                        cursor.execute(SQL, data)
                    except Exception as e:
                        print(f"\n❌ 插入失败，跳过该行（GCXH={row.get('GCXH')}）: {e}")
                        continue

                conn.commit()
                print(f"✔ 文件导入完成：{file_path}")


# ------------------------------
# 主函数
# ------------------------------
if __name__ == "__main__":
    import_csv_files()
    cursor.close()
    conn.close()
    print("\n🎉 全部 CSV 文件导入完成！")
