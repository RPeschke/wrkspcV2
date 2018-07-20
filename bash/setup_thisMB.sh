#!/bin/bash
echo
echo
echo "If you see abnormal behaviour, please use 'ps -au'"
echo "command then kill the related python processes using"
echo "'sudo kill -9 PID' the start again."
echo
echo "If the script hangs up on 'reading scrod register 0,'"
echo "check that the media converter is connected to the "
echo "network as eth4. If it is connected and there are TX"
echo "packets but no RX packets (ifconfig), then check that"
echo "the route is present by typing 'route'."
echo "You can add a new route with the command:"
echo "sudo ip route add 192.168.20.0/24 dev eth4"
echo
#echo "ENTER the interface type:"
#echo "e.g. >>>eth4"
#read -p ">>>" InterfaceType
#echo
InterfaceType=eth4
if [ "$#" = "1" ]
then
  binMask=$1
else
  echo "ENTER ASIC mask:"
  echo "e.g. >>>0100000001  to setup ASIC_0 and ASIC_8"
  echo
  read -p " >>>" binMask
fi
ASICmask=$(bc<<<"obase=10;ibase=2;$binMask")
#echo
echo "Reprogramming FPGA..."
sudo /bin/bash bash/progFPGA.sh
sudo ip route add 192.168.20.0/24 dev eth4
echo "Waiting 30 seconds..."
sleep 30
echo "Reading SCROD register 0"
sudo ./py/MicroProcesses/readRegScrod.py $InterfaceType 0
sleep .1
echo
echo "Setting ASIC and DAC configs..."
sudo ./py/Config/setMBTXConfig.py $InterfaceType
sleep .1
echo "                               ...Set Config-done."
echo "Reading SCROD register 0."
sudo ./py/MicroProcesses/readRegScrod.py $InterfaceType 0
sleep .1
echo
echo "Now calculating pedestals:"
for i in {0..9}
do
	if [ $(($(bc<<<"2^$i")&$ASICmask)) -gt 0 ]
	then
		echo "Calculating pedestals for ASIC $i ..."
		sudo ./py/MicroProcesses/pedcalc.py $InterfaceType $i
		sleep .1
	else
		echo "Skipping ASIC $i....................."
		sleep .05
	fi
done
sleep 1
echo "                                    ......Pedcalc done"
echo
echo "Finished executing 'setup_thisMB.sh'"
echo
echo
