
import re
from rpython.tool import logparser

log = logparser.parse_log_file("log")
log = logparser.extract_category(log, "jit-log-opt")
d = {}
counted = 0
not_counted = 0
result = {}
for item in log:
    first = item.split("\n")[0]
    if '# Loop' in first:
        m = re.search("<code object (.*), file '(.*)', line (\d+)", first)
        if not m:
            continue
        key = (m.group(1), m.group(2), int(m.group(3)))
        for i, op in enumerate(item.split("\n")[2:-1]):
            if 'guard_' in op:
                m = re.search("descr=<Guard(0x[0-9a-f]+)>", op)
                d[int(m.group(1), 16)] = (key, i)
                #print op, i, int(m.group(1), 16)
    else:
        m = re.search("bridge out of Guard (0x[a-f0-9]+)", first)
        bridge_no = int(m.group(1), 16)
        if bridge_no in d:
            result.setdefault(d[bridge_no][0], []).append((bridge_no, d[bridge_no][1]))
        else:
            not_counted += 1
        for i, op in enumerate(item.split("\n")[2:-1]):
            if 'guard_' in op:
                m = re.search("descr=<Guard(0x[0-9a-f]+)>", op)
                d[int(m.group(1), 16)] = (bridge_no, i)
print not_counted

#print counted, not_counted
open("tracebridge.py", "w").write("trace_bridge = " + repr(result))
