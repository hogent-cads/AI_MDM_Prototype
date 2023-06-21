#/bin/sh

# This is a script that installs the AI-MDM tool on a Linux Alma server using Vagrant
# This assumes that there is a nginx.conf file in the shared folder /vagrant

sudo dnf -y install git nginx java-1.8.0-openjdk wget pip

# Download external files
wget https://github.com/zinggAI/zingg/releases/download/v0.3.4/zingg-0.3.4-SNAPSHOT-spark-3.1.2.tar.gz
wget https://archive.apache.org/dist/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz
tar xf zingg-0.3.4-SNAPSHOT-spark-3.1.2.tar.gz
mv zingg-0.3.4-SNAPSHOT zingg-0.3.4
tar xf spark-3.1.2-bin-hadoop3.2.tgz
git clone https://github.com/hogent-cads/AI_MDM_Prototype.git

# Copy external files and create symlinks with simpler names
mkdir AI_MDM_Prototype/external
cp -r zingg-0.3.4 AI_MDM_Prototype/external/
cp -r spark-3.1.2-bin-hadoop3.2 AI_MDM_Prototype/external/
ln -sr AI_MDM_Prototype/external/zingg-0.3.4 AI_MDM_Prototype/external/zingg
ln -sr AI_MDM_Prototype/external/spark-3.1.2-bin-hadoop3.2 AI_MDM_Prototype/external/spark

# Download and install miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b
source ./miniconda3/etc/profile.d/conda.sh


# Change the zingg script by adding a line to activate the virtual environment "aimdm"
sed -i '/SPARK_HOME\/bin\/spark-submit/i source \/home\/vagrant\/miniconda3\/etc\/profile.d\/conda.sh && conda activate aimdm' AI_MDM_Prototype/external/scripts/zingg.sh

cd AI_MDM_Prototype
# Create and activate a virtual environment with conda.
conda create -y -n aimdm python=3.10
conda activate aimdm
# Install the packages in this virtual environment
pip install -r requirements.txt
pip install gunicorn gunicorn[gevent]

# Configure and start nginx
# Note: root is set as /usr/share/nginx/html in nginx.conf
sudo mkdir  -p /usr/share/nginx/html/reports
sudo chmod a+rw /usr/share/nginx/html/reports
# Copy nginx.conf to /etc/nginx.
# !! THIS WILL OVERWRITE THE EXISTING nginx.conf FILE !!
sudo cp nginx.conf /etc/nginx/
sudo systemctl enable nginx
sudo systemctl start nginx

# Allow forwarding in SELinux
sudo setsebool -P httpd_can_network_connect 1

