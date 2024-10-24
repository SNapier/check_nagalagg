import requests, yaml, os, random, sys, base64
from random import *

#NAGIOS_PLUGIN_TEMPLATE HELPER FILE
#SNAPIER

cname = "nagiosxi_plugin_helper"
cversion = "0.0.3"
appPath = os.path.dirname(os.path.realpath(__file__))

#TEST VALUE
def test():
    i = randint(50,100)
    return i

#NAGIOSXI THRESHOLDS
def nagThresholdRangeEval(xrange,x):
    
    #WE GOT A RANGE 
    if(xrange.startswith('@')):
        threshold = xrange.strip('@')
        threshold = str.split(threshold, ':',1)
        
        #EVALUATE TE RESULT AGAINST THE RANGE
        r = "Nothing Changed Result"
        f = ""
        c = ""
        if threshold[0] != "":
            f = int(threshold[0])         
        #SECOND IS REQUIRED        
        if threshold[1] == "":
            stateid = 3
            msg = "{}: {} - WHEN USING A RANGE @X:CEILING VALUE IS REQUIRED".format(checkStateFromCode(3),cname.upper())
            nagExit(stateid,msg)
        else:
            c = int(threshold[1])
        
        #AM I IN?
        if f != "" and x >= f and x <= c:
            r = True
        elif f == "" and x <= c:
            r = True
        else:
            r = False
    else:
        #WE GOT A MALFORMED VALUE CONTAINING A ":"
        #EXIT UNKNOWN AS CRIT VALUES ARE REUIRED TO PROCESS THE CHECK RESULT
        stateid = 3
        msg = "{}: {} - MALFORMED RANGE VALUE ({}), FORMAT REQUIRED '@int(FLOOR):int(CEILING)'".format(checkStateFromCode(3),cname.upper(),xrange)
        nagExit(3,msg)

    #LATER
    return r


#NAGIOSXI_CONFIG.YAML
#NEVER STORE CREDS IN PLAIN TEXT IN RPODUCTION
def creds(nsid):
    with open(appPath+"\\nagios_config.yml", "r") as yamlfile:
        try:
            data = yaml.safe_load(yamlfile)
            r = {"url":data[0]["nagios"][nsid]["url"],"un":data[0]["nagios"][nsid]["usr"],"pw":data[0]["nagios"][nsid]["pswd"],"apikey":data[0]["nagios"][nsid]["api"]}
        except Exception as e:
            print(e)
            r = False
        finally:
            return r

#API BASIC AUTH EXAMPLE TO REQUEST AN AUTH TOKEN NAGIOSXI SERVER
def nagiosxiAuthAPI(crds):
    
    #DATA PAYLOAD
    d = {
        "username" : crds["un"],
        "password" : crds["pw"],
        "valid_min": "1" 
    }
    myurl = 'https://{}/nagiosxi/api/v1/authenticate?'.format(crds["url"])
    tkn = False
    try:
        #AUTHENTICATE OUR NAGIOSXI USER
        response = requests.post(url=myurl, data=d, verify=False)
        r = response.json()
    except Exception as e:
        print(e)
    finally:
        return r

##NAGIOSXI DIRECT API CALL
def nagiosxiGenericAPI(resource,endpoint,modifier,method,myurl,mykey):
    
    #URL FOR APICALL TO NAGIOSXI
    url = ("https://{turl}/nagiosxi/api/v1/{resource}/{endpoint}?{modifier}&apikey={akey}".format(turl=myurl,akey=mykey,resource=resource,endpoint=endpoint,modifier=modifier)) 

    #ONLY ALLOW FOR USE OF GET IN THIS INSTANCE
    if method == "get":
        try:
            r = requests.get(url=url,verify=False)
        except Exception as e:
            print("ERROR: %s",e)
            r = False
    else:
        r = False
    return r

#NAGIOSXI API V2 
def nagiosxiGenericAPIv2(myxi,myep,mycls,qry,mytkn):
    try:
        myurl = "https://{}/nagiosxi/api/v2/{}/{}?{}&token={}".format(myxi,myep,mycls,qry,mytkn)
        ## Authentication request
        response = requests.get(myurl, verify=False)
        r = response.json()
    except Exception as e:
        print(e)
    finally:    
        return r
    
#STATE FROM STATEID
def checkStateFromCode(i):
    switcher = {
        0: "OK",
        1: "WARNING",
        2: "CRITICAL",
        3: "UNKNOWN"
    }

    #GIVE THE STATE BACK
    return switcher.get(i)

#NAGIOS EXIT
def nagExit(stateid,msg):
    
    #ENRICH IF NEEDED
    print(msg)

    #EXIT WITH THE STATEID
    sys.exit(int(stateid))

########################################################################################
#GENERIC PYTHON FUNCTIONS
########################################################################################

#API BASIC AUTH EXAMPLE TO GATHER TOKEN IN RESPONSE FROM AUTH SERVER
def basicAuthAPI():
    username = 'johndoe'
    password= 'zznAQOoWyj8uuAgq'
    basic_key_secret = username+":"+password
    basic_key_secret_enc = base64.b64encode(basic_key_secret.encode()).decode()

    # Your decoded key will be something like:
    #zzRjettzNUJXbFRqWENuuGszWWllX1iiR0VJYTpRelBLZkp5a2l2V0xmSGtmZ1NkWExWzzhDaWdh
    
    headersAuth = {
        'Authorization': 'Basic '+ str(basic_key_secret_enc),
    }

    data = {
    'key1': 'value1',
    'key2': 'value2'
    }

    ## Authentication request
    response = requests.post('https://somedomain.test.com/token', headers=headersAuth, data=data, verify=True)
    tkn = response.json()
    
    return tkn

#API BEARER AUTH EXAMPLE TO GATHER TELEMETRY DATA
def bearerAuthAPI(tkn):
    #tkn = passed as var

    headersAPI = {
        'accept': 'application/json',
        'Authorization': 'Bearer '+str(tkn),
        #'Authorization': 'Token '+str(tkn),
    }
    ### Usage of parameters defined in your API
    params = (
        ('offset', '0'),
        ('limit', '20'),
    )

    # Making sample API call with authentication and API parameters data
    response = requests.get('https://somedomain.test.com/api/Users/Year/2020/Workers', headers=headersAPI, params=params, verify=True)
    api_response = response.json()
    return api_response

#PERCENTAGE OF A NUMER
def getPercent(a,b,rndcnt=2):
    #MAKE SURE WE ARE DEALING WITH INTEGERS
    int(a)
    int(b)
    
    #GET PERCENT (A) OF (B)
    pct = (a / b * 100)
    
    #MAKE IT MANAGEABLE WITH ROUND
    rpct = round(pct,rndcnt)

    #SHIP IT!
    return rpct
