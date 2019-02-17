import subprocess

# SMART value status
GOOD = 0
WARN = 1
BAD  = 2
positions = []

def read_smart(dev):
    s = subprocess.Popen(["smartctl", "-A", dev], stdout=subprocess.PIPE).stdout.read()
    s = s.decode("utf-8")
#    s = """smartctl 6.3 2014-07-26 r3976 [FreeBSD 9.3-RELEASE-p16 amd64] (local build)
#Copyright (C) 2002-14, Bruce Allen, Christian Franke, www.smartmontools.org
#
#=== START OF READ SMART DATA SECTION ===
#SMART Attributes Data Structure revision number: 10
#Vendor Specific SMART Attributes with Thresholds:
#ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
#  1 Raw_Read_Error_Rate     0x000f   119   100   006    Pre-fail  Always       -       233506248
#  3 Spin_Up_Time            0x0003   095   095   000    Pre-fail  Always       -       0
#  4 Start_Stop_Count        0x0032   100   100   020    Old_age   Always       -       34
#  5 Reallocated_Sector_Ct   0x0033   100   100   010    Pre-fail  Always       -       0
#  7 Seek_Error_Rate         0x000f   070   060   030    Pre-fail  Always       -       10893010
#  9 Power_On_Hours          0x0032   100   100   000    Old_age   Always       -       422
# 10 Spin_Retry_Count        0x0013   100   100   097    Pre-fail  Always       -       0
# 12 Power_Cycle_Count       0x0032   100   100   020    Old_age   Always       -       34
#183 Runtime_Bad_Block       0x0032   100   100   000    Old_age   Always       -       0
#184 End-to-End_Error        0x0032   100   100   099    Old_age   Always       -       0
#187 Reported_Uncorrect      0x0032   100   100   000    Old_age   Always       -       0
#188 Command_Timeout         0x0032   100   100   000    Old_age   Always       -       0 0 0
#189 High_Fly_Writes         0x003a   099   099   000    Old_age   Always       -       1
#190 Airflow_Temperature_Cel 0x0022   065   058   045    Old_age   Always       -       35 (Min/Max 23/35)
#191 G-Sense_Error_Rate      0x0032   100   100   000    Old_age   Always       -       0
#192 Power-Off_Retract_Count 0x0032   100   100   000    Old_age   Always       -       2
#193 Load_Cycle_Count        0x0032   100   100   000    Old_age   Always       -       81
#194 Temperature_Celsius     0x0022   035   042   000    Old_age   Always       -       35 (0 23 0 0 0)
#197 Current_Pending_Sector  0x0012   100   100   000    Old_age   Always       -       0
#198 Offline_Uncorrectable   0x0010   100   100   000    Old_age   Offline      -       0
#199 UDMA_CRC_Error_Count    0x003e   200   200   000    Old_age   Always       -       0
#240 Head_Flying_Hours       0x0000   100   253   000    Old_age   Offline      -       422h+13m+26.772s
#241 Total_LBAs_Written      0x0000   100   253   000    Old_age   Offline      -       11376810357
#242 Total_LBAs_Read         0x0000   100   253   000    Old_age   Offline      -       211017862927
#
#"""

    lines = s.split("\n")

    header = lines[6]
    global positions
    positions = []
    positions.append(header.find("ID#"))
    positions.append(header.find("ATTRIBUTE_NAME"))
    positions.append(header.find("FLAG"))
    positions.append(header.find("VALUE"))
    positions.append(header.find("WORST"))
    positions.append(header.find("THRESH"))
    positions.append(header.find("TYPE"))
    positions.append(header.find("UPDATED"))
    positions.append(header.find("WHEN_FAILED"))
    positions.append(header.find("RAW_VALUE"))
    out = []
    for l in lines[7:-1]:
        if l.strip() != "":
            out.append(l)

    return out

def split_smart_line(line):
    out = {}
    out["id"]          = int(line[positions[0]:positions[1]].strip())
    out["name"]        = line[positions[1]:positions[2]].strip()
    out["flag"]        = line[positions[2]:positions[3]].strip()
    out["value"]       = line[positions[3]:positions[4]].strip()
    out["worst"]       = line[positions[4]:positions[5]].strip()
    out["threshold"]   = line[positions[5]:positions[6]].strip()
    out["type"]        = line[positions[6]:positions[7]].strip()
    out["updated"]     = line[positions[7]:positions[8]].strip()
    out["when_failed"] = line[positions[8]:positions[9]].strip()
    raw                = line[positions[9]:].strip()

    if raw.find(" ") > -1:
        raw = raw[:raw.find(" ")]

    out["raw"] = raw
    return out

