Title: Elasticsearch Queries
Date: 2016-04-05 20:00
Status: published
Category: Programming
Tags: Elasticsearch, Python
Slug: els
Authors: Ben Burnett
Summary: Building Elasticsearch queries and filters the easy way

## Introduction

I've been working with
[Elasticsearch](https://www.elastic.co/products/elasticsearch)
recently at work, and I'm impressed with it. My only issue with it is
the query and filter syntax. I find the syntax to be hard to read and
worse to write. I must have spent more time wondering why the results
of a query are empty than I have spent writing the queries to begin
with. I needed something to change this.

I first considered having someone else write them, but I ruled that
out after carefully considering my job security.  The solution I
settled on was to create a language with a simple syntax that retained
the expressiveness of a subset of the [ELS query
DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
that I was finding problematic.

I should mention that we also use [Python](https://www.python.org) as
our primary language in the office, so I'll be using it to illustrate
the ideas. Of course, the solution can be expressed in many other
languages and in many other forms. So don't feel that this needs to be
a Python only solution.

## The Data

For the purposes of our queries, we'll be using a simple bank account
data set. Typical entries are of the form:

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

## The Language

Consider the following expression:

```text
'balance' > 1200
```

The intent of the expression is to filter out all the bank accounts
such that only the ones with a `balance` entry greater than $1200 are
returned. Let's look at it's equivalent ELS query DSL version:

```json
{
  "range": {
    "balance": {
      "gt": 1200
    }
  }
}
```

The ELS query is not much more complex in this case, but it requires
that we aleast do more typing. If we make the expression more complex,
the problem I faced starts to emerge.

Consider the following:

```text
'balance' > 3500 and 'age' > 20
```

This expression is equivalent to:

```json
{
  "bool": {
    "filter": {
      "and": [
        {
          "range": {
            "balance": {
              "gt": 3500
            }
          }
        },
        {
          "range": {
            "age": {
              "gt": 20
            }
          }
        }
      ]
    }
  }
}
```

Notice I said equivalent to, rather than this is the _best_ was to
write the equivalent query in terms of the ELS query DSL. The ELS
query doesn't need to be so verbose; the query _can_ be written in
more compact form. But the point here is not to show how much typing
is required, rather it is to impress how complex queries _can_ become.

It should be clear that expressions are at least easier to write, read
and, in my opinion, reason about, than there ELS query equivalent.

## The Source

On to the more interesting part.

As promised, we'll be using Python in this example code, but feel free
to use one of your choosing.

Initially, the problem seemed to require a small, home-grown
parser. However, it became clear that this was not necessary: Python
ships with it's own parser baked right in. We can just use it instead
of creating our own.

The details of how the Python parser works are not relevant to our
discussion, but they may be the topic of a future post. What we need
to know is that an arbitrary string of text can be feed in to the
parser and a [abstract syntax
tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree) (herein AST)
will be emitted.

Recall the first expression we considered:

```text
'balance' > 1200
```

Given the above as input, the Python parser emits the following:

```python
ast.Compare(
  left=ast.Str(s='balance'),
  ops=[ast.Gt()],
  comparators=[ast.Num(n=1200)])
```

For those of you who are Python programmers: notice we didn't even
have to pass in meaningful Python code; the semantics, in this
case. can be ignored. (What does string greater than integer even
mean?)

For reference, the AST was created using:

```python
expr = "'balance' > 1200"
print ast.dump(ast.parse(expr, mode='eval').body)
```

We can argue over the use of `eval` another time; for now, let's just
agree that it works.

Given the AST for an expression, we need to convert it into something
that can be used with Elasticsearch. The AST is just a collection of
nested structures, so it can be traversed easily.

Here is the guts of the code to take an expression generate the ELS
query equivalent:

    #!python
    def expr2els(expr):
        return _expr2els(
            ast.parse(expr, mode='eval').body)

    op2str = {ast.And: 'and', ast.Or: 'or',
              ast.Gt: 'gt', ast.Lt: 'lt',
              ast.GtE: 'gte',ast.LtE: 'lte'}
    
    def _expr2els(node):
        if isinstance(node, ast.BoolOp):
            child = []
            for v in node.values:
                child.append(_expr2els(v))
            op = op2str[type(node.op)]
            parent = {'bool': {'filter': {op: child}}}
            return parent
        elif isinstance(node, ast.Compare):
            op = op2str[type(node.ops[0])]
            val = node.comparators[0].n
            name = node.left.s
            parent = {'range': {name: {op: val}}}
            return parent

    expr = "'balance' > 1200"
    result = expr2els(expr)
    print json.dumps(result, indent=2)

This is what it does:

* Lines 1-3 contain code we've already seen, but with a minor
  alteration. It takes a string as an input, generates an AST from the
  expression, and then passes it to `_expr2els` for further
  processing.
* Lines 5-7 define a map from an AST type to a string.
* Lines 10-17 handle the case where the AST node is a boolean
  expression (i.e. `ast.BoolOp`).

## Boolean Expressions

Boolean expressions require that we handle more than one child
expression. To see why this is necessary, consider the following
expression:

```text
'balance' > 3500 and ('age' > 20 or 'age' < 30)
```

The AST for the expression is:

    #!python
    BoolOp(
      op=And(),
      values=[
        Compare(
          left=Str(s='balance'), 
          ops=[Gt()],
          comparators=[Num(n=3500)]),
        BoolOp(
          op=Or(),
          values=[
            Compare(
              left=Str(s='age'),
              ops=[Gt()],
              comparators=[Num(n=20)]),
            Compare(
              left=Str(s='age'),
              ops=[Lt()],
              comparators=[Num(n=30)])]))])

Notice, on line 3, that `values` has more than one item. (Otherwise
known as a list.) The reason for this is that the expression considers
two cases at this point. One where the following is true:

```text
'balance' > 3500
```

**And** another, where the following is true:

```text
('age' > 20 or 'age' < 30)
```

This is exactly what we would expect when we **and** two expressions
together. The same is true when we **or** two expressions, much like
we see on lines 8-17 in the AST expression.

The remainder of the code,

    #!python
    op = op2str[type(node.op)]
    parent = {'bool': {'filter': {op: child}}}
    
Translates the type of the AST node to a string&mdash;that's `'and'` or
`'or'` in our language&mdash;and begins to build the ELS query. If we
re-read the AST dump above, we can see that it would generate the
following:

```json
{
  "bool": {
    "filter": {
      "and": [
        ...
      ]
    }
  }
}
```

Where `...` would be the `child` entries. Notice that `child` could be
another boolean expression or a comparison expression (covered
bellow). Since because of the way we traverse the AST recursively,
`child` can be a very complex sub-expression.

## Comparison Operators

Once again, consider the following expression:

```text
'balance' > 3500
```

The next piece of code considers the case where the current node is a
comparison operator:

    #!python
    op = op2str[type(node.ops[0])]
    val = node.comparators[0].n
    name = node.left.s
    parent = {'range': {name: {op: val}}}

* Line 1 maps the type of the operator to a string. In our case, this
  could be `ast.Gt`, `ast.Lt`, `ast.GtE`, or `ast.LtE` to `gt`, `lt`,
  `gte`, and `lte`, respectively.
* Line 2 extracts the value of the number being compared,
  i.e. `3500`. while line 3 extracts the name of the variable (well,
  our syntax for variables, anyway), i.e. `'balance'`.
* Finally, line 4 pieces together the query, i.e.:

```json
{
  "range": {
    "balance": {
      "gt": 3500
    }
  }
}
```

## Conclusion

Taken together, these small chunks of code can go a long way to
simplifying the process of writing ELS queries. It's not clear if this
is the best way, but it's a way that has worked well for me.

The current implementation emits very verbose code. It may be possible
to optimize the resulting output, but this would require a second
stage. I didn't think it critical to this post to venture down that
route. I may visit how this might be done in a future post.

If you have any questions or comments, please leave them bellow.
