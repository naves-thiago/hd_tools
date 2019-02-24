''' Module for reading SMART attribute values from hard drives. Requires smartctl.'''

import subprocess

def read_smart(dev):
    s = subprocess.Popen(['smartctl', '-A', dev], stdout=subprocess.PIPE).stdout.read()
    s = s.decode('utf-8')

    lines = s.split('\n')
    header = lines[6]
    global positions
    positions = []
    positions.append(header.find('ID#'))
    positions.append(header.find('ATTRIBUTE_NAME'))
    positions.append(header.find('FLAG'))
    positions.append(header.find('VALUE'))
    positions.append(header.find('WORST'))
    positions.append(header.find('THRESH'))
    positions.append(header.find('TYPE'))
    positions.append(header.find('UPDATED'))
    positions.append(header.find('WHEN_FAILED'))
    positions.append(header.find('RAW_VALUE'))
    out = {}
    for l in lines[7:-1]:
        if l.strip() != '':
            attr = _split_smart_line(l)
            out[attr['id']] = attr

    return out

def _split_smart_line(line):
    out = {}
    out['id']          = int(line[positions[0]:positions[1]].strip())
    out['name']        = attribute_name.get(out['id'], '???')
    out['flag']        = line[positions[2]:positions[3]].strip()
    out['value']       = line[positions[3]:positions[4]].strip()
    out['worst']       = line[positions[4]:positions[5]].strip()
    out['threshold']   = line[positions[5]:positions[6]].strip()
    out['type']        = line[positions[6]:positions[7]].strip()
    out['updated']     = line[positions[7]:positions[8]].strip()
    out['when_failed'] = line[positions[8]:positions[9]].strip()
    raw                = line[positions[9]:].strip()

    if raw.find(' ') > -1:
        raw = raw[:raw.find(' ')]

    out['raw'] = raw
    return out

attribute_name = {
    1:'Read Error Rate',
    2:'Throughput Performance',
    3:'Spin-Up Time',
    4:'Start/Stop Count',
    5:'Reallocated Sectors Count',
    6:'Read Channel Margin',
    7:'Seek Error Rate',
    8:'Seek Time Performance',
    9:'Power-On Hours',
    10:'Spin Retry Count',
    11:'Recalibration Retries',
    12:'Power Cycle Count',
    13:'Soft Read Error Rate',
    22:'Current Helium Level',
    170:'Available Reserved Space',
    171:'SSD Program Fail Count',
    172:'SSD Erase Fail Count',
    173:'SSD Wear Leveling Count',
    174:'Unexpected power loss count',
    175:'Power Loss Protection Failure',
    176:'Erase Fail Count',
    177:'Wear Range Delta',
    179:'Used Reserved Block Count Total',
    180:'Unused Reserved Block Count Total',
    181:'Program Fail Count Total or Non-4K Aligned Access Count',
    182:'Erase Fail Count',
    183:'SATA Downshift Error Count or Runtime Bad Block',
    184:'End-to-End error',
    185:'Head Stability',
    186:'Induced Op-Vibration Detection',
    187:'Reported Uncorrectable Errors',
    188:'Command Timeout',
    189:'High Fly Writes',
    190:'Airflow Temperature',
    191:'G-sense Error Rate',
    192:'Unsafe Shutdown Count',
    193:'Load Cycle Count',
    194:'Temperature Celsius',
    195:'Hardware ECC Recovered',
    196:'Reallocation Event Count',
    197:'Current Pending Sector Count',
    198:'Offline Uncorrectable Sector Count',
    199:'UltraDMA CRC Error Count',
    200:'Multi-Zone Error Rate',
    201:'Soft Read Error Rate',
    202:'Data Address Mark errors',
    203:'Run Out Cancel',
    204:'Soft ECC Correction',
    205:'Thermal Asperity Rate',
    206:'Flying Height',
    207:'Spin High Current',
    208:'Spin Buzz',
    209:'Offline Seek Performance',
    210:'Vibration During Write',
    211:'Vibration During Write',
    212:'Shock During Write',
    220:'Disk Shift',
    221:'G-Sense Error Rate',
    222:'Loaded Hours',
    223:'Load/Unload Retry Count',
    224:'Load Friction',
    225:'Load/Unload Cycle Count',
    226:'Load \'In\'-time',
    227:'Torque Amplification Count',
    228:'Power-Off Retract Cycle',
    230:'GMR Head Amplitude or Drive Life Protection Status (SSDs)',
    231:'Life Left (SSDs) or Temperature',
    232:'Endurance Remaining',
    233:'Media Wearout Indicator (SSDs) or Power-On Hours',
    234:'Average erase count AND Maximum Erase Count',
    235:'Good Block Count AND System(Free) Block Count',
    240:'Head Flying Hours or Transfer Error Rate',
    241:'Total LBAs Written',
    242:'Total LBAs Read',
    243:'Total LBAs Written Expanded',
    244:'Total LBAs Read Expanded',
    249:'NAND Writes (1GiB)',
    250:'Read Error Retry Rate',
    251:'Minimum Spares Remaining',
    252:'Newly Added Bad Flash Block',
    254:'Free Fall Protection',
}

