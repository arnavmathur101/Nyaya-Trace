@echo off
title NyayaTrace - Evidence Audit Web Dashboard
echo Starting NyayaTrace Evidence Audit Web Dashboard...
start http://localhost:8501
streamlit run app.py --server.port 8501
pause