def check_drive(dev, raw_limits):
    ''' dev = "/dev/ada0"
        raw_limits = {attribute id:[WARN threshold, BAD threshold], 5:[0, 0], 10:[50, 100], ...}
        output = {attribute id:{status:GOOD | WARN | BAD,
                                name:"Attribute name",
                                raw_value:SMART value},
                  attribute id:{...}
                 }'''

    out = {}
    smart = read_smart(dev)

    for line in smart:
        values = split_smart_line(line)
        if values["id"] in raw_limits:
            out[values["id"]] = {"name":values["name"], "value":values["raw"]}
            if values["when_failed"] != "-":
                # Drive reported failure
                out[values["id"]]["status"] = BAD
            elif int(values["raw"]) > raw_limits[values["id"]][1]:
                # Above higher threshold
                out[values["id"]]["status"] = BAD
            elif int(values["raw"]) > raw_limits[values["id"]][0]:
                # Above lower threshold
                out[values["id"]]["status"] = WARN
            else:
                out[values["id"]]["status"] = GOOD

    return out

def tput(*params):
    tmp = ["tput"]
    tmp.extend(params)
    return subprocess.Popen(tmp, stdout=subprocess.PIPE).stdout.read().decode("utf-8")

term_val_spacing   = "    "
term_val_border    = "  "

# Hardcoded values because I can't get tput to work properly in FreeNAS
term_color_bad     = "\x1b[30m" + "\x1b[41m"
term_color_warning = "\x1b[30m" + "\x1b[43m"
term_color_good    = "\x1b[30m" + "\x1b[42m"
term_color_default = "\x1b(B\x1b[m"

#term_color_bad     = tput("setaf", "0") + tput("setab", "1") # Black on Red
#term_color_warning = tput("setaf", "0") + tput("setab", "3") # Black on Yellow
#term_color_good    = tput("setaf", "0") + tput("setab", "2") # Black on Green
#term_color_default = tput("sgr0")                            # Default colors

def format_val(name, val, color):
    colors = {GOOD:term_color_good, WARN:term_color_warning, BAD:term_color_bad}
    return colors[color] + term_val_border + name + ": " + val + term_val_border + term_color_default

def print_smart_per_drive(smart, attribute_order = None, hdd_order = None):
    ''' smart = {"hdd_name":{smart values}, "hdd_name":{smart values}, ...}
        attribute_order = Optional list of smart attribute ids.
        The smart values will be printed in this order.
        hdd_order = Optional list of hdd_names.
        The drives will be printed in this order'''

    if not hdd_order:
        hdd_order = list(smart.keys())
        hdd_order.sort()

    if not attribute_order:
        # Sort attributes by name
        hd0 = smart[next(iter(smart))]
        def sort_key(v):
            return hd0[v]["name"]
        attribute_order = list(hd0)
        attribute_order.sort(key = sort_key)

    values_per_line = 1
    for name in hdd_order:
        print(name)
        line = ""
        count = 0
        for val in attribute_order:
            attr = smart[name][val]
            line += format_val(attr["name"], attr["value"], attr["status"])
            count += 1
            if count % values_per_line == 0 or count == len(attribute_order):
                print(line)
                line = ""
            else:
                line += term_val_spacing
        if line != "":
            print(line)

        print("")

def print_smart_per_attribute(smart, attribute_order = None, hdd_order = None):
    ''' smart = {"hdd_name":{smart values}, "hdd_name":{smart values}, ...}
        attribute_order = Optional list of smart attribute ids.
        The smart values will be printed in this order.
        hdd_order = Optional list of hdd_names.
        The drives will be printed in this order'''

    if not hdd_order:
        hdd_order = list(smart.keys())
        hdd_order.sort()

    hd0 = smart[next(iter(smart))]
    if not attribute_order:
        # Sort attributes by name
        def sort_key(v):
            return hd0[v]["name"]
        attribute_order = list(hd0)
        attribute_order.sort(key = sort_key)

    values_per_line = 4
    for val in attribute_order:
        attr = hd0[val]
        print(attr["name"])
        line = ""
        count = 0
        for name in hdd_order:
            attr = smart[name][val]
            line += format_val(name, attr["value"], attr["status"])
            count += 1
            if count % values_per_line == 0 or count == len(attribute_order):
                print(line)
                line = ""
            else:
                line += term_val_spacing
        if line != "":
            print(line)

        print("")

drives =  ["/dev/ada" + str(x) for x in range(4)]
limits = {4:[1000, 2000],
          5:[0, 5],
          9:[20000, 40000],
          187:[0,5],
          190:[35, 41],
          197:[0,3],
          198:[0,3]
}
smart = {}
for dev in drives:
    smart[dev] = check_drive(dev, limits)

#print_smart_per_drive(smart)
print_smart_per_attribute(smart)
