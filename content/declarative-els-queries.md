Title: Declarative Elasticsearch Queries
Date: 2016-05-23 20:00
Status: draft
Category: Programming
Tags: Elasticsearch, Python
Slug: declarative-els-queries
Authors: Ben Burnett
Summary: Building Elasticsearch queries from classes

## Introduction

As I wrote
[previously](http://versionzero.org/blog/2016/04/05/els/index.html), I
am not happy with the way in which Elasticsearch (ELS) queries must be
written.

In the last article I introduced a small domain specific language to
help simplify creating ELS queries and filters. Unfortunatly, with
that method, it was not possible to capture all possible queries in a
general manner. This article introduces a new style of defining
queries. This time we use class declarations as the basis for creating
queries.

## The Data

As with last time, we'll be using a simple bank account data
set. Typical entries are of the form:

```json
[
  {
    "account": 12,
    "balance": 16623,
    "firstname": "Iris",
    "lastname": "Mckenzie",
    "age": 29,
  },
  {
    "account": 42,
    "balance": 3450,
    "firstname": "Bradshaw",
    "lastname": "Rupertson",
    "age": 19,
  }
  ...
]
```

Our data has five entries: one for `account`, `balance`, `firstname`,
`lastname`, and `age`. While it's too simplistic for real-world use,
it'll be sufficient for our purposes.

Imagine we wanted to run the following query:

```json
{
  "query": {
    "filter": {
      "range": {
        "balance": {
          "gt": 1200
        }
      }
    }
  }
}
```

It would be nice to be able to re-write this as a Python
class. Imagine we could write the following:

```python
class SomeInterestingQuery(object):
  class query(object):
    filter = [
      els.range(balance__gt=1200),
    ]
```

Where `els.range` is a class that can be initialized with one or more
arguments.

## Class dissection

To begin understanding the aproch, we need to first conver how to
extract useful information from a class declaration.

Python is well suited to our needs, but other languages, like
JavaScript, can be used to accomplish something similar. In
particular, Python alows us to gather information about a class, like
the name of the class and it's member, which is the basis for our
approach.

Consider the following class:

```python
class ClassName1(object):
  variable1 = "Variable #1"
  class innerclass(object):
    variable2 = 42
```

We would like to be able to distil it in to it's component parts. Namely,

```json
{
  "variable1": "Variable #1",
  "innerclass": {
    "variable2": 42
  }
}
```

We can do something like the following to help extract the information
we are interested in:

```python
import inspect

def extract_members(elements):
  results = None
  if isintrinsic(elements):
    results = elements
  elif isintrinsiclist(elements):
    results = [e for e in elements]
  return results

def extract(cls):
  results = {}
  if cls:
    for name in dir(cls):
      if name[:2] != '__':  # Ignore private members.
        attr = getattr(cls, name)
        if inspect.isclass(attr):
          results[name] = extract(attr)
        else:
          results[name] = extract_members(attr)
  return results
```

Where the helpers `isintrinsic` and `isintrinsiclist` determine if the
given element is a built-in type or a list containing data in the form
of built-in types.

To use these methods is a matter of calling:

```python
import json

results = extract(ClassName1)
print json.dumps(results, indent=2)
```

Which will print the results we saw above.
