# check_nagalagg
NagiosXI plugin that will aggregate the critical and warning count of alerts for a given host in a specific time range. 

## NAGIOSXI COMMAND
 	python3 $USER1$/check_nagalagg.py -n $ARG1$ -H $HOSTNAME$ -r $EVENTSTARTTIME$ -s $ARG2$ $ARG3$
  
### It gets just the crits,

    check_nagalagg.py -n dev -H u2204ncpa -r <timestamp> -s 300 -c -p
    (2) CRITICAL PROBLEM/S DETECTED ON (u2204ncpa) IN THE LAST (300)s. SERVICE/S=[os.linux.cpu.utilization-percent-avg,os.linux.cpu.utilization-percent-avg] | total_count=2; ok_count=0; warn_count=0; crit_count=2; 

### the crits and the warns,
 
    check_nagalagg.py -n dev -H u2204ncpa -r <timestamp> -s 300 -c -w -p
    (2) CRITICAL PROBLEM/S AND (1) WARNING PROBLEM/S DETECTED ON (u2204ncpa) IN THE LAST (300)s. SERVICE/S=[os.linux.cpu.utilization-percent-avg,os.linux.cpu.utilization-percent-avg,os.linux.cpu.utilization-percent-avg] | total_count=13; ok_count=10; warn_count=1; crit_count=2;

### the negatives,,and it's even got performance data.
    check_nagalagg.py -n dev -H u2204ncpa -r <timestamp> -s 40000 -c -w -p
    NO REPORTABLE PROBLEM/S DETECTED ON (u2204ncpa)IN THE LAST (300)s | total_count=0; ok_count=0; warn_count=0; crit_count=0;

The plugin will also exit with the associated nagios state which corresponds to the problems it finds. This normal method of operation allows for integration into the built in Nagios notification workflows and strategies.

## More important than what it does is what it doesn't do.

**It doesn't limit the start time, go back as far as you want but, beware that comes with consequences.\
**It only calculates hard states.\
**It does not parse or display content any deeper than the host and a list of service names for eventids outside of the big three;

    65536 = CRITICAL ALERT
    32768 = WARN ALERT
    262144 = OK

**It limits the output to a list of services to try and be less impactful for the visual chaos that can be caused by long service output in the XI interface.

# $\color{Bittersweet}{NOTE:}$
When you start talking log aggregation, your talking about horse power with your compute resources. The more logs to be parsed and aggregated the more horse power you need to do the aggregation, it's a viscous cycle. Every time you execute a method, you add load to the system. The more complex the method the more load that you add to the system, the "observer effect". Make note that you may induce more load on the system by using this plugin.

### Outside the limits of a plugin
When you find that the resources, specificity or evaluations you wish to perform gets way more complex than what the on state change processing model of Nagios can provide, you're probably not doing the aggregation in the right place.

Happy Monitoring!
