import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text  # <--- 1. 导入这个函数

class LocalStorage:
    @staticmethod
    def get_conn():
        return st.connection("postgresql", type="sql")

    @staticmethod
    def load_data():
        conn = LocalStorage.get_conn()
        try:
            # 修改：增加 id 的查询，方便后续删除
            df = conn.query("""
                SELECT 
                    id,
                    created_at as date, 
                    question as q, 
                    answer as a, 
                    result 
                FROM interview_history 
                ORDER BY created_at DESC
            """, ttl=0)
            return {"history": df.to_dict('records')}
        except Exception as e:
            return {"history": []}

    @staticmethod
    def delete_record(record_id):
        """根据 ID 删除单条记录"""
        conn = LocalStorage.get_conn()
        query = text("DELETE FROM interview_history WHERE id = :id")
        try:
            with conn.session as s:
                s.execute(query, params={"id": record_id})
                s.commit()
            return True
        except Exception as e:
            st.error(f"删除失败: {e}")
            return False

    @staticmethod
    def save_record(question, answer, result):
        conn = LocalStorage.get_conn()
        current_date = datetime.now()
        
        # 确保插入的列名与数据库 (created_at) 一致
        query = text("""
            INSERT INTO interview_history (created_at, question, answer, result) 
            VALUES (:date, :q, :a, :r);
        """)
        
        with conn.session as s:
            s.execute(
                query, 
                params={"date": current_date, "q": question, "a": answer, "r": result}
            )
            s.commit()