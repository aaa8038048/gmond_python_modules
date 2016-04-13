import random
import time

import os
import subprocess

import traceback
descriptors=[]
IB_STATS_DIR = '/sys/class/infiniband'
IB_QUERY_UTILITY = 'perfquery'
IB_PORTS = {

}

LAST_METRICS = {}

METRICS = {
    'data': {}
}

def IB_total(name):
	current_time = time.time()
	totalIB=0
	for ib_device in os.listdir(IB_STATS_DIR):
        # Loop through the InfiniBand ports on this device
		ports_path = os.path.join(IB_STATS_DIR, ib_device, 'ports')
		for ib_port_number in os.listdir(ports_path):
			sys_file_path = os.path.join(ports_path, ib_port_number)

            # Store the device information for this port
			lid_file = os.path.join(sys_file_path, 'lid')
			try:
				with open(lid_file) as f:
                    # Linux sysfs lists the port_lid in hex
					port_lid = int(f.readline().split(' ')[0], 0)
			except IOError:
				print("Unable to read IB port LID # from file: %s" % lid_file)
			IB_PORTS[port_lid] = ib_device	
	def process_metric_value(metric_name, counter_value):
		if metric_name=="":
			totalIB=0
		else:
			delta = 0.0
			last_value = 0.0
			try:
				last_value = LAST_METRICS[metric_name]
				if last_value > counter_value:
					delta = counter_value
				else:
					delta = counter_value - last_value

			except KeyError:
                # If LAST_METRICS has no value, this is our first time updating.
				pass

			LAST_METRICS[metric_name] = counter_value
			if metric_name.startswith(('IBtotal')):
				delta *= 4
			try:
				last_time = METRICS['time']
				measurement_interval = current_time - last_time
				METRICS['data'][metric_name] = delta / measurement_interval
			except KeyError:
                # this is our first time updating
				METRICS['data'][metric_name] = delta	
			
		totalIB=METRICS['data'][metric_name]

		return totalIB		
	try:
		total=0
		for pp in IB_PORTS:
		#pp is the lid of the IB,and the port is 1.
			pp=str(pp)
			process = subprocess.Popen(IB_QUERY_UTILITY + " -x"+" "+pp+" 1",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			while True:
				nextline = process.stdout.readline()	
				if nextline == '' and process.poll() != None:
					break
				elif nextline.startswith(('PortRcvData')):
					counter_name = nextline.split(':')[0]
					print '-----------'+counter_name+'--------------'
					try:
						counter_value = float(nextline.split('.')[-1])
						print '+++++++++++++++'+str(counter_value)+'++++++++++++++'
					except KeyError, ValueError:
						counter_value = 0
						print("Unable to read a value from InfiniBand counter %s" % counter_name)
				else:
					continue
			total=total+counter_value
			#get the total data of ib from IB_QUERY_UTILITY that is according to the IB_PORTS.
		IBtotal='IBtotal'
		totalIB=process_metric_value(IBtotal, total)	
		output, error = process.communicate()	
	except:
        # Catch all other exceptions here. 
		error = traceback.format_exc()
	if error:
		print("An error occured while running perfquery:\n\n%s" % error)
	METRICS['time'] = current_time	
	return int(totalIB)
def metric_init(params):
	global descriptors
	random.seed()

	d1={
		'name':'IBtotal',
		'call_back':IB_total,
		'time_max':60,
		'value_type':'uint',
		'units':'C',
		'slope':'both',
		'format':'%u',
		'description':'zzzzzzz',
		'groups':'zongib'
	}

	descriptors=[d1]
	return descriptors
def metric_cleanup():
	pass
if __name__=='__main__':
	metric_init({})
	#test
	while True:
		for d in descriptors:
			v=d['call_back'](d['name'])
			print ('value for %s is '+d['format'])%(d['name'],v)
		time.sleep(5)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
