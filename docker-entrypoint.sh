#!/usr/bin/env bash

echo "Starting nginx"
nginx

echo "Starting gunicorn"
gunicorn --worker-class gevent --workers=3 \
         -t 0 \
         --access-logfile gunicorn.access.log \
         --error-logfile gunicorn.error.log \
         run_flask:app --daemon

echo "Starting streamlit"
streamlit run run_streamlit.py \
    --browser.gatherUsageStats false \
    --server.port 8501 \
    --server.baseUrlPath /aimdmtool/ \
    --server.enableCORS true \
    --server.enableXsrfProtection true \
    --server.headless=true \
    &> /dev/null
