import streamlit as st
from openai import OpenAI

api_key = "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"

try:
  client = OpenAI(api_key=api_key)
  models = client.models.lsit()
  st.write("API키 사용 가능")
except Exception as e:
  st.write(f"키 사용 불가:{e}")
