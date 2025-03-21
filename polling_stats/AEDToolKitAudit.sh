#!/bin/bash
cat <<COMMENT

 __   _ _______ _______ _______ _______  _____  _     _ _______ 
 | \  | |______    |    |______ |       |     | |     |    |    
 |  \_| |______    |    ______| |_____  |_____| |_____|    |    
                                       ...PROFESSIONAL SERVICES 
 >>CONFIDENTIAL<<                                           

COMMENT
CodeBase="7.1.1.0"
DIFS=$IFS
me=`basename "$0"`
VERSION=0
APImaxVERSION=3
VERBOSE=false
EXPORT=false
MAP=false
fill="L"
FILE1="inventory.st"
FOLDER="/base/data/AEDToolKit/"
path='/base/store/files/' 

test_output() {
  APIErrorCnt=$(cat $1| egrep -c '  "errors": \[')
  if [ $APIErrorCnt -gt 0 ]; then
   echo -e "WARNING: API Response seems to have failed for $1!"
  fi 
}

create_map() {
  echo -e "GID|     Server-Type     |        Copy of      \n---|---------------------|---------------------" > $FOLDER$FILE1
  curl -H X-Arbux-APIToken:$token -ksL https://$ip/api/aps/v$APIversion/protection-groups/server-types/?perPage=0|egrep "parentType|serverType|serverName"|awk -F: '{print $2}'|sed -e $'s/"//g' -e $'s/, //g' -e $'s/,//g' -e $'s/^ //g'|awk '{printf("%s%s", $0, (NR%3 ? "," : "\n"))}'|awk -F, '{print $3";"$2";"$1}' > $FOLDER$FILE1.master.tmp
  TempIFS=$IFS 
  IFS=$'\n'
 
  for line in $(cat $FOLDER$FILE1.master.tmp); do
    IFS=$';'
    LineElements1=($line)
    key=$(echo ${LineElements1[2]}|sed 's/ //g')
    string=$(cat $FOLDER$FILE1.master.tmp|egrep "^$key;"|awk -F\; '{print $2}')
    echo "${LineElements1[0]}|${LineElements1[1]}|$string" >> $FOLDER$FILE1
  done
 
  rm -f $FOLDER$FILE1.*.tmp
  unset -v LineElements1 
  IFS=$TempIFS
}

discover_api_version() {
  if [ $VERSION -eq 0 ]; then
    Counter=$APImaxVERSION
    APIversion=0
    echo -e "\n Discovering API Version..."    	
    
    until [ $Counter -eq 0 ]; do
      if $VERBOSE; then echo "curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aps/v$Counter/summary"; fi
      
      if ! [ $(curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aps/v$Counter/summary|grep -c protectionLevel) = 0 ]; then
        echo -e " Discovered API Version: $Counter\n"
        APIversion=$Counter
        break
      fi
      
      let Counter-=1
    done

    if [ $APIversion -eq 0 ]; then
      echo -e "\nWarning: Provided API credentials might me wrong... Fallback to API Version V1\n"
      if $VERBOSE; then echo -e "DEBUG-API-REPLY"; curl -v -H X-Arbux-APIToken:$2 -ksL https://$1/api/aps/v1/summary; fi
      APIversion=1
    fi
  
  else
    APIversion=$VERSION
  fi
}

poll_stats(){ # $4-> PG_ID, $5-> startTime, $6 --> endTime, $7 --> duration_name
  echo -e "Calling API to save last $7 of traffic stats for PG $4"
  curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aed/v$APIversion/protection-groups/$4/traffic/?startTime=${5}\&endTime=${6} > $3.stats/traffic/$4\_$7.json
  test_output $3.stats/traffic/$4\_$7.json

  echo -e "Calling API to save last $7 of traffic location stats for PG $4"
  curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aed/v$APIversion/protection-groups/ip-locations/?pgid=$4\&startTime=${5}\&endTime=${6} > $3.stats/locations/$4\_$7.json
  test_output $3.stats/locations/$4\_$7.json

  echo -e "Calling API to save last $7 of traffic attack stats for PG $4"
  curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aed/v$APIversion/protection-groups/attack-categories/?pgid=$4\&startTime=${5}\&endTime=${6} > $3.stats/attacks/$4\_$7.json
  test_output $3.stats/attacks/$4\_$7.json

  echo -e "Calling API to save last $7 of traffic service stats for PG $4"
  curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aed/v$APIversion/protection-groups/services/?pgid=$4\&startTime=${5}\&endTime=${6} > $3.stats/services/$4\_$7.json
  test_output $3.stats/services/$4\_$7.json

  echo -e "Calling API to save last $7 of traffic protocol stats for PG $4"
  curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aed/v$APIversion/protection-groups/protocols/?pgid=$4\&startTime=${5}\&endTime=${6} > $3.stats/protocols/$4\_$7.json
  test_output $3.stats/protocols/$4\_$7.json
}

