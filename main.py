import streamlit as st
from supabase import create_client, Client

# ─── เชื่อมต่อ Supabase ────────────────────────────
SUPABASE_URL = "https://vpfmcksxctphacshbgfa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwZm1ja3N4Y3RwaGFjc2hiZ2ZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1MzkxOTYsImV4cCI6MjA2NTExNTE5Nn0.JD5troFT5hWIs89VR4rL0EFoklP_c3Crdd3EreUR53w"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── UI หน้าแรก ────────────────────────────────────
st.title("เกม ใช่หรือไม่")

player_name = st.text_input("ใส่ชื่อของคุณ")
room_name = st.text_input("ชื่อห้องที่ต้องการเข้าหรือสร้างใหม่")

if st.button("เข้าร่วมห้อง"):
    # เช็คว่ามีห้องนี้อยู่หรือยัง
    room = supabase.table("rooms") \
        .select("*") \
        .eq("name", room_name) \
        .execute()

    if len(room.data) == 0:
        # สร้างห้องใหม่
        new_room = supabase.table("rooms") \
            .insert({
                "name": room_name,
                "host_name": player_name
            }) \
            .execute()
        st.success(f"สร้างห้องใหม่แล้ว: {room_name}")
        room_id = new_room.data[0]["id"]
    else:
        st.info(f"เข้าห้อง: {room_name}")
        room_id = room.data[0]["id"]

    # เพิ่มผู้เล่น
    supabase.table("players") \
        .insert({
            "room_id": room_id,
            "name": player_name,
            "is_host": len(room.data) == 0
        }) \
        .execute()
    st.success("เข้าร่วมห้องเรียบร้อยแล้ว!")

    # ─── ดึงและแสดงรายชื่อผู้เล่น ─────────────────────
    players = supabase.table("players") \
        .select("*") \
        .eq("room_id", room_id) \
        .execute().data

    st.subheader("ผู้เล่นในห้อง")
    for p in players:
        tag = " (Host)" if p["is_host"] else ""
        st.markdown(f"- {p['name']}{tag}")

    # ─── ตรวจสอบว่าเป็น Host หรือไม่ ─────────────────
    me = [p for p in players if p["name"] == player_name]
    is_host = me[0]["is_host"] if me else False

    # ─── แสดงปุ่มเริ่มเกมเฉพาะ Host ─────────────────
    if is_host:
        st.subheader("คุณคือ Host ของห้องนี้")
        if st.button("🎮 เริ่มเกม"):
            supabase.table("rounds") \
                .insert({
                    "room_id": room_id,
                    "question": "คุณพร้อมเล่นหรือยัง?",
                    "correct_answer": True
                }) \
                .execute()
            st.success("เริ่มเกมแล้ว!")
