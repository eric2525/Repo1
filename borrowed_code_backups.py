#!/usr/bin/python

import time
import sys
import os

##
# Configuration variables
##

# Local
script_dir = '/root/script/backup' # Dir script is located in

# Remote
remote_host = 'xx.xxx.xx.xxx' # IP Address of remote host
remote_dir = '/root/backup/tp1' # Remote backup directory
remote_user = 'root' # Remote username

# What to do
backup_home = True # Backup /home directory
backup_etc = True # Bbackup /etc directory
send_alert = True # Send email alert of backup when it finished
do_scp = True # Scp backup

# Other
max_home_dir_size = 2000000 # Max home directory size, in bytes
alert_email = 'jonstjohn@gmail.com' # Email address for alert
path_to_sendmail = '/usr/sbin/sendmail'

##
# Functions
##

# Backup function tars directory, scps to the remote host
def backup(dir, file, remote_host, remote_dir, remote_user, script_dir):

    log.write("Backup up %s to %s\n" % (dir,file))
    os.chdir(dir)
    cmd = "tar -czf %s/%s --exclude-from=%s/backup_exclude.txt ." 
        % (script_dir, file, script_dir)
    os.system(cmd)

    os.chdir(script_dir)

    log.write("Uploading %s\n" % (file))

    if do_scp:
        cmd = "scp -Bq %s %s@%s:%s/%s" % (
            file, remote_user, remote_host, remote_dir, file)
    #print cmd
    os.system(cmd)


##
# Script
##

# Start log file

log_path = "%s/scp_backup.log" % (script_dir);
log = open(log_path,'w')
log.write(
    "Starting script at %s\n" % time.strftime("%m/%d/%Y %H:%M:%S")
)
t1 = time.time()

# Backup all home directories
if backup_home:

    cmd = 'du --max-depth=1 -k /home --exclude-from=backup_exclude.txt'
    put, get = os.popen4(cmd) # Get a listing of directories and sizes

    entries = get.readlines()
    entries.pop()
    for line in entries: # Loop over each line from the du command

        line = line.rstrip()
        size, dir = line.split("\t") # Divide into size and directory name

        if float(size) < max_home_dir_size:
            tmp = dir.split("/") # Split name along directory '/'
            # Name file based on directory name, with tar.gz ending
            file = "%s.tar.gz" % (tmp.pop()) 
            backup(dir, file, remote_host, remote_dir,
                remote_user, script_dir) # Do backup

# Backup /etc
if backup_etc:
    backup('/etc','etc_backup.tar.gz',remote_host, remote_dir,
        remote_user, script_dir)

# End log file
t2 = time.time()
log.write("Ending script at %s\n" % time.strftime("%m/%d/%Y %H:%M:%S"))
log.write("Time to run script: %s seconds\n" % (t2-t1))
log.close()

# Send email alert
if send_alert:

    MAIL = path_to_sendmail

    msg = "To: %s\r\nFrom: %s\r\nSubject: SCP Backup Log\r\n\r\n" 
        % (alert_email)
    f = open(log_path, 'r') # Get contents of log file
    msg += f.read()
    f.close()

    p = os.popen("%s -t" % MAIL, 'w') # Send email
    p.write(msg)
    exitcode = p.close()
    #	if exitcode:
    #	 print "Exit code: %s" % exitcode