def __smart_mock():
    return '''smartctl 6.3 2014-07-26 r3976 [FreeBSD 9.3-RELEASE-p16 amd64] (local build)
Copyright (C) 2002-14, Bruce Allen, Christian Franke, www.smartmontools.org

=== START OF READ SMART DATA SECTION ===
SMART Attributes Data Structure revision number: 10
Vendor Specific SMART Attributes with Thresholds:
ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
  1 Raw_Read_Error_Rate     0x000f   119   100   006    Pre-fail  Always       -       233506248
  3 Spin_Up_Time            0x0003   095   095   000    Pre-fail  Always       -       0
  4 Start_Stop_Count        0x0032   100   100   020    Old_age   Always       -       34
  5 Reallocated_Sector_Ct   0x0033   100   100   010    Pre-fail  Always       -       0
  7 Seek_Error_Rate         0x000f   070   060   030    Pre-fail  Always       -       10893010
  9 Power_On_Hours          0x0032   100   100   000    Old_age   Always       -       422
 10 Spin_Retry_Count        0x0013   100   100   097    Pre-fail  Always       -       0
 12 Power_Cycle_Count       0x0032   100   100   020    Old_age   Always       -       34
183 Runtime_Bad_Block       0x0032   100   100   000    Old_age   Always       -       0
184 End-to-End_Error        0x0032   100   100   099    Old_age   Always       -       0
187 Reported_Uncorrect      0x0032   100   100   000    Old_age   Always       -       0
188 Command_Timeout         0x0032   100   100   000    Old_age   Always       -       0 0 0
189 High_Fly_Writes         0x003a   099   099   000    Old_age   Always       -       1
190 Airflow_Temperature_Cel 0x0022   065   058   045    Old_age   Always       -       35 (Min/Max 23/35)
191 G-Sense_Error_Rate      0x0032   100   100   000    Old_age   Always       -       0
192 Power-Off_Retract_Count 0x0032   100   100   000    Old_age   Always       -       2
193 Load_Cycle_Count        0x0032   100   100   000    Old_age   Always       -       81
194 Temperature_Celsius     0x0022   035   042   000    Old_age   Always       -       35 (0 23 0 0 0)
197 Current_Pending_Sector  0x0012   100   100   000    Old_age   Always       -       0
198 Offline_Uncorrectable   0x0010   100   100   000    Old_age   Offline      -       0
199 UDMA_CRC_Error_Count    0x003e   200   200   000    Old_age   Always       -       0
240 Head_Flying_Hours       0x0000   100   253   000    Old_age   Offline      -       422h+13m+26.772s
241 Total_LBAs_Written      0x0000   100   253   000    Old_age   Offline      -       11376810357
242 Total_LBAs_Read         0x0000   100   253   000    Old_age   Offline      -       211017862927

'''
