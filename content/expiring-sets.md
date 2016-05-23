Title: Time Expired Sets Using Redis
Date: 2016-05-21 5:00
Status: published
Category: Programming
Tags: Python, Redis, Data Structures
Slug: expiring-sets
Authors: Ben Burnett
Summary: Redis-driven sets expired by time.

[Redis](http://redis.io) is an open-source (or free software) server
for managing in-memory data structures. It provides native support for
a variety of data structures, including strings, lists, (sorted) sets,
etc. It can be used in a variety of situations, such as providing fast
look-ups in a cached environment.

While Redis supports timeouts for keys, given a time-to-live (TTL), it
does not provide support for timeouts on the values of a key. The
purpose of this article is to explore option that enable such
behavior.

There are a variety of ways in which we can extract this behavior
from Redis. We will focus on two such methods.

## List of keys

First, we can use a list of key names and a set of keys that can be
expired, with the values attached to them.

Consider the following:

```
LPUSH list "key1"
LPUSH list "key2" # list now contains "key1","key2"
...
SET key1 "Hello,"
EXPIRE key1 10
SET key2 "World!"
EXPIRE key2 10
...
```

Here we create at least two keys, one for the list of keys considered
and one for each value we want to store and eventually
expire. Consider `key1` as an example: it is referenced in `list` and
is given the value of `"Hello,"` with a TTL of `10`.

Notice this method requires additional book-keeping to remove keys
from `list` after they have expired. Detecting when a key has expired
can be done as follows:

```
TTL key1
```

Before `key1` has expired, the `TTL` command will return the TTL it
was originally assigned. When `key1` has expired, the `TTL` command
will return `-1`. Iterating over `list` and executing `TTL` on the
values results in a new list with only the values that have not yet
expired.

The complexity for the book-keeping in this implementation is *O(N)*,
where *N* is the number of elements in `list`.

## Sorted Set

The second method uses a sorted set and is slightly more
complex. Recall that sorted sets contain a score and a value (possibly
the score itself). Our implementation uses a score and a single value
per entry.

Consider the following:

```
ZADD sset 4 "Hello,"
ZADD sset 5 "World!"
ZADD sset 2 "How"
ZADD sset 1 "are"
ZADD sset 3 "you?"
...
ZRANGE sset 0 -1 WITHSCORES # returns all elements in sset
1) "are"
2) "How"
...
```

This creates a sorted set containing
`"are","How","you?","Hello,","World!"`, with their respective
scores. Notice the values are not in the same order in which they were
added.  This is due to the way `ZSET` and sorted sets, in general,
work. A sorted set stores its values by score, rather than insertion
order.

To expire elements in this implementation we perform the following:

```
ZREMRANGEBYSCORE sset -inf 3
```

Where `-inf` is is the lowest possible score in the sorted set `sset`
and `3` asks for the removal of every element with a score of `3` or
less.

Notice that, again, we need additional book-keeping to remove keys
from `sset` that have expired. Book-keeping in this instance requires
*O((log N)+M)*, where *N* is the number of elements in `sset` and *M*
is the number elements being expired. Also note that this style of
book-keeping requires substantially less logic work than the one
required by the list implementation.

## An Example

So why is all of this useful?

Consider the case where you want to expire a set of values after a
certain amount of time has past. This might be useful when caching a
data-set that becomes less and less interesting over time. For
example, we might want to know the state of server over last
hour. This might include the load average or the average number of
page faults.

We need a number of data points for this to work: a timestamp of when
the measurement was taken and the values seen at that point in time.

Consider the following:

```
ZADD srvstats 1463879868 "{load:1.05,faults:1}"
ZADD srvstats 1463880018 "{load:1.05,faults:4}"
ZADD srvstats 1463880168 "{load:1.15,faults:3}"
ZADD srvstats 1463880318 "{load:1.14,faults:2}"
ZADD srvstats 1463880468 "{load:1.06,faults:5}"
...
```

Where `1463879868` is a timestamp for the measurement and `load` and
`faults` are the data points we are interested in.

Imagine we want to expire values after two minutes. This requires a
trivial calculation: let **TTL** be 120 (two minutes in seconds) and
**now** be `1463880468`. Furthermore, let **upper** be **(now -
TTL)**, or `1463880339`. To expire those values older than two
minutes, we perform the following operation:

```
ZREMRANGEBYSCORE sset -inf 1463880339
```

Isn't that cute?

### Python Implementation

Imagine we would prefer a less verbose approach. We can implement the
above using Python and the
[redis-py](https://redis-py.readthedocs.io/en/latest/) package. The
package exposes a set of thin wrappers around the Redis API.

If we wanted to re-create the expiring priority set example we saw
above, we could use the following `redis-py` powered code:

    #!python
    class ExpiringSet(object):

        def __init__(self, ttl, ...):
            self.ttl = ttl
            ...

        def push(self, value, score=None, unique=False):
            '''Add an element with a given score'''
            score = now() if not score else score
            with self.redis.pipeline() as pipe:
                pipe.zremrangebyscore(self.key, 0, now() - self.ttl)
                if unique:
                    pipe.zremrangebyscore(self.key, score, score)
                pipe.zadd(self.key, self._pack(value), score)
                results = pipe.execute()
                return results

        def elements(self):
            """Return all elements as a Python list"""
            self.redis.zremrangebyscore(self.key, 0, now() - self.ttl)
            return [self._unpack(i) for i in self.redis.zrange(self.key, 0, -1)]
         
        ...

This code is based on the `PriorityQueue` class in the wonderfully
written [qr](https://github.com/tnm/qr) package. The code itself is
hardly rocket-science, but we will step through it regardless.

Consider the `push` method. It takes one required parameter, `value`,
and two optional parameters, `score` and `unique`. If no score is
given, the current time is used; element uniqueness is not enforced by
default.

First notice the use of the familiar `zremrangebyscore` method. As
before, we use this call to remove any expired elements.

Now, note the use of the `pipeline` method. It ensures that all calls
up to the `execute` method are executed atomically. That is, they will
be evaluated as a block before any further operations can proceed. This
prevents concurrent uses of the sorted set from interfering with each
other. This is especially important when enforcing uniqueness.

As an illustration, consider the following code:

```python
# Process one
c = ExpiringSet(...)
c.push('Hello,', 1463879868, unique=True)

# Process two
c = ExpiringSet(...)
c.push('World!', 1463879868, unique=True)
```

Note the identical timestamp, `1463879868`. If the code did not
enforce atomicity, there would be four possible results, two of which
are valid:

```python
# Result 1: Process one completes entirely first:
c = ['World!']

# Result 2: Process two completes entirely first:
c = ['Hello,']

# Result 3 and 4: Process one and two intermix:
c = ['Hello,', 'World!'] # Or the reverse
```

The reason for results 3 and 4 can be explained by considering the
following, non-pipelined code:

```
if unique:
   redis.zremrangebyscore(self.key, score, score)
redis.zadd(self.key, self._pack(value), score)
```

In the event of both processes completing calls to
`zremrangebyscore`, there will be a race to call `zadd`. Regardless of
execution order of the processes, the result will be a set with two
elements, when only one is expected.

As a side note, the `_pack` method serializes the data; we do this to
ensure that non-trivial data, like a dictionary, can be unpacked
later. By default, this is done using `pickle`, but any serializer,
like a JSON serializer, can be used.

The `elements` method should be clear: it expires old elements and
returns all list of the remaining ones. Not the use of `_unpack`; it
reverts the serialization performed on insertion.

## Conclusion

Well, that about wraps it up.

We covered two methods for implementing time expired sets. One used a
list of keys and the other used a sorted sets. We also implemented a
version of the sorted sets approach in Python, using the `redis-py`
package.

There is much more than can be done that is not covered in this
article; if you are interested in the code, you can view it here:
[github.com/versionzero/qr](https://github.com/versionzero/qr).
