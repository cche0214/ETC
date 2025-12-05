import pymysql

# ====== MySQL 连接信息 ======
host = "10.193.129.192"   # 你的 ZeroTier IP
user = "root"
password = "050214@Mysql"
port = 3306

# ====== 连接 MySQL ======
try:
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        charset="utf8"
    )
    print("成功连接到 MySQL！")

except Exception as e:
    print("连接失败:", e)
    exit()

cursor = conn.cursor()

# ====== 查询所有数据库 ======
cursor.execute("SHOW DATABASES;")
databases = cursor.fetchall()

print("\n📌 当前 MySQL 中的数据库有：")
for db in databases:
    print(" -", db[0])

print("\n============================")

# ====== 遍历每个数据库 → 列出表 ======
for db in databases:
    db_name = db[0]
    print(f"\n📂 数据库：{db_name}")

    # 选择数据库
    cursor.execute(f"USE `{db_name}`;")

    # 查询表
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    if tables:
        for t in tables:
            print("   -", t[0])
    else:
        print("   （无表）")

# 关闭连接
cursor.close()
conn.close()
