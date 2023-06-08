#!/bin/sh

# Do not use a virtual environment for now
#source envs/ai-mdm/bin/activate

# Start the websocket relay server
# nohup python run_websocketrelay_server.py &

# Start gunicorn and streamlit
nohup gunicorn -t 0 --worker-class gevent -w 3 run_flask:app --access-logfile gunicorn.access.log --error-logfile gunicorn.error.log &
nohup streamlit run run_streamlit.py --server.port 8501 --server.baseUrlPath /aimdmtool/ --server.enableCORS true --server.enableXsrfProtection true --server.headless=true --browser.gatherUsageStats false &

# Set environment variables, but maybe this doesn't do much.
export SPARK_HOME=$HOME/AI_MDM_Prototype/external/spark
export ZINGG_HOME=$HOME/AI_MDM_Prototype/external/zingg

export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin:ZINGG_HOME/scripts
