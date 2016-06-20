import json
import inspect

from elasticsearch import Elasticsearch, ElasticsearchException

from django.conf import settings
from django.core.management.base import BaseCommand


class FEELSError(BaseException):
    pass


def find_param(**kwargs):
    found_param = False
    for k in kwargs:
        if '__' in k:
            found_param = True
    return found_param


def validate_params(ops, name, check_params, **kwargs):
    # If there was one parameter, i.e. on argument
    # with a double underscore ('__') then all
    # arguments must be parameters; otherwise, if no
    # paramters were found, then we assume it's a
    # valid expression, for now.
    if check_params:
        for k in kwargs:
            if '__' not in k:
                raise FEELSError(
                    '{} "{}" is not an expression.'.format(name, k))
            name, op = k.split('__')
            if op not in ops:
                raise FEELSError(
                    '{} "{}" not supported.'.format(name, k))


def isintrinsic(x):
    '''Test if _x_ is a built-in type'''
    return (
        isinstance(x, str) or
        isinstance(x, int) or
        isinstance(x, float) or
        isinstance(x, dict))


def isintrinsiclist(x):
    '''Test if _x_ is a list containing built-in types'''
    return (
        isinstance(x, list) and
        len(x) > 0 and
        isintrinsic(x[0]))


def _extract_members(elements):
    '''Turn the members of a class in to a data structure'''
    results = None
    if isintrinsic(elements):
        # Built-in types are just passed back as is.
        results = elements
    elif isintrinsiclist(elements):
        # Lists of built-in types are also passed back as is.
        results = [e for e in elements]
    else:
        # ELS types are handled in a special way.
        results = []
        for e in elements:
            items = {}
            class_ = e.__class__
            class_name = class_.__name__
            # Extract the classes __init__ parameter list.
            kwargs = getattr(e, 'kwargs')
            for k in kwargs:
                if '__' in k:
                    # If one of the parameters has a '__' in it, we'll
                    # handle it as if it defines an expresson. For
                    # example, 'paramter__gt=0' will be parsed as the name
                    # 'parameter' and the expression '>0'.
                    name, op = k.split('__')
                    if class_name not in items:
                        items[class_name] = {}
                    if name not in items[class_name]:
                        items[class_name][name] = {}
                    items[class_name][name][op] = kwargs[k]
                else:
                    # Otherwise, just store the parameter by name.
                    items[class_name] = kwargs
            results.append(items)
    return results


def _build_query(cls):
    results = {}
    if cls:
        for name in dir(cls):
            # Ignore private members and those in the following list.
            ignore = ['build']
            if name[:2] != '__' and name not in ignore:
                attr = getattr(cls, name)
                if inspect.isclass(attr):
                    results[name] = _build_query(attr)
                else:
                    results[name] = _extract_members(attr)
    return results


class fe(object):

    class BaseQuery(object):
            @classmethod
            def build(cls):
                result = _build_query(cls)
                body = json.dumps(result, indent=2)
                return body

    class query(object):

        class term(object):
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                check_params = find_param(**kwargs)
                ops = ['value', 'boost']
                validate_params(ops, 'Term', check_params, **kwargs)

        class terms(object):
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                check_params = find_param(**kwargs)
                ops = ['index', 'type', 'id', 'path', 'routing']
                if check_params:
                    validate_params(ops, 'Terms', check_params, **kwargs)
                else:
                    # If there are no params, then we expect there to
                    # be one 'terms' where the paramter is a list.
                    if len(kwargs) > 1:
                        raise FEELSError(
                            'Terms supports only one list as a parameter.')
                    for k in kwargs:
                        if not isinstance(kwargs[k], list):
                            raise FEELSError(
                                'Terms parameter must be a list.')

        class range(object):
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                ops = ['gte', 'gt', 'lte', 'lt', 'boost']
                # Ranges will always need their parameters checked.
                validate_params(ops, 'Range', check_params=True, **kwargs)

        class geo_distance(object):
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                keys = ['distance', 'point', 'pin.location', 'distance_type']
                for k in kwargs:
                    if k not in keys:
                        raise FEELSError(
                            'GeoDistance "{}" is not valid.'.format(k))

        class sort(object):
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        #class extended_stats(object):
        #    def __init__(self, **kwargs):
        #        name = kwargs['name']
        #        self.kwargs = {
        #            name: {
        #                'extended_stats': {
        #                    'field': kwargs['field']
        #                }
        #            }
        #        }


def _get_parameter_group_numbers():
    parameter_group_numbers = [
        'Engine Coolant Temperature (C)',
        'Fuel Level (%)',
        'PTO RPM',
        'Engine Oil Pressure (kPa)',
        'Actual Engine - Percent Torque (%)',
        'Fuel Delivery Pressure (kPa)',
        'Instantaneous Liquid Fuel Usage (L/hour)',
        'velocity',
        'Engine RPM',
        'Engine Fuel Temperature (C)',
        'Wheel Based Speed (miles/hour)',
        'Grain Flow (kg/s)',
        'Grain Flow 1 (kg/s)',
        'Grain Flow 2 (kg/s)',
        'Grain Flow 3 (kg/s)',
        'Grain Moisture (%)',
    ]
    return parameter_group_numbers


class Command(BaseCommand):
    
    def handle(self, *args, **options):

        try:
            client = Elasticsearch(hosts=[settings.ELASTIC_SEARCH_HOST],
                                   http_auth=(settings.ELASTIC_SEARCH_USERNAME,
                                              settings.ELASTIC_SEARCH_PASSWORD))
        except ElasticsearchException as e:
            msg = 'Exception when connecting to Elastic Search: %s' % (e)
            print msg

        class SomeInterestingQuery(fe.BaseQuery):
            _source = [
                "coordinates",
                "growerId",
                "workingSets",
                "implement_type",
            ]
            size = 2
            sort = [
                {'date': {"order": "asc", "ignore_unmapped": True}}
            ]
            
            class query(object):
                class bool(object):
                    filter = [
                        fe.query.range(
                            workingSetCount__gt=0),
                    ]
                    
                    must = [
                        fe.query.term(canPlugId='B03150674'),
                        fe.query.term(dataType=1),
                    ]
                    
                    must_not = [
                        fe.query.geo_distance(
                            distance='1km',
                            point={'lat': 0, 'lon': 0},
                            distance_type='sloppy_arc'),
                    ]

        aggs = {}
        for name in _get_parameter_group_numbers():
            aggs[name] = {
                'extended_stats': {
                    'field': 'workingSets.%s' % (name),
                },
            }
        SomeInterestingQuery.aggs = aggs

        body = SomeInterestingQuery.build()
        print body
        
        response = client.search(index='canplug', body=body)
        print json.dumps(response, indent=2)
