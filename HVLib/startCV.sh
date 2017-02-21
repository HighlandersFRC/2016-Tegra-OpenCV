#source /home/ubuntu/.bashrc

export LD_LIBRARY_PATH=/usr/local/cuda-6.5/lib:/usr/local/lib:/usr/lib:/lib:
#. /home/ubuntu/.bashrc
cd /home/ubuntu/2016-Tegra-OpenCV/HVLib	
sudo ifconfig eth0 hw ether $(ethtool -P eth0 | awk '{print $3}')

nohup python AdvancedWebInterface.py


