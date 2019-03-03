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

term_val_spacing   = '    '

# Hardcoded values because I can't get tput to work properly in FreeNAS
term_color_bad     = '\x1b[30m' + '\x1b[41m'
term_color_warning = '\x1b[30m' + '\x1b[43m'
term_color_good    = '\x1b[30m' + '\x1b[42m'
term_color_unknown = '\x1b[30m' + '\x1b[44m'
term_color_default = '\x1b(B\x1b[m'
colors = {GOOD:term_color_good, WARN:term_color_warning, BAD:term_color_bad,
          UNKNOWN:term_color_unknown}

class column_maker:
    ' Generate the required paddings (spaces) for printing data aligned in n columns. '
    def __init__(self, columns, align_right = False):
        self._columns = columns
        self._strings = []
        self._max_len = []
        self._align_right = align_right
        for x in range(columns):
            self._max_len.append(0)

    def strings(self):
        return self._strings

    def append(self, s):
        index = len(self._strings) % self._columns
        self._strings.append(s)
        self._max_len[index] = max(self._max_len[index], len(s))

    def __len__(self):
        return len(self._strings)

    def __getitem__(self, index):
        s = self._strings[index]
        if self._align_right:
            return ' ' * (self._max_len[index % self._columns] - len(s)) + s
        else:
            return s + ' ' * (self._max_len[index % self._columns] - len(s))

    def __iter__(self):
        for i in range(len(self._strings)):
            yield self.__getitem__(i)


def print_smart_per_drive(smart, columns = 1, attribute_order = None, hdd_order = None):
    ''' smart = {'hdd_name':{smart values}, 'hdd_name':{smart values}, ...}
        columns = SMART attributes per line.
        attribute_order = Optional list of smart attribute ids.
        The smart values will be printed in this order.
        hdd_order = Optional list of hdd_names.
        The drives will be printed in this order'''

    if not hdd_order:
        hdd_order = list(smart)
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
        out = column_maker(columns)
        for i in range(len(attribute_order)):
            val = attribute_order[i]
            attr = smart[name][val]
            if attr.get('value'):
                out.append(colors[attr['status']] + attr['name'] + ': ' + attr['value'])
            else:
                out.append(colors[UNKNOWN] + attr['name'] + '???')

        line = ''
        count = 0
        for i in range(len(out)):
            line += out[i] + term_color_default + term_val_spacing
            count += 1
            if count % columns == 0:
                print(line)
                line = ''

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
        hdd_order = list(smart)
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
        out_attr = column_maker(columns)
        out_val  = column_maker(columns, True)

        for name in hdd_order:
            attr = smart[name].get(val)
            if attr.get('value'):
                out_attr.append(colors[attr['status']] + name)
                out_val.append(attr['value'])
            else:
                out_attr.append(colors[UNKNOWN] + name)
                out_val.append('???')

        line = ''
        count = 0
        for i in range(len(out_attr)):
            line += out_attr[i] + ': ' + out_val[i] + term_color_default + term_val_spacing
            count += 1
            if count % columns == 0:
                print(line)
                line = ''

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
