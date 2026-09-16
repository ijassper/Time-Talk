import streamlit as st
from openai import OpenAI


try:
  client = OpenAI(api_key=api_key)
  models = client.models.list()
  st.write("API키 사용 가능")
except Exception as e:
  st.write(f"키 사용 불가:{e}")
