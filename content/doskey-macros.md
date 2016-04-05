Title: Doskey Macros
Date: 2002-08-20 8:42
Modified: 2002-08-20 5:00
Status: published
Category: Windows
Tags: DOS, cmd, Windows
Slug: doskey-macros
Authors: Ben Burnett
Summary: Simple doskey macros

Doskey macros are a wonderful thing, even today with the GUI goodness
Windows offers, there is still many a reason to drop down to the
command line. Now, most Linux and UNIX folks will laugh at the
arguably abysmal tool set given by the good old DOS prompt, but it can
be made just a little more interesting if you start using doskey in
conjunction with a set of batch files.

Below is a very simple template doskey macro/batch file which will
first execute as a batch file, and then use itself as a doskey macro
file. Hopefully it will get you started down a more efficient command
line route. Or you might just find it a clever, but useless mess.

```text
;= @echo off
;= rem Call DOSKEY and use this file as the macrofile
;= %SystemRoot%\system32\doskey /listsize=1000 /macrofile=%0%
;= rem In batch mode, jump to the end of the file
;= goto end
;= rem ******************************************************************
;= rem *   Filename: aliases.bat
;= rem *    Version: 1.0
;= rem *     Author: Ben Burnett <me@cs.wisc.edu>
;= rem *    Purpose: Simple, but useful aliases; this can be done by
;= rem *             other means--of course--but this is dead simple and
;= rem *             works on EVERY Windows machine on the planet.
;= rem *    History:
;= rem * 22/01/2002: File Created (Syncrude Canada).
;= rem * 01/05/2007: Updated author's address, added new macros, a
;= rem *             history and some new helpful comments.
;= rem * 19/06/2007: Added Notepad, Explorer and Emacs macros.
;= rem * 20/06/2007: Fixed doskey macrofile= path problem: it is now not
;= rem *             a relative path, so it can be called from anywhere.
;= rem ******************************************************************

;= Doskey aliases
h=doskey /history

;= File listing enhancements
ls=dir /x $*
l=dir /x $*
ll=dir /w $*
la=dir /x /a $*

;= Directory navigation
up=cd ..
pd=pushd

;= Copy and move macros
cp=copy
mv=move

;= Delete macros
rm=del /p $*
rmf=del /q $*
rmtmp=del /q *~ *# 2>nul

;= Fast access to Notepad
n=notepad $*

;= Fast access to Explorer
c=explorer .

;= :end
;= rem ******************************************************************
;= rem * EOF - Don't remove the following line.  It clears out the ';'
;= rem * macro. Were using it because there is no support for comments
;= rem * in a DOSKEY macro file.
;= rem ******************************************************************
;=
```

It abuses the fact that the command prompt in Windows will silently
eat the `;=` prefix, while doskey will treat it as a macro being
re-defined over and over again.

**EDIT**: Honourable mention on
  [StackOverflow](http://stackoverflow.com/questions/4186427/how-do-you-write-comments-in-doskey-macro-files)
