import sqlite3

DB_PATH = "data/conversation_logs.db"

def clear_user_logs(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM conversation_logs WHERE user_id =?", (user_id,))
        conn.commit()
        print(f"已成功清空 user_id 为 {user_id} 的所有数据。")
    except Exception as e:
        print(f"删除数据时出现错误: {e}")
    finally:
        conn.close()

# 使用示例
clear_user_logs('kid123')