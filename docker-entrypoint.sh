#!/usr/bin/env bash

echo "Starting nginx"
nginx

echo "Starting gunicorn"
conda run --no-capture-output -n aimdm \
         gunicorn --worker-class gevent --workers=3 \
         -t 0 \
         --access-logfile gunicorn.access.log \
         --error-logfile gunicorn.error.log \
         run_flask:app --daemon

echo "Starting streamlit"
conda run --no-capture-output -n aimdm \
    streamlit run run_streamlit.py \
    --browser.gatherUsageStats false \
    --server.port 8501 \
    --server.baseUrlPath /aimdmtool/ \
    --server.enableCORS true \
    --server.enableXsrfProtection true \
    --server.headless=true \
    &> /dev/null
