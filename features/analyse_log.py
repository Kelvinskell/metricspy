#!/usr/bin/env python3

import re
import os
import platform
from datetime import datetime

logdate = datetime.now().strftime('%b %e')
date = datetime.today().strftime('%Y-%m-%d')
time = datetime.today().strftime('%H:%M:%S')
user = os.getlogin()

class Logs():
    def __init__(self, values):
        self.values = values

    def logSudo(self):
        # Check file existence and read access
        for file in self.values["log_files"]:
            if file == "/var/log/sudo.log":
                sudo = file
        if not os.access(sudo, os.F_OK) or not os.access(sudo, os.R_OK):
            return False
        

        # Create path
        dirpath = 'logs/sudo'
        filepath = f'report-{date}.txt'

        # Open file
        if not os.path.isdir(dirpath):
            os.mkdir(dirpath)
        logfile = open(os.path.join(dirpath, filepath), 'w')

        # Log to file
        pattern = r'{}'.format(logdate)
        with open(sudo) as file:
            lines = file.readlines()
            for i in range(0, len(lines)):
                line1 = lines[i]
                if re.search(f'^{pattern}', line1):
                    logfile.write(line1)
                    line2 = lines[i + 1]
                    logfile.write(line2)
        logfile.close()
        return True
        ########## Garbage collection will remove any empty files ##########
   