dump_infos(){ # $1 -> Directory , $2-> PG_ID
  echo -e "Collecting Dump Information for PG $2"
  tmsdump -i 'ext*' -c 5000 -m $2 -D rx -t 10 > $1.stats/dumps/$2.log
}


get_statistics(){
  endTime=$(date +%s)
  startTime_7d=`expr $endTime - 604800`
  startTime_1d=`expr $endTime - 86400`
  startTime_1h=`expr $endTime - 3600`
  echo "Creating Directory $3.stats/traffic"
  mkdir -p $3.stats/traffic
  mkdir -p $3.stats/locations
  mkdir -p $3.stats/attacks
  mkdir -p $3.stats/services
  mkdir -p $3.stats/protocols
  if [ "$DUMPS" = true ]; then
    echo "Creating Directory $3.stats/dumps"
    mkdir -p $3.stats/dumps/
  fi
  PGS=$(curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aed/v$APIversion/protection-groups/?perPage=0 | jq -r '.[]')
  for row in $(echo "${PGS}" | jq -r '.[] | @base64'); do
      _jq() {
      echo ${row} | base64 --decode | jq -r ${1}
      }
    PG_ID=$(_jq '.pgid')
    # Last 7 Days
    poll_stats $1 $2 $3 $PG_ID $startTime_7d $endTime 7d
    poll_stats $1 $2 $3 $PG_ID $startTime_1d $endTime 1d
    poll_stats $1 $2 $3 $PG_ID $startTime_1h $endTime 1h
    if [ "$DUMPS" = true ]; then
      dump_infos $3 $PG_ID
    fi
  done
}

call_native() {
  apifile[1]="st"
  apifile[2]="pg"
  apifile[3]="otf"
  apifile[4]="iwh"
  apifile[5]="ibh"
  apifile[6]="ibc"
  apifile[7]="ibd"
  apifile[8]="ibu"
  apifile[9]="obh"
  apifile[10]="obc"
  apifile[11]="owh"
  apifile[12]="mfl"

  api2resource[1]="protection-groups/server-types"
  api2resource[2]="protection-groups"
  api2resource[3]="otf/protection"
  api2resource[4]="protection-groups/whitelisted-hosts"
  api2resource[5]="protection-groups/blacklisted-hosts"
  api2resource[6]="protection-groups/blacklisted-countries"
  api2resource[7]="protection-groups/blacklisted-domains"
  api2resource[8]="protection-groups/blacklisted-urls"
  api2resource[9]="otf/blacklisted-hosts"
  api2resource[10]="otf/blacklisted-countries"
  api2resource[11]="otf/whitelisted-hosts"
  api2resource[12]="filter"

  api3resource[1]="protection-groups/server-types"
  api3resource[2]="protection-groups"
  api3resource[3]="otf/protection"
  api3resource[4]="protection-groups/allowed-hosts"
  api3resource[5]="protection-groups/denied-hosts"
  api3resource[6]="protection-groups/denied-countries"
  api3resource[7]="protection-groups/denied-domains"
  api3resource[8]="protection-groups/denied-urls"
  api3resource[9]="otf/denied-hosts"
  api3resource[10]="otf/denied-countries"
  api3resource[11]="otf/allowed-hosts"
  api3resource[12]="filter"

  for j in {1..3}; do
    echo -e " Calling API, saving ${api3resource[$j]} to $3.${apifile[$j]}"
    if $VERBOSE; then echo -e "\nDBG: curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aps/v$APIversion/${api3resource[$j]}/?perPage=0"; fi
    curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aps/v$APIversion/${api3resource[$j]}/?perPage=0 > $3.${apifile[$j]}
    test_output $3.${apifile[$j]}
  done

  echo -e " Calling API, saving protection-groups/ids/alert-thresholds/ to $3.at"
  for id in $(grep pgid $3.pg|awk -F" " '{print $2}'|sed -e $'s/,//g'); do 
    echo pgid:$id >> $3.at
    if $VERBOSE; then echo -e "\nDBG:curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aps/v$APIversion/protection-groups/$id/alert-thresholds/"; fi
    curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aps/v$APIversion/protection-groups/$id/alert-thresholds/|egrep '\"'|sed -e $'s/"//g' -e $'s/{//g' -e $'s/, //g' -e $'s/,//g' -e $'s/ //g' >> $3.at
  done 
  test_output $3.at

  text_errors="-1"
  if [ "$APIversion" -ge "3" ]; then
     text_errors=$(curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aps/v$APIversion/protection-groups/allowed-hosts/|egrep -c '"errors":')
  fi

  if [ "$text_errors" -gt 0 ] && [ ! "$VERSION" -ge "3" ]; then
       ((APIversion=APIversion-1))
       echo -e "\n WARNING: Fallback to older API Version (V$APIversion) for allow/deny list support.\n  Use the \"-v\" to force an API Version to be used.\n" 
       for j in {4..12}; do
         echo -e " Calling API, saving ${api2resource[$j]} to $3.${apifile[$j]}"
         if $VERBOSE; then echo -e "\nDBG: curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aps/v$APIversion/${api2resource[$j]}/?perPage=0"; fi
         curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aps/v$APIversion/${api2resource[$j]}/?perPage=0 > $3.${apifile[$j]}
         test_output $3.${apifile[$j]}
       done
  else
     for j in {4..12}; do
       echo -e " Calling API, saving ${api3resource[$j]} to $3.${apifile[$j]}"
       if $VERBOSE; then echo -e "\nDBG: curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aps/v$APIversion/${api3resource[$j]}/?perPage=0"; fi
       curl -H X-Arbux-APIToken:$2 -ksL https://$1/api/aps/v$APIversion/${api3resource[$j]}/?perPage=0 > $3.${apifile[$j]}
       test_output $3.${apifile[$j]}
     done
     if [ "$TRAFFIC" = true ]; then
        get_statistics $1 $2 $3
     fi
  fi
}

