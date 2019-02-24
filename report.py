import subprocess
from argparse import ArgumentParser
from modules.smart import read_smart, attribute_name

# SMART value status
GOOD    = 0
WARN    = 1
BAD     = 2
UNKNOWN = 3
positions = []

def check_drive(dev, raw_limits):
    ''' dev = '/dev/ada0'
        raw_limits = {attribute id:[WARN threshold, BAD threshold], 5:[0, 0], 10:[50, 100], ...}
        output = {attribute id:{status:GOOD | WARN | BAD,
                                name:'Attribute name',
                                raw_value:SMART value},
                  attribute id:{...}
                 }'''

    out = {}
    smart = read_smart(dev)

    for attr in raw_limits:
        out[attr] = {'name':attribute_name.get(attr, '???')}
        if attr in smart:
            raw = int(smart[attr]['raw'])
            out[attr]['value'] = smart[attr]['raw']
            if smart[attr]['when_failed'] != '-':
                # Drive reported failure
                out[attr]['status'] = BAD
            elif raw > raw_limits[attr][1]:
                # Above higher threshold
                out[attr]['status'] = BAD
            elif raw > raw_limits[attr][0]:
                # Above lower threshold
                out[attr]['status'] = WARN
            else:
                out[attr]['status'] = GOOD

    return out

def tput(*params):
    tmp = ['tput']
    tmp.extend(params)
    return subprocess.Popen(tmp, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

term_val_spacing   = '    '
term_val_border    = '  '

# Hardcoded values because I can't get tput to work properly in FreeNAS
term_color_bad     = '\x1b[30m' + '\x1b[41m'
term_color_warning = '\x1b[30m' + '\x1b[43m'
term_color_good    = '\x1b[30m' + '\x1b[42m'
term_color_unknown = '\x1b[30m' + '\x1b[44m'
term_color_default = '\x1b(B\x1b[m'

#term_color_bad     = tput('setaf', '0') + tput('setab', '1') # Black on Red
#term_color_warning = tput('setaf', '0') + tput('setab', '3') # Black on Yellow
#term_color_good    = tput('setaf', '0') + tput('setab', '2') # Black on Green
#term_color_unknown = tput('setaf', '0') + tput('setab', '4') # Black on Green
#term_color_default = tput('sgr0')                            # Default colors

def format_val(name, val, color):
    colors = {GOOD:term_color_good, WARN:term_color_warning, BAD:term_color_bad,
              UNKNOWN:term_color_unknown}
    return colors[color] + term_val_border + name + ': ' + val + term_val_border + term_color_default

def print_smart_per_drive(smart, columns = 1, attribute_order = None, hdd_order = None):
    ''' smart = {'hdd_name':{smart values}, 'hdd_name':{smart values}, ...}
        columns = SMART attributes per line.
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
            return hd0[v]['name']
        attribute_order = list(hd0)
        attribute_order.sort(key = sort_key)

    for name in hdd_order:
        print(name)
        line = ''
        count = 0
        for val in attribute_order:
            attr = smart[name][val]
            if attr.get('value'):
                line += format_val(attr['name'], attr['value'], attr['status'])
            else:
                line += format_val(attr['name'], '???', UNKNOWN)
            count += 1
            if count % columns == 0 or count == len(attribute_order):
                print(line)
                line = ''
            else:
                line += term_val_spacing
        if line != '':
            print(line)

        print('')

def print_smart_per_attribute(smart, columns = 1, attribute_order = None, hdd_order = None):
    ''' smart = {'hdd_name':{smart values}, 'hdd_name':{smart values}, ...}
        columns = Drives per line.
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
            return hd0[v]['name']
        attribute_order = list(hd0)
        attribute_order.sort(key = sort_key)

    for val in attribute_order:
        attr = hd0[val]
        print(attr['name'])
        line = ''
        count = 0
        for name in hdd_order:
            attr = smart[name].get(val)
            if attr.get('value'):
                line += format_val(name, attr['value'], attr['status'])
            else:
                line += format_val(name, '???', UNKNOWN)

            count += 1
            if count % columns == 0 or count == len(attribute_order):
                print(line)
                line = ''
            else:
                line += term_val_spacing
        if line != '':
            print(line)

        print('')

parser = ArgumentParser(description='Check drives\' SMART attributes against "warning" and "bad" thresholds. '
                                    'Output color coded in green, yellow or red representing a good / warning / bad value.')
parser.add_argument('disks', metavar='disk', type=str, nargs='+', help='Disks to check')
parser.add_argument('-d', '--perdrive', action='store_true', dest='perdrive',
                    help='Group output per drive instead of per SMART attribute')
parser.add_argument('-c', '--columns', metavar='N', type=int, default=1, help='Output column count (default 1)')
opts = parser.parse_args()

limits = {4:[1000, 2000],
          5:[0, 5],
          9:[20000, 40000],
          187:[0,5],
          194:[35, 41],
          197:[0,3],
          198:[0,3],
}
smart = {}
for dev in opts.disks:
    smart[dev] = check_drive(dev, limits)

if opts.perdrive:
    print_smart_per_drive(smart, opts.columns)
else:
    print_smart_per_attribute(smart, opts.columns)
