# HD Tools
This is a collection of tools related to testing and monitoring hard drives.  
These tools are written in python3.

## Test HD
This tool is used to stress test the disk by writing random data to random sectors and verifying afterwards.  
Current version assumes 4096 bytes sectors and writes 10000 sectors, reporting any sectors that fail verification.  
__Data on the drive will be overwritten. Do not use this on a drive containing data.__  
Usage `python3 test_hd.py /dev/sdX` where `/dev/sdX` is the drive to test.  
This tool was only tested on linux.  

## Report
This tool reports the selected SMART values for a list of drives. The output can be grouped by drive or SMART attribute (default).  
For each attribute a "warning" and a "bad" thresholds are defined. Each value output is colored in green, yellow or red representing a good, warning or bad value.  
Configured SMART attributes and thresholds:

| ID  | Name                     | Warning |  Bad  |
|-----|--------------------------|---------|-------|
|  4  | Start Stop Count         | 1000    | 2000  |
|  5  | Reallocated Sector Count | 0       | 5     |
|  9  | Power on Hours           | 20000   | 40000 |
| 187 | Reported Uncorrectable   | 0       | 5     |
| 190 | Airflow Temperature      | 35      | 41    |
| 197 | Current Pending Sector   | 0       | 3     |
| 198 | Offline Uncorrectable    | 0       | 3     |

Currently this script will check `/dev/ada0` through `/dev/ada3`.  
Usage: `python3 report.py`
