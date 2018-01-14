Title: Run Windows commands from the Windows Subsystem for Linux
Date: 2016-04-09 12:00
Status: draft
Category: Systems
Tags: Windows, Linux
Slug: run-windows-cmds-in-wsl
Authors: Ben Burnett
Summary: They said it couldn't be done.

## Introduction

A while back, [Microsoft](http://www.microsoft.com/) announced a
partnership with [Canonical](http://www.canonical.com) that would
bring native [support for
Linux](https://blogs.windows.com/windowsexperience/2016/04/06/announcing-windows-10-insider-preview-build-14316/)
to the Windows echo-system.

The partnership includes creating an addition to Windows 10, through a
new subsystem called Windows Subsystem for Linux, that allows Windows
to run and use a subset of an Ubuntu distribution. A working version
of this system&mdash;still in beta&mdash;was release on April 6th 2016
and is available through the [Windows Insider
Program](https://blogs.windows.com/windowsexperience/2016/04/06/announcing-windows-10-insider-preview-build-14316/). You
can also watch the project activity on the [Windows Command Line Tools
For Developers](https://blogs.msdn.microsoft.com/commandline/) blog.

One of the problems with the Windows Subsystem for Linux (herein WSL)
is that it _only_ supports running Linux tasks. According to
Microsoft, "[you cannot interact with Windows applications and
tools.](https://blogs.windows.com/buildingapps/2016/03/30/run-bash-on-ubuntu-on-windows/)"
That is to say, if you launch `bash`, you cannot run, say,
`notepad.exe` from _within_ `bash`. This means that Windows system
tasks cannot be automated. This is unfortunate, since using the
assortment of Linux tools perform some of these tasks would be ideal.

Systems like [Cygwin](https://cygwin.com) (or more interestingly,
[Babun](http://babun.github.io)) can inter-operate with Windows
application. However, this is due to the way the systems were
implemented. Cygwin, for instance, is a collection of Unix tool that
have been ported and compiled to run on Windows. This is stark
contrast to how WSL operates, which actually runs native Linux
applications.

The purposes of this post is to demonstrate that it is possible to
escape the Linux sand-box and run native Windows applications.

## The Approach

The way in which WSL works does not allow us to escape the Linux
sand-box directly. To do this we will require a set of tools
specifically crafted for this task.

A simple tool, available
[here](https://github.com/versionzero/winrun), allows Linux
applications to interact with Windows. It operates by monitoring the
Windows filesystem for changes. If a new file is detected, it is read
and the command it contains is run.

Consider the case of `notepad.exe`. If we would like to launch it, we
need only create a new file, containing the following:

```text
C:/Windows/notepad.exe
```

Note that we use `/` slashes. This is to avoid having to deal with
double escaping the path, using `\\\\` as a delimiter.

Our utility will notice the creation of a new file and starts the
process churning.

Communicating the application name to the WSL is now simply a matter
of creating a new text file with the command we care to run. There are
many ways to do this in Linux, but a simple one takes the following
form:

```bash
echo "C:/Windows/notepad.exe" > /mnt/c/winrun/run
```

Where `run` is an arbitrary name of a text file, and `/mnt/c/winrun`
is a directory that can be read and written to by both Windows and
Linux.

Note that the current implementation of the monitoring tool will not
delete the `run` file, so we need to clean it up ourselves.

## How it Works

The monitoring tools is a plain vanilla Win32 application. When run,
it opens `C:\winrun` and monitors the directory for the creation of
new files.

The processes by which it accomplishes this is a somewhat complex, but
that is generally the nature of Win32 programming.

First, we use the
[`ReadDirectoryChangesW`](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365465(v=vs.85).aspx)
API call to detect any change in the directory we are monitoring. When
a file is added,

If you have any questions or comments for me, please leave them bellow.
