#!/usr/bin/env python3

# Import modules
try:
    import argparse
    import os
    import sys
except ModuleNotFoundError as error:
    print(f"pymetrics: Error: {error}. \nUse 'pip install' to install module")
from features import config_parse

# Create the parser
parser = argparse.ArgumentParser(prog="pymetrics", description="Collect, analyse and report useful system meyrics", allow_abbrev=False, epilog="Enjoy the program!")

# Version
parser.version = 'pymetrics: version 1.0'

# Add the arguments
parser.add_argument('-c', metavar='Config file', action="store", type=str, help="specify alternative yaml configiration file")
parser.add_argument('-e', '--email', metavar='Email address', action='store', type=str, help='Specify an email address to send report.') 
parser.add_argument('-f', '--format', metavar='Log format', action='store', type=str, help='Specify format for log reporting')
parser.add_argument('-t', '--test', action="store_true", help="test configuration and exit")
parser.add_argument('-T', action='store_true', help="test configuration file, dump it and exit")
parser.add_argument('-v', '--version', action='version', help='Print version and exit')

# Execute parse_args method
args = parser.parse_args()

# Define yaml configuration file
if args.c:
    c = args.c
    if not os.path.exists(c):
        print("pymetrics: Error: No such file or directory.")
        sys.exit(1)
    if not os.path.isfile(c):
        print(f"pymetrics: Error: {c} is not a file")
        sys.exit(1)
    config_file = c
else:
    config_file = "pymetrics.conf.yml"

# Read configuration file
parser_class = config_parse.YamlParser(config_file)
parsed_values = parser_class.yaml_to_python()

# Print configuration
if args.test or args.T:
    if parsed_values:
        print(f"The configuration file {config_file} syntax is ok.", end="\n\n")
        if args.T:
            print(parsed_values)
        sys.exit()
    else:
        print(f"The configuration file {config_file} has bad syntax")
        sys.exit(1)

# Load parsed values
try:
    log_files = parsed_values["log_files"]
    log_format = parsed_values["log_report_format"]
    delete_logs = parsed_values["delete_logs"]
    expire_logs = parsed_values["expire_logs"]
    notify = parsed_values["notify"]
    email_address = parsed_values["email_address"]
    web_log = parsed_values["web_server"]["logs"]
    web_data = parsed_values["web_server"]["data"]
    timeout = parsed_values["timeout"]
    url = parsed_values["url"]
except KeyError as key:
    print(f"pymetrics: Error: Key {key} is missing in {config_file} \nExitting...")
    sys.exit(1)
except TypeError:
    print(f"pymetrics: Error: Missing value(s) in {config_file} \nExiting...")
    sys.exit(1)

# Load email address from '-e' option
if args.email:
        email_address = args.email

# Check if email is valid
if email_address:
    import re
    pattern = r"((?#Prevent prefix from begining with any special characters)^[A-Za-z0-9]+[-\.\w]+(?#Negative look behind)(?<![-\._]))@([-\w]+).([A-Z|a-z]{2,}[.]?)+"
    if not re.fullmatch(pattern, email_address):
        email_address = None
        print("pymetrics: Info: Email address not valid. \nOmitting...")

# Specify log format
if args.format:
    if args.format not in ["plain_text", "csv", "json"]:
        print(f"pymetrics: Info: Illegal format {args.format}. \nUsing default format.")
    else:
        log_format = args.format

# Convert parsed values to a dictionary
values = {"log_files": log_files, "log_format": log_format, "delete_logs": delete_logs, "expire_logs": expire_logs,
        "notify": notify, "email": email_address, "web_log": web_log, "web_data": web_data, "url": url, "timeout": timeout}

# Check for Illegal keys in config file
for key in parsed_values.keys():
    if key not in values.keys():
        if key in ["email_address", "log_report_format", "web_server"]:
            pass
        else:
            print("pymetrics: Info: Illegal key: {} in {}".format(key, config_file))

# Log usage to logs/access.log
from features import access
access.WriteToAccessLog().log()

# Collect system information
from features import sys_info
info = sys_info.SysFetch(values)
log = sys_info.LogSysFetch(values)

# Send collected metrics to logs
log.logGeneral()
log.logConnection()
log.logInterface()

# Garbage collection
from features import delete_log
gc = delete_log.DeleteLog(values)
gc.deleteOldLogs()
