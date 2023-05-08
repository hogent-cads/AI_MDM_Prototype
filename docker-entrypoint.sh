#!/usr/bin/env bash

echo "Starting nginx"
nginx

echo "Starting gunicorn"
gunicorn --workers=3 run_flask:app --daemon

echo "Starting streamlit"
streamlit run run_streamlit.py \
    --server.port 8501 \
    --server.baseUrlPath /aimdmtool/ \
    --server.enableCORS true \
    --server.enableXsrfProtection true \
    --server.headless=true \
    &> /dev/null