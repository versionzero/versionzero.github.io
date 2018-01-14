Title: Installing Windows NT 4.0 Workstation Using Virtual PC
Date: 2007-09-23 4:34
Status: published
Category: Windows
Tags: Windows, Virtual PC, Virtual Machines
Slug: windows-nt-4.0-workstation-using-virtual-pc
Authors: Ben Burnett
Summary: Installing Windows NT 4.0 Workstation Using Virtual PC

I assume a lot about you’re background in these tutorials. They are
primarily for myself, because I have a tendency to forget things more
often than not, so don’t be too distressed and come calling on me if I
don’t hold your hand through the whole thing. (Sorry, it’s 12:04am,
and it’s been a long day.)

# Requirements

* Windows NT Workstation CD-ROM or disk image

# Installation

* Create an ISO of your original Windows NT CD or get a copy from some
  someplace... Do this because otherwise it takes ages to install; it’s
  lightning fast with disk images as compared to real CD media.
  
* Create a new Virtual Machine in Virtual PC with 64MB of RAM and 4GB
  of disk space, or change all that to your requirements.  Start the new
  Virtual Machine and have Virtual PC capture the WinNT.iso (or whatever
  you called it) as a CD-ROM.
* Once the new Virtual Machine has started, use your common since and
  format the drive using NTFS. After the format is complete, which
  will be quick, you can sit back and let the setup do its thing.

* On the first boot, it will look like nothing is happening…
  forever. But it is actually doing something, so just be
  patient. Even though you selected NTFS as your file system, it first
  must be formatted as FAT and then converted. I’m sure there is some
  weird historical reason for this, but I don’t know it of hand. My
  best guess is that they had a very quick and easy way to format a
  FAT partition (so the actual install phase was fast), put some run
  once utilities on it, and then you boot for the first time, it blows
  the whole FAT partition away and puts an NTFS one in its place.

* When prompted for the CD key, if you have it saved in a file, just
  copy it out of there (remove the ‘-’ and ‘OEM’, if it has it) and
  use Virtual PC to paste it into the Virtual Machine (fake the key
  strokes rock!). It’s all about being lazy. Unfortunately, unlike
  other OS installers, the NT one is not smart enough to skip from one
  edit control to the next, once the edit control is full. This means
  that instead of being able to just paste the whole thing, like you
  can for Windows 95, you must paste each part individually, and then
  TAB to the next edit control manually. It’s a small irritation, but
  if you have you speakers turned up, you’ll know you entered too many
  characters in on field, because Windows will beep repeatedly at
  you. (My ears leant that the hard way.)

* When asked about networking, just say you are on a Wired to the
  network and let NT detect the network adapter for you, by clicking
  on the search button. The TCP/IP Protocol is enabled by default. For
  most people this is sufficient, but you can also select NetBEUI for
  novelty’s sake.

* The next step allows you to install new services, I added Simple
  TCP/IP Services and more importantly—for my network,
  anyway—Microsoft TCP/IP Printing.

* (Optional) During setup it asks to make a start-up disk, if you copy
  `D:\SUPPORT\HQTOOL\NTHQ` and re-name it to startupNT.img, or
  something similar, you can capture the new disk image, and have the
  Windows NT setup create a new start-up disk for you. How ever so
  clever.

* Once the installation is complete, release the floppy disk, because
  otherwise you’ll find yourself in recovery land. Also, I suggest
  disabling the auto detection of the floppy disk, as the seek noise
  on boot will drive you up the wall. (Maybe not the first time, but
  it will eventually get to you, I promise.) While you’re at it, you
  can also release the install media, since you won’t need it anymore.

* It actually turns out that it’s just boots in general that take
  forever, just be patient.

# Networking

Because of the way we installed Windows NT, the networking may not be
configured correctly. To fix this open the Control Panel and double
click on the Network icon. Once there, add click on Add… and double
click on Protocol in the component list. From the Manufacturers list,
select Microsoft and them, from the Network Protocols double click on
TCP/IP. Finally, click OK and allow Windows to go about it’s rebooting
way. Reboots always seem to make Windows happy. If your computer is
ever frustrated, just reboot it, it’ll make it smile.

# Service Pack

Once you have the networking configured properly, it’s time to update
Windows (as all good Windows users do, right?). I found, to my
surprise, that the Windows 95 Service Pack was still available from
the Microsoft web-site. Man, I’d hate to be the person doing the
support for that.

You can get SP6a from
[here](http://support.microsoft.com/kb/152734). Be warned, however,
that you will have to do this on your host machine and transfer the
files over the network, as the version of IE that ships with NT (on my
old version, anyway— packing a full SP1, oh yeah!) won’t even open
www.google.com.

# Notes

Get the following packages:

* [Internet Explorer 5.0](http://www.cintek.com/download/ie5.htm)
* [Microsoft .NET Framework 1.1 Redistributable](http://www.cintek.com/download/ie5.htm)

Now, when you tell Virtual PC to Install or Update Virtual Machine
Additions, in the words of the venerable comedian Douglas Addams,
"Don’t Panic!", because it will just give you a weird error (the
kernel is missing a handy function to tell Virtual PC if a debugger is
running, if that means anything to you, great! If not, don’t worry
about, it’s not important anyway). But this error really isn’t an
error; you can ignore it and simple Explore the CD for the setup
program… Sadly, it turns out only the DOS applications actually work
on a Window 95 base install (and they do not play well with Windows,
so you have to exit to the command line and run FSHARE.EXE to get
Folder Sharing to work— and even then, it’s only in DOS that you can
access that drive. If you try to run Windows once it has been loaded,
Windows goes all wonky— try it, if you don’t believe me.) What really
strikes me about this is that even the OS/2 additions work—and who
even uses that OS anymore?! (Says the man installing Windows 95)—so
why doesn’t it work on a stock Windows 95 install?
