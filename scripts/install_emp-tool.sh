sudo apt install -y build-essential cmake libssl-dev libgmp-dev libboost-dev 
sudo apt install -y libboost-{chrono,log,program-options,date-time,thread,system,filesystem,regex,test}-dev

git clone https://github.com/emp-toolkit/emp-tool.git
cd emp-tool
git reset --hard 8f95ba4f79bc15d4646e9137f2018b1a12a1343a
cmake .
make
sudo make install
