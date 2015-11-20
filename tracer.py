
import atexit
import __pypy__
import pypyjit
import re

class Tracer(object):
    def __init__(self):
        d = {}
        try:
            exec open("tracedata.py").read() in d
        except (OSError, IOError):
            pass
        self._trace_too_long_set = d.get('trace_too_long', set())
        self._trace_immediately = d.get('trace_immediately', {})
        try:
            exec open("tracebridge.py").read() in d
        except (OSError, IOError):
            pass
        self._trace_bridges = d.get('trace_bridge', {})
        self._lookup = {}

    def trace_too_long(self, jd_name, key):
        self._trace_too_long_set.add(hash(key[0]))

    def code_callback(self, code):
        if hash(code) in self._trace_too_long_set:
            pypyjit.dont_trace_here(0, False, code)
        if hash(code) in self._trace_immediately:
            for v in self._trace_immediately[hash(code)]:
                pypyjit.trace_next_iteration(v, False, code)

    def on_compile(self, loopinfo):
        gkey = loopinfo.greenkey
        if gkey is not None and loopinfo.jitdriver_name == 'pypyjit':
            if hash(gkey[0]) in self._trace_immediately:
                self._trace_immediately[hash(gkey[0])].add(gkey[1])
            else:
                self._trace_immediately[hash(gkey[0])] = set([gkey[1]])
            key = gkey[0].co_name, gkey[0].co_filename, gkey[0].co_firstlineno
            if key in self._trace_bridges:
                s = {}
                for k, v in self._trace_bridges[key]:
                    s[v] = k
                for i, op in enumerate(loopinfo.operations):
                    if i in s:
                        if 'guard' in repr(op):
                            pypyjit.trace_next_iteration_hash(op.hash)
                            m = re.search('Guard(0x[0-9a-f]+)', repr(op))
                            self._lookup[int(m.group(1), 16)] = s[i]
        elif loopinfo.jitdriver_name == 'pypyjit':
            if loopinfo.bridge_no in self._lookup:
                key = self._lookup[loopinfo.bridge_no]
                if key in self._trace_bridges:
                    s = {}
                    for k, v in self._trace_bridges[key]:
                        s[v] = k
                    for i, op in enumerate(loopinfo.operations):
                        if i in s:
                            if 'guard' in repr(op):
                                pypyjit.trace_next_iteration_hash(op.hash)
                                m = re.search('Guard(0x[0-9a-f]+)', repr(op))
                                self._lookup[int(m.group(1), 16)] = s[i]
                    
            #print self._lookup[loopinfo.bridge_no] in self._trace_bridges
#            self._trace_bridges[(hash(gkey[0]), gkey[1])] = set()
            #import pdb
            #pdb.set_trace()
#        else:
#            print loopinfo.bridge_no

    def finish(self):
        with open("tracedata.py", "w") as f:
            f.write("trace_too_long = set([")
            for k in self._trace_too_long_set:
                f.write(repr(k) + ", ")
            f.write("])\n")
            f.write("trace_immediately = {}\n")
            for k, v in self._trace_immediately.iteritems():
                f.write("trace_immediately[%d] = set([%s])\n" %
                        (k, ", ".join([repr(x) for x in v])))

tracer = Tracer()

pypyjit.set_trace_too_long_hook(tracer.trace_too_long)
pypyjit.set_compile_hook(tracer.on_compile, operations=True)
__pypy__.set_code_callback(tracer.code_callback)

atexit.register(tracer.finish)
