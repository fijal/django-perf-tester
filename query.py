
import os, sys
import tracer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_perf_test.settings')
import django
django.setup()

from fooapp.models import Question, Choice
from datetime import datetime, timedelta
from django.utils.timezone import utc

def f():
    from django.db.models.sql.query import Query, JoinPromoter
    from django.db.models.sql.compiler import SQLCompiler
    from django.db.models import query
    from django.db.models.manager import Manager
    from collections import Counter
    from django.utils import timezone
    from django.db.models.fields import Field
    from abc import ABCMeta
    import pypyjit

    def disable(obj):
        if hasattr(obj, 'im_func'):
            obj = obj.im_func
        pypyjit.dont_trace_here(0, False, obj.__code__)

    disable(SQLCompiler.results_iter)
    #disable(Manager.manager_method)
    disable(query.QuerySet.filter)
    disable(timezone.is_aware)
    disable(Field.get_db_prep_lookup)
    #pypyjit.dont_trace_here(0, False, Query.build_lookup.im_func.__code__)
    #pypyjit.dont_trace_here(0, False, Query.setup_joins.im_func.__code__)
    #pypyjit.dont_trace_here(0, False, Query.build_filter.im_func.__code__)
    #pypyjit.dont_trace_here(0, False, Query.solve_lookup_type.im_func.__code__)
    #pypyjit.dont_trace_here(0, False, Query.add_q.im_func.__code__)
    #pypyjit.dont_trace_here(0, False, JoinPromoter.add_votes.im_func.__code__)
    #pypyjit.dont_trace_here(0, False, Query._add_q.im_func.__code__)
    #pypyjit.dont_trace_here(0, False, Query.clone.im_func.__code__)
    #pypyjit.dont_trace_here(0, False, query.QuerySet.filter.im_func.__code__)
    #pypyjit.dont_trace_here(0, False, Counter.update.im_func.__code__)
    #pypyjit.dont_trace_here(0, False, ABCMeta.__instancecheck__.im_func.__code__)
#f()

def main():
    import time
    t0 = time.time()
    d0 = datetime(2015, 10, 21, 0, 0, 15, tzinfo=utc)
    d1 = datetime(2015, 10, 21, 0, 0, 30, tzinfo=utc)
    for i in xrange(int(sys.argv[1])):
        # make sure we exhaust the iterators
        [x for x in Question.objects.filter(pub_date__gte=d0, pub_date__lt=d1).all()]
    print time.time() - t0

if __name__ == '__main__':
    main()
