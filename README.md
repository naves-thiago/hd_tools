# HD Tools
This ~~is~~ wil be  a collection of tools related to testing and monitoring hard drives.
These tools are written in python3.

## Test HD
This tool is used to stress test the disk by writing random data to random sectors and verifying afterwards.  
Current version assumes 4096 bytes sectors and writes 10000 sectors, reporting any sectors that fail verification.  
__Data on the drive will be overwritten. Do not use this on a drive containing data.__  
Usage `python3 test_hd.py /dev/sdX` where `/dev/sdX` is the drive to test.  
This tool was only tested on linux.  
