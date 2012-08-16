#!/usr/bin/python

#This program installs the modified version of "OpenStack" Devstack version
#which includes billing modules.
#This setup is based "Devstack" installation

import os
import shutil
import subprocess
#This setup works only in ubuntu server Ubuntu server 11.10 

#Copy files to ~/devstack i.e. home directory
#----------copy_devstack begins-----------#
def copy_devstack(dir):
	
	try:
		current_dir = os.path.abspath(os.path.join(dir, 'devstack'))
		dst_dir = os.path.join(os.getenv("HOME"),'devstack')
		if  os.path.exists(dst_dir):
			print '\nRemoving existing devstack directory...' 
			shutil.rmtree(dst_dir)
		print '\n Making new directory ~/devstack'
		shutil.copytree(current_dir, dst_dir)
	        user = os.getenv("SUDO_USER")
		home_dir = os.getenv("HOME")
                subprocess.call(["sudo", "chown", "-R", user +":"+ user, os.path.join(home_dir, 'devstack')])

	except IOError:
		print '\n Unable to copy directory...'
	
	return

#----------copy_devstack ends-----------#

#----------copy_stack begins-----------#
def copy_stack(dir):
	current_dir = os.path.abspath(os.path.join(dir, 'stack'))

	try:
		if  os.path.exists('/opt/stack'):
			print '\n Removing existing /opt/stack directory...'
			shutil.rmtree('/opt/stack')
		print '\n Making new directory /opt/stack/'
		shutil.copytree(current_dir, '/opt/stack')
		user = os.getenv("SUDO_USER")
		subprocess.call(["sudo", "chown", "-R", user +":"+ user, "/opt/"])

	except IOError :
		print 'Unable to copy directory... ' 
		
	except OSError :
		print '\n\n Failed \n\n Run this script with sudo i.e.sudo python\n\n'
		
	return
#----------copy_stack ends-----------#

		

		
#----------main function begins-----------#
def main():
	print 'This script is tested in Ubuntu server 11.10 (Oneiric Ocelot)\n'
	copy_devstack('.')
	copy_stack('.')


if __name__ == '__main__':
	main()
