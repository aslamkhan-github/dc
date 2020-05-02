#!/bin/bash
#
#
###########################################################################################################################################################################
######################################  THIS SCRIPT IS FOR UPGRADING ANY VERSION OF DC TO THE MOST LATEST VERSION  ########################################################
###NOTE: This Script must be run on the SYSPU Manager & Prior to this dont forget to put the ISO File into the /tmp/cores folder of SYSPU Manager with respect to its OS###
###########################################################################################################################################################################
###########################################################################################################################################################################
#
#                        Script_DC_Upgrades.bash
#
#=========================================================================
# MediaKind - Aslam Khan
#=========================================================================
# Current version: v3.0 - 02/04/2020
#========================================================================
# History:
#   - v1.0 - 25/10/2019 - Creation for DC upgrades from older to 1.7.0
#                           
#	- v2.0 - 19/12/2019 - Made to upgrade any older version to 1.7.1
#                       - Also it automates the riemann logs pulling                          
#   - v3.0 - 01/04/2020 - Added the lines to collect data immediatley after 
#						  upgrades.
#                         
#       
#=========================================================================


echo "Script starting `date`" >> /root/dc_upgrade_log.txt
#mount -o loop /tmp/cores/SW_data_collection_service-VSPP-6.RHEL6.6.iso /mnt/
mount -o loop /tmp/cores/SW_data_collection_service* /mnt/
/mnt/copy2HD.bash
umount /mnt/
createrepo --update /var/sysu/repos/fabrix_sw/
sysu apps.rsync -n syspu
#sysu -S MGRDB packages.install -p DataCollectionSyspuWrapper	
#sysu -S MGRDB sketch
crm resource stop data_collection_service
sysu -S MGRDB apps.upgrade -n data_collection
/bin/cp /opt/Fabrix.TV/Troubleshooting/DataCollectionService/bin/config.ini /opt/Fabrix.TV/Troubleshooting/DataCollectionService/bin/config.ini.old
/bin/mv /opt/Fabrix.TV/Troubleshooting/DataCollectionService/bin/config.ini.rpmnew /opt/Fabrix.TV/Troubleshooting/DataCollectionService/bin/config.ini

#Setting the params in config.ini
#Setting the params in config.ini

#rip=`grep -i riemann_ip /var/sysu/system.ini |awk '{print $5}'`
rip=`grep -i riemann_ip /opt/mon_agent/conf.d/mplugins/mon_agent.ini |awk '{print $3}'`
CHECK=`grep -i diagnostics_ip /opt/Fabrix.TV/Troubleshooting/DataCollectionService/bin/config.ini | awk '{print $3}'`
 if [ $rip == $CHECK ];then
    echo "Parameters are already set.." | tee -a /dev/tty |grep bar
 else    
    sed -i 's/diagnostics_ip =/diagnostics_ip = '$rip'/' /opt/Fabrix.TV/Troubleshooting/DataCollectionService/bin/config.ini 
    sed -i 's/grafana_url =/grafana_url = http:\/\/'$rip':3000/' /opt/Fabrix.TV/Troubleshooting/DataCollectionService/bin/config.ini
 fi

name=`hostname`
manager=`sysu ls.nodes |grep -2 "$name"  |grep node_name |awk '{print $4}'`

 if [ $manager == "mgrdb1" ];then
    sysu -N mgrdb2 scp.put -rp /opt/Fabrix.TV/Troubleshooting/DataCollectionService/bin/config.ini:/opt/Fabrix.TV/Troubleshooting/DataCollectionService/bin/config.ini
 else
    sysu -N mgrdb1 scp.put -rp /opt/Fabrix.TV/Troubleshooting/DataCollectionService/bin/config.ini:/opt/Fabrix.TV/Troubleshooting/DataCollectionService/bin/config.ini
 fi

sysu -A manager psh "cat /opt/Fabrix.TV/Troubleshooting/DataCollectionService/bin/config.ini|egrep 'diagnostics_ip|grafana_url'"
crm resource start data_collection_service
sysu -A manager psh "rpm -qa |grep data_coll"
VER=`sysu -A manager psh rpm -qa |grep data_coll |tail -n 1 | awk '{print $2}'`
echo "The DC Got Upgraded to the Most Latest Version on both the Managers which is:" $VER | tee -a /dev/tty |grep bar

#Collecting Data
echo "Please Wait for few moments..." | tee -a /dev/tty |grep bar 
sleep 30

RUN_DC=`crm_mon -1 |grep data_collection_service |awk '{print $4}'`
RUN_SYSPU=`crm_mon -1 |grep syspu_vip |awk '{print $4}'`
  
 if [ $RUN_DC == $RUN_SYSPU ]; then
     echo "Data Collection is Starting... Please Wait until it finishes" | tee -a /dev/tty |grep bar
     /opt/Fabrix.TV/Troubleshooting/DataCollectionService/dc_cli/auto_data_collector.sh
 else
    echo "Please collect the data from Other Manager" | tee -a /dev/tty |grep bar
 fi

echo "Script Ended `date`" >> /root/dc_upgrade_log.txt