echo -e "\nATTENTION: This script should only be used by NETSCOUT,"
echo -e "           or when you have been specifically asked to do so."

while getopts v:demtp option ; do
 case "${option}"
 in
 v) VERSION=${OPTARG};;
 d) VERBOSE=true;;
 e) EXPORT=true;; 
 m) MAP=true;; 
 t) TRAFFIC=true;;
 p) DUMPS=true;;
 esac
done

if [ $EXPORT = "false" ] && [ $MAP = "false" ]; then
 echo -e "\nDIAG> bash $me <option(s)>\n
\t-e\t export configuration elements\n
\t-m\t show Server-Types mapping\n
\t-t\t export Protection Groups traffic statistics\n
\t-p\t export Protection Groups traffic dumps\n
\t-v\t API-Version 1,2,...
\t  \t  (default=discovery)\n\n
   These are the tested AED Versions for this Script V$CodeBase
 \t- 6.4.0, 6.4.1\n\t- 6.5.0\n\t- 6.6.0\n\t- 6.7.0.0\n\t- 6.8.0.0, 6.8.1.0\n\t- 6.9.0.0\n\t- 6.10.0.0\n\t- 7.0.0.0\n\t- 7.1.0.0, 7.1.1.0\n"   
 exit 1
fi 

if [ $EXPORT = "true" ] && [ $MAP = "true" ]; then
 echo -e "\n\nERROR: Please select only one option at a time! Bye...\n\n"
 exit 1
fi 

if ! ( [ $VERSION -ge 0 ] && [ $VERSION -le $APImaxVERSION ] ) ; then
 echo -e "\n\nERROR: Unsupported API Version '$VERSION' detected! Bye...\n\n"
 exit 1
fi 

if [ -d "/base/data" ]; then
  if [ ! -d "$FOLDER" ]; then
    mkdir -p $FOLDER
  fi 
else
  FOLDER=""
fi

ip=$(ifconfig mgt0 2>/dev/null|grep 'inet addr'|awk '{print $2}'|awk -F: '{print $2}')

if [ "$ip" = "" ]; then
  ip=$(ifconfig mgt0 2>/dev/null|grep 'inet '|awk '{print $2}')
fi

if [ "$ip" = "" ]; then
  ip="127.0.0.1"
fi

if [ "$EXPORT" = true ] || [ "$MAP" = true ]; then
  echo -n "Please Enter LOCAL APITOKEN and press [ENTER]: "
  read token    
  
  if [ "$token" = "" ]; then
    echo -e "\n\nERROR: Empty Input detected! Bye...\n\n!"
    exit 1
  fi
  
  if [ ! -d "$path" ]; then
    echo -e "\n\nERROR: SCRIPT IS REQUIRED TO RUN DIRECTLY ON THE AED! Bye...\n\n"
    exit 1
  fi 
    
  file=$(hostname | sed 's/[.]/-/g')_$(date +"%d-%m-%y")

  if [ "$EXPORT" = true ]; then
    discover_api_version $ip $token 
    call_native $ip $token $file
    echo -e "\n Building package $path$file$fill.tar.bz2\n"
    if [ "$TRAFFIC" = true ]; then
      tar -cjf $path$file$fill.tar.bz2 $file.st $file.pg $file.at $file.iwh $file.ibh $file.ibc $file.ibd $file.ibu $file.obh $file.owh $file.obc $file.otf $file.mfl $file.stats/*
      rm -rf $file.stats/
    else
      tar -cjf $path$file$fill.tar.bz2 $file.st $file.pg $file.at $file.iwh $file.ibh $file.ibc $file.ibd $file.ibu $file.obh $file.owh $file.obc $file.otf $file.mfl
    fi
    rm -f $file.pg $file.st $file.at $file.iwh $file.ibh $file.ibc $file.ibd $file.ibu $file.obh $file.owh $file.obc $file.otf $file.mfl
  elif [ "$MAP" = true ]; then
    discover_api_version $ip $token 
    create_map
    IFS=$TempIFS 
    cat $FOLDER$FILE1|column -t -s '|'
    echo -e " "
  fi
fi
