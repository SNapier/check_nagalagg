import requests, argparse, os, datetime
from time import sleep
from datetime import datetime
from random import *

#EXPECTED IN THE SAME DIRECTORY AS THE PLUGIN
import nagiosxi_plugin_helper as xihlpr

#DEAL WITH THE SELF SIGNED NAGIOS SSL
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#NAGIOS ALERT AGGREGATOR
#WHEN EXECUTED THE PLUGIN WILL COMPILE A LIST OF ANY PROBLEM STATES EXISTING
#FOR A SPECIFIC HOST OBJECT AND TRIGGER A SINGLE NAGIOS ALERT THAT CONTAINS 
#THE AGGREGATED COUNTS RESULTS THAT CAN BE SENT FORWARD WITH NAGIOSXI STANDARD
#NOTIFICATION WORKFLOWS.
 
#SNAPIER

#SCRIPT DEFINITION
cname = "check_nagalagg"
cversion = "0.0.3"
appPath = os.path.dirname(os.path.realpath(__file__))


if __name__ == "__main__" :
    
    #INPUT FROM NAGIOS
    args = argparse.ArgumentParser(prog=cname+" v:"+cversion, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    #ARGS
    #NSID
    args.add_argument(
        "-n","--nsid",
        required=False,
        choices=("drs","dev","prd"),
        default=None,
        help="String(nsid): The target nagiosxi environment for the plugin."
    ),    
    #HOSTNAME/ADDRESS
    args.add_argument(
        "-H","--host",
        required=True,
        default=None,
        help="String(hostname/hostaddress): The target host for the plugin to execute against."
    ),
    #CRITICAL THRESHOLD
    args.add_argument(
        "-s","--starttime",
        required=True,
        default=None,
        help="String(SECONDS): The start time in seconds from now to begin event aggreagtion."
    ),
    #WARNING THRESHOLD
    args.add_argument(
        "-e","--endtime",
        required=False,
        default=None,
        help="String(TIMESTAMP): The end time 'timestamp' to stop event aggreagtion, defaults to now if empty."
    ),
    #CRITICAL THRESHOLD
    args.add_argument(
        "-c","--crit",
        required=False,
        default=None,
        action="store_true",
        help="Boolean(CRITICAL): Include critical states in the evaluation."
    ),
    #WARNING THRESHOLD
    args.add_argument(
        "-w","--warn",
        required=False,
        default=None,
        action="store_true",
        help="Boolean(WARNING): Include warning states in the evaluation."
    ),
    #PERFDATA
    args.add_argument (
        "-p","--perfdata",
        required=False,
        default=None,
        action="store_true",
        help="Boolean(True/False): If present in the comaand then perfdata for the check will be included in the output."
    )

    #PARSE ARGS
    meta = args.parse_args()

    #TIMESTAMP 1 SECOND RESOLUTION
    nowtstamp = round(datetime.now().timestamp())
    starttime = (nowtstamp - int(meta.starttime))

    #INCLUDED AS A TEST FOR THE NAGIOS CREDS FILE
    #INFO IS USED WITH NAGIOSXI GENERIC API CALLS
    if meta.nsid:
        #GET CREDS FROM YAML
        crds = xihlpr.creds(meta.nsid)
        if crds == False:
            stateid = "3"
            msg = "FAILED TO GET NAGIOSXI API CREDENTIALS"
            xihlpr.nagExit(stateid,msg)

    #CRITICAL PROBLEM STATE
    cps = False
    cpscount = 0
    dcp = False

    #DETECT CRITICAL PROBLEMS
    if meta.crit:
        dcp = True
    
    #WARNING PROBLEM STATES
    wps = False
    wpscount = 0
    dwp = False
    
    #DETECT WARNING PROBLEMS
    if meta.warn:
        dwp = True
    
    #GET THE LATEST ALERTS FROM THE NAGIOSXI LOGENTRIES API ENDPOINT
    #USE LOGENTRY ID TO LIMIT THE LOGS
    types="262144,32768,65536"

    #ENDTIME IS OPTIONAL BUT IF IT WAS INCLUDED WE SHOULD ACCOUNT FOR THAT IN THE MODIFIER
    if meta.endtime:
        modifier = "&starttime={}&endtime={}&logentry_type=in:{}".format(starttime,meta.endtime,types)
    else:
        modifier = "&starttime={}&logentry_type=in:{}".format(starttime,types)

    #USE THE NAGIOSXI API TO GET LOGS
    logs = xihlpr.nagiosxiGenericAPI("objects","logentries",modifier,"get",crds["url"],crds["apikey"])

    if logs:
        #JSON!
        lj = logs.json()
        
        #COUNTZ
        okcount = 0
        totalcount = 0
        
        #LOOPZ
        if lj["recordcount"] > 0:
            
            #PROBLEM LIST
            plist = list()

            for i in lj["logentry"]:
                
                #GET THE LOG ENTRY DATA SO WE CAN EVALUATE THE OUTPUT
                led = i["logentry_data"].split(";")
                
                #WE KNOW THAT THESE ARE SERVICE ALERTS AND WE NEED THE HOSTNAME
                #TO CONTINUE TO PARSE THE RESULTS
                for e in range(len(led)):
                    sa = led[0].split(":")
                    sn = led[1]
                    ss = led[3]

                    #SPLIT HOST FROM SERVICE ALERT
                    for z in range(len(sa)):
                        host = sa[1].strip()

                #IF ANY OF THESE ALERTS IS FOR OUR TARGET HOST WE CAN COUNT THEM
                #TODO LONG SERVICE OUTPUT
                if host == meta.host:

                    #INCREMENT THE COUNTS AND SET OUTPUT
                    totalcount += 1
                    let = i["logentry_type"]
                    
                    #WARNING
                    if let == "32768" and ss == "HARD":
                        wps = True
                        wpscount += 1
                        plist.append(sn)
                    
                    #CRITICAL
                    elif let == "65536" and ss == "HARD":
                        cps = True
                        cpscount += 1
                        plist.append(sn)
                    
                    #OK
                    else:
                        okcount += 1
            #WE HAVE A PROBLEMLIST
            #print(plist)

    #WE FAILED TO GET THE LOGS
    else:
        stateid = "3"
        msg = "FAILED TO GET THE LOG ENTRIES FROM NAGIOSXI"
        xihlpr.nagExit(stateid,msg)
    
    #EVALUATE THE LOG RESULTS
    stateid = ""
    msg = ""
    
    #NORMALLY FIRST IS WORSE BUT, WHY NOT BOTH?
    if dcp and cps and dwp and wps:
        # WE WILL STILL EXIT CRIT BUT INCLUDE BOTH COUNTS IN THE MESSAGE
        stateid = "2"
        msg = "({}) CRITICAL PROBLEM/S AND ({}) WARNING PROBLEM/S DETECTED ON ({}) IN THE LAST ({})s. SERVICE/S=[{}]".format(cpscount,wpscount,meta.host,meta.starttime,",".join(plist))

    #IF WE ARE TO DETECT CRITICAL PROBLEMS AND CRITICAL PROBLEM STATE IS TRUE EXIT CRIT
    elif dcp and cps:
        stateid = "2"
        msg = "({}) CRITICAL PROBLEM/S DETECTED ON ({}) IN THE LAST ({})s. SERVICE/S=[{}]".format(cpscount,meta.host,meta.starttime,",".join(plist))
    
    #IF NOT CRIT AND WARNING PROBLEM STATE IS TRUE EXIT WARNING
    elif dwp and wps and cps == False:
        stateid = "1"
        msg = "({}) WARNING PROBLEM/S DETECTED ON ({}) IN THE LAST ({})s. SERVICE/S=[{}]".format(wpscount,meta.host,meta.starttime,",".join(plist))    
    
    #WE GOT NO REPORTABLE PROBLEMS EXIT OK
    #THIS TAKES INTO ACCOUNT THE POSSIBILITY OF NEITHER CRITICAL OR WARNING PROBLEMS DETECTED
    else:
        stateid = "0"
        msg = "NO REPORTABLE PROBLEM/S DETECTED ON ({})IN THE LAST ({})s".format(meta.host,meta.starttime)

    #PERFDATA
    #MEASURE EVERYTHING!
    if meta.perfdata: 
        pdata = " | total_count={}; ok_count={}; warn_count={}; crit_count={};".format(totalcount,okcount,wpscount,cpscount)
        msg += pdata

    #EXIT THE PLUGIN
    xihlpr.nagExit(stateid,msg)