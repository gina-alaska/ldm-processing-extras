#!/bin/bash
##################################
ddtt=`date +%Y%m%d`
logDir='/home/processing/cmorph2/log'
(
export PATH=$PATH:/opt/ldm/bin
export PYTHONPATH=/usr/bin/python3
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/python3.6
readonly LOCKFILE_DIR=/tmp
readonly LOCK_FD=201

lock() {
    local prefix=$1
    local fd=${2:-$LOCK_FD}
    local lock_file=$LOCKFILE_DIR/$prefix.lock

    # create lock file
    eval "exec $fd>$lock_file"

    # acquier the lock
    flock -n $fd \
        && return 0 \
        || return 1
}

eexit() {
    local error_str="$@"

    echo $error_str
    exit 1
}

main() {
   #
   echo "+++++ Starting CMORPH2 download - `date` ++++++"
   #
   # chg to download directory
   toolDir='/home/processing/cmorph2'
   archiveDir='/mnt/noaa-case-study-data/cmorph2'
   cd $toolDir/download
   echo "Running: $toolDir/get_cmorph2.py"
   $toolDir/get_cmorph2.py 
   #
   if ls | grep CMORPH2
   then
      for filename in CMORPH2*.nc
      do
         echo "pqinsert -v $filename"
         pqinsert -v $filename
         echo "Moving file to $archiveDir"
         mv $filename $archiveDir
         DFLAG="True"
      done
   else
      echo "No recent files found!"
   fi
   # clean up old archive files
   old_ddtt=`date -d '2 days ago' +%Y%m%d`
   echo "Checking for old CMORPH2 files: $old_ddtt"
   if ls $archiveDir | grep CMORPH2_0.05deg-30min_"$old_ddtt"
   then
      echo "Removing CMORPH2 files valid: $old_ddtt"
      rm $archiveDir/CMORPH2_0.05deg-30min_"$old_ddtt"*.nc
   fi
   #  also clean up old logs
   if ls $toolDir/log | grep cmorph2-"$old_ddtt".log
   then
      echo "Removing old logs: $old_ddtt"
      rm $logDir/cmorph2-"$old_ddtt".log
   fi
   ddtt=`date +%Y%m%d`
   echo "===== End CMORPH2 download - `date` ======"
}
main
#
) >> $logDir/cmorph2-$ddtt".log" 2>&1

#
