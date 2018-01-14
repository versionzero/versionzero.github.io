Title: Windows Environment Variable Trick
Date: 2008-08-29 5:00
Status: published
Category: Windows
Tags: DOS, cmd, Environment Variables, Windows
Slug: windows-environment-variable-trick
Authors: Ben Burnett
Summary: Making arrays

Although not explicitly supported, it is possible to make, let's call
them pseudo-arrays, in the environment with no fancy string parsing or
anything sloppy like that. It involves some clever uses of call
command to evaluate and extract values from the pseudo-arrays and well
positioned `%` signs to demarcate which environment variables we want
evaluated and when.

Lets look at a quick example to see the basic mechanism. Assignment would be
done as follows:

```
set count=1
set var%count%=42
```

There are two method to extract the value, while at the command prompt
use the `%var%count%%` form to extract the value:

```
call echo %var%count%%
```

On the other hand, while within a batch file use the following form to
extract the value:

```
call echo %%var%count%%%
```

Note the extra strafing `%` signs. Both of the above expressions will
display the number 42, as expected; or maybe it's is surprising, it
all depends on your expectations and what you might consider
interesting and cool. Sadly, I do consider this cool; insofar as it
works on a straight out of the box Windows installation. The technique
may look a little hairy, but it's quite useful. The above will print
the contents of `var1` (i.e. 42) as we explained.  We could also
replace the `echo` command with a set if we wanted to set some other
variable to the value in `var1`. Meaning the following is a valid
assignment at the command line:

```
call set x=%var%count%%
```

Where:

```
echo %x%
```

Would print the number 42, as we would expect. We can even carry out
arithmetic operations on these pseudo-arrays' values. For instance,
the following would subtract 2 from the value of `varN`:

```
call set /a x=%var%N%%-2 >nul
```

Note that here we need to redirect the output to the `nul` port,
otherwise the result arithmetic operation would be printed to the
screen. Either way, this technique means that some rather advanced
operations can be done over a range of values, with some effort.
