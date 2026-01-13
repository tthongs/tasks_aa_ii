14th September 2025
===================
Ubuntu : OS : install

UNIX/Linux/Ubuntu : command line based

Ubuntu:
	open terminal
	type in UNIX cmd 
			->output
	500+ cmds
	simple/complex

terminal: shell
bash

project


TCL
Python

YT channel
Books? (No)
Notes?
	Class, notes, README, Examples

JD: Job Discription

Foundries:
TSMC (Taiwan)
180nm
3nm

GF (Global foundries)

Samsung
Intel



user id : pine
machine:  pine


whoami
	prints user id (uid) currently logged in

hostname
	machine name
	host (machine)


windows:
	folder
UNIX:
	directory


RH7
CentOS7.0
Most upgraded OS:
RHEL8


Chip Design
	IC design
	IP 
		
	IT (team)
	machines
	RH7/RH8 : CPU/RAM
	50 Linux
	5000-10000


Ankur
	IT team: unix user id
	ankur

	50 UNIX

	VM

	fe-ankur
		rsh  alpha
		ssh  beta
		rlogin	gamma	

	Linux: powerful : CPU 12-24-64-128
			  RAM: 32GB / 800GB


	Chip design?

		Software (EDA companies)
		EDA: Electronic design automation 
		Cadence (Analog)
		Synopsys (Digital)
		Siemens (Mentor Graphics) (physical verification)
		Xilinx
		Ansys
		
	1)Tool install 
	2)License

	Asic
		Layout -> Cadence -> virtuoso (tool)
					install
					license

	Linux : use (GUI)

	command line

	RAM
		Linux


Linux
	multi user env
		u1
		u2
		u3
		and so on



Linux
	cmd line based




17 Sep 2025


C:\A\B


pwd:
	print working directory with absolute path
	/etc/bin
	directory: folder

path:

/ root path
/home/pine/dir1
/home/pine/dir2

ls: list cmd

UNIX cmd: cases sensitive (lower case)

Mkdir

mkdir : create new directory

mkdir dir1
mkdir d2
mkdir d3 d4 d5
clear -> clear the terminal

Dont use special character: * for dir/file name
* : astrick
* : star
* : wild card

rm: remove a file or dir
rm README.txt
(once removed is gone, there is a default backup)

rm -r d4
rm -r d1 d2 d3

rmdir d5


ctrl+L : clear 

cd: change directory


ls : list cmd

home directory in Linux?
=========================


cd <enter>
we change our current to home directory
i.e
/home/pine


Linux
	cmd
	binary
		/etc/bin/rm
	which rm
	built-in
		cd


editors:
	gvim
	gedit
	nedit
	nano

	open simple text file


& -> ampersand

process background
pid: process id

ls /home/pine
ls ..
ls ../..

* : wild card 


pdf:
	acroread
	evince
ls -F

ls -l 
	long list
	

21 Sept-ld 2025

ls
ls -F
ls -l
ls -d 
ls -l -d
ls -ld
ls -a
ls -A
ls -la
ls -lA


.  -> current dir
.. -> parent dir


bash/unix
	weak quote " "
	strong quote ' '

.bashrc (must be present in home directory of user)
bash: shell
rc: run command

run cmd of bash shell


~ (tilde)
~ -> /home/pine

/home/pine/.bashrc

~ : /home/pine

gedit ~/.bashrc &

# to comment in bash



mkdir -p D1
mkdir -p D1/D2


echo : to print

echo : it adds a new line character in the end
\n


alais cmd: list all possible alais definitions for you


shell:
	standard input
			-> shell-> kernel
					-> out

					stderr
					stdout

					shell
shell:cl
	bash
	csh
	tcsh
	zsh
	ksh

echo adds a \n in the end of text


user defined var
	bash
		v=100
		echo "$v"

system defined var
	environment variables
		echo "$SHELL"


env:
	cmd to print all environment var and its value


The value of $USER is pine

echo "The value of $USER is $USER"
The value of pine is pine
pine@pine:~/PINE/2026/UNIX_BASH$ echo "The value of \$USER is $USER"
The value of $USER is pine
pine@pine:~/PINE/2026/UNIX_BASH$ echo 'this is $USER'
this is $USER


PS1='\w'



mkdir

cp 
mv
rm

cp -r d1 d2


echo examples
	switch
quotes "" / ''	
cat

echo "helo" 

>
>>
 redirect operators

stdout
stderr




24th Sep 2025

Unix file structure


super user : root

/ :root dir
/home
/etc
/bin
/usr/bin


root


your accnt: pine

sudo install


do something as super user

/etc/sudu file
pine
	: root accnt


sudo 



 mv file /



permissions
	
-rw-rw-r-- 1 pine pine 0 Sep 24 21:52 file

- regular file

r: read access : can read file's content
w: write access : can change the content of file / delete / move
(x: execute access

file owner:  	rw-  (pine)
group owner: 	rw-   (pine)
others:		r--	(others)



UNIX?
cmd line system

cmd options


ls -l
rm -r 

(manual)
man ls 
press q to exit


redirect operator
>  (write)
>> (append)

ls
->
stdout

ls file
->file
stdout


ls file_nofile


ls nofile
ls: cannot access 'nofile': No such file or directory

error

stderr

standard error

ls file nofile
ls: cannot access 'nofile': No such file or directory
file

echo -e "this is \t a tab"
echo "this is \t a normal text"


echo -n
	supress default \n



> re-direct operator
redirects stdout to a file

0 : stdin
1 : stdout
2 : stderr



ls file nofile &> f3
pine@pine:~/PINE/2026/UNIX_BASH$ cat f3
ls: cannot access 'nofile': No such file or directory
file
pine@pine:~/PINE/2026/UNIX_BASH$ ls file nofile 2> f3
file
pine@pine:~/PINE/2026/UNIX_BASH$ cat f3
ls: cannot access 'nofile': No such file or directory
pine@pine:~/PINE/2026/UNIX_BASH$ ls file nofile > f3 2> f4
pine@pine:~/PINE/2026/UNIX_BASH$ cat f3
file
pine@pine:~/PINE/2026/UNIX_BASH$ cat f4
ls: cannot access 'nofile': No such file or directory


stdin <

cat: concatinate cmd



echo $PATH
echo $USER
echo $PWD
echo $HOSTNAME

vi : shell based
vim: update of vi (shell)
gvim : graphical vim
	cmd mode (cmd mode) : cant type directly
	search a text / char
			
	insert mode
	cmd mode to insert mode

wc : word count
	->lines cnt
	-> word cnt
	-> char


word: seperated by WS

this is	pine : 12
char cnt: all char including white space
WS: space / tab / new line


wc:
	-l
	-w
	-m

wc -l

pipe: | (file type)


unix cmd -> stdout-> unix cmd


cat f | wc -l
ls -A | wc -l
	
binary			(octal)
r	w	x
0	0	0 	0 
0	0	1	1
0	1	0	2
0	1	1	3
1	0 	0	4
1	0	1	5
1	1	0	6
1	1	1	7

chmod u+x file
-rw-rw-r-- 1 pine pine   110 Sep 27 22:11 f1
chmod 000 f1

chmod 000 f1
pine@pine:~/PINE/2026/UNIX_BASH$ ls -l f1
---------- 1 pine pine 110 Sep 27 22:11 f1
pine@pine:~/PINE/2026/UNIX_BASH$ cat f1
cat: f1: Permission denied
pine@pine:~/PINE/2026/UNIX_BASH$ echo "HELLO" > f1
bash: f1: Permission denied
pine@pine:~/PINE/2026/UNIX_BASH$ cat > f1
bash: f1: Permission denied

UNIX:
	file: 	666-umask 
	dir:	777-umask
666
002
---
664 (file)

777
002
--- 
775 (dir)

chmod u+x file
./file

dir: execute : to be able to cd to that dir
dir: r : to be able to list files/dirs under main dir


perm can only be changed by file/dir owner
#


wc
pipe
permissions
softlinks
	ln file newfile (hard link)
	ln -s file newfile (soft link)

ctrl+d : EOF (signal)



gvim : details
sort
find
ls switch
#


gvim f1 &

cmd mode

switch to insert mode from cmd mode
i
a
o
shift+i
shift+a
shift+o

open file in gvim
press i/o go to insert mode
type
esc (switch back to CM from IM)
:q (quit without save)
:wq (quit with save)
:w (save without quit)

.swp

:w! (force save)

rf -rf
	(force option)

gvim f1 f2 &

:n to switch files
:N
:tab all (enable tab)

gvim -p f1 f2 &

:all
enable HS (horizontal split of window)


gvim -o f1 f2 &

enable HS 



gvim -O f1 f2 &


how to enable line numbers in gvim

open file
stay in cmd mode
:set nu (enter)

:set nonu (remove line numbers)

put in home dir:
.vimrc (startup file gvim/vim/vi)



UNIX cmds
=========
chmod / permissions
chown
wc
pipe
cat
usage of < , > , >> , << (here marker)

cut cmd

range:
	starting-end
		-c2-4
		-c -6
		-c4-


-c: cut the char/range of char

-d : using delimiter
-f : field

a,b,c
d,e
f


there is no def val of delimeter in cut
some cmds have def del as space 


echo "abc def" | cut -d' ' -f1
abc
echo "abc def" | cut -d' ' -f2
def


if you cannot achieve the desired o/p using cut cmd then awk cmd is the
solution



4th Oct 2025
============

gvim 

insert mode:
	backspace
	delete button


undo: u (in cmd mode)


we can also delete data in cmd mode

x: delete the char where cursor is present
4x
1x: same as x
2x ....

dw: word<space>
delete word (put cursor position at first char of the word)

hi there this is pine


<word>
<> word boundry


d$ 
$: end of line (without \n)

delete 

dd  : delete complete line with \n

3dd : delete 3 lines 

d0 : delete from cursor position till start of the line


d+shift-g (dG) : delete from current line till end of file

dgg : delete from current line till start of the file

gvim:
dd: line delete (cut)
paste: p cmd 

dd line cut : p line with \n

cut/paste

copy/paste

copy: yank (yanking)

d-> delete
y-> yank

yy: copy the line
p : paste the line
15p: paste the line 15 times

nyy: copy n number of lines from current line
p: paste those n number of lines

dot =>  .  key can access prev cmd


cat cut.csv 
a,b,c
d,e,f
i,l,k
pine@pine:~/PINE/2026/UNIX_BASH$ cut -d',' -f1,3 --output-delimiter=" " cut.csv      
a c
d f
i k
pine@pine:~/PINE/2026/UNIX_BASH$ cut -d',' -f1,3  cut.csv
a,c
d,f
i,k



pid
background job
foreground job
ps cmd


every unix cmd will have a unique process id (pid)

when the cmd is done, pid also gets deleted


jobs -l 
to list the background running jobs in current term


ps -f
list pid of jobs running in current terminal


sleep 2


exit cmd

exit status

	0 : sucessful 
	non-zero : 1 -255 (fail: stderr)



PWD:	D1/.f1
	D2/
	D3/.f1
	D4/.f1
	D5/

script?


-eq (interger equal)

10/10/2025

hjkl : traverse in gvim in cmd mode
3j
6k
r : replacement key
shift+r : allows multiple char replacement
cc: delete line + insert mode
cw: delete word + insert mode
$ : move to end of line
^ (cap/carrot) : start of line non-space char 
0	: start of line including space

search any char in same line:
press f in cmd mode
then press char: t (any)
press ; to go to next 
press , search backwards

shift+f (right to left)

w ; ;

w : word to word switch
W : ABC  to word switch 
5W : switch to 5th word
word char:
[a-zA-Z0-9_]

THIS      is a word
this       word helelo
Asd abc abc


b: jump  word backwards

} : Jump para to para
{ : move prev para


grep/egrep: unix cmd : we can find the text/char in a file without
openning it


head/tail
head


x=x+1
x=$x+1
x+=1
x=1

x=$((x+1))
let
expr


path


mv ./d1/d2/f* ..
mv ./d1/f* ./d2/
mv ~/f* ../d2/


f* > d2
f
f1
fa
fabc
cf

f content copy


cp f1 ./d2/

head -3 f1 > ./d2/f2


cat f1 > f2
cp f1 f2

cp ~/d1/f1 ~/d2/



15/10/2025
wc
head/tail
cat
tac

sort
tr


tr:
translate/delete characters


tr <option> set

* : wildcard
zero or more characters

ls f*
f  (* matching zero no char
f12345 (* match 5 char )



ls f*


Ggrep : get regular expression pattern
egrep: extended grep (advance regular expr)





f
f1
fa
f1233






tr:

translate / delete


tr <opt> S1 S2 file

tr 'a' 'A' <<< "string"
tr 'a' 'A' file





variable substitution
cmd substitution


VS:
a=10
echo $a

CS
file=$(mktemp)
echo $file



tr : truncate

tr -t

character set (regular expr)
[:upper:] == [A-Z] == AorBorCDEF..orZ
[:lower:] == [a-z] == aorb or ...z

[a-Z] : a or b ..z or A or B...Z
[acde] : a or c or d or e
[12acb] : 1 or 2 or a or c or b
[12a-d_] : 1 or 2 or a or b or c or d or _

[:space:] : white space (space tab and \n)

tr ' ' '\0' <<< "hi there"
hithere
\0 is null character


-s 
sqeeze


tr -s

sqeeze repeated char


18 th Oct 2025

tr -c
tr -d 

echo $PATH | tr ':' '\n'


[:digit:]  === '0-9'
[:alpha:]
[:alnum:]
[:space:] : WS (space, tab and NL)


sort
----
.bashrc
export LC_ALL="C"

sort according to the ascii value
0
1
2
null
space
a
z
A
Z

sort
	ascii values
ascii table
ascii value: 0 is for null character

-n : numeric sort
-f : ignore case


space: default delimiter

sort
sort --debug  -k2,2 -k1,1 f1


uniq  (works on consecutive duplicate lines)
sort -u



-s switch ?

cat a.csv
a,asic,2025
a,pd,2026
a,dv,2026
sort --debug -t ',' -k1,1 -k3,3 -s a.csv 
sort: text ordering performed using simple byte comparison
a,asic,2025
_
       ____
a,pd,2026
_
     ____
a,dv,2026
_
     ____

sort --debug -t ',' -k2.4,2.6n f2
sort --debug -t ',' -k2.4,2.4n f2

ls -lh | sort -h -r -k5

grep/regular expression

regex: concept
	can be used in multiple commands/languages
						tcl, perl, python, bash

unix:
	cut (does not use regex)
	grep (uses regex)
	sed : 
	awk :
	find 

grep:
	data find from a file

grep 'regex' file1 file2
egrep 'regex' file1 file2


regex:	
using literal characters:
	a
	ac

charracter set:

grep '0' file
grep '1' file


char set:
	[0123]
	0 or 1 or 2 or 3
	[321]
	3 or 2 or 1

	[1-5]
	[12345]
	1 or 2 or 3 or 4 or 5

grep '12345' file
grep '[12345]' file

1[23]
	12
	or
	13

not 123
char set:
	[246]
	2 or 4 or 6
grep '123' file
grep '[1][2][3]' file

[246][246]
2/4/6
2/4/6
22
24
26
42
44
46
62
64
66

246246
246[246]

2462
2464
2466



[1234]
[abgz]
a or b or g or z
[_3%0]
_ or 3 or % or 0


[01]ab

0ab
1ab

[a-d][2-3]z

[A-Za-z]

Meta character:
dot: .
represents any single


[1a.d]

1 or a or . or d

[111]
1 or 1 or 1




char set
---------

egrep 
A{3}
AAA

A{1,4}
A
AA
AAA
AAAA

AB{1,2}
AB
ABB

(AB){1,2}
AB
ABAB

[A-Z]{2}
AA
BB
AB
BA
CZ

[0-9]{2,4}
09
092
0123

[123]{2,}
11
22
33
12
23
31
111
222
123
321

[bcd]{1,4}
b
c
d
bbbb
dddd
cbdd


char set
modifiers
anchors


egrep 'a|A' file


not in char set
	[^abcd]
	not a or not b or not c or not d
	
	[ab^cd]
	a or b or ^ or c or d

	[e-h]

anchors
	^ : start of the line
	$ : end of the line

	blank line: ^$


. dot: meta char
	any single char not \n
	not null
	


Assignment

	write egrep which prints lines which:

	start with #
	end with .
	start with number OR end with alphabet
	start with 3 spaces OR end with .
	start witth non-alphanumeric
	end with min two numbers
	start with no space/no tab 
	end with space or tab
	have only 1 number
	have only two albhabets




anchors
	^
	$

modifiers
	*
	+
	?

* : star /astrick
	0 or more times repeatition of any char(s)

egrep 'ab*c' file
egrep 'ab{1,}c' file : abc abbc abbbc ....
ac
abc
abbc
abbbc
and so on
b 0 or more times

egrep 'a(cd)*e' file
0 or more times cd
ae
acde
acdcde
acdcdcde
and so on



+
	1 or more times repeat of any char(s)


egrep 'ab+c' file
egrep 'a[a-z]+c : abdfc
			azc
			azzzzzzc
			aycdfghcffc


abc
abbc
abbbc
and so on


?
 0 or 1 times repeat of any char(s)

ab?c
ac
abc

. : any single
[.] : literal dot . 

egrep '[.]+' file
egrep '\.+' file
.
..
...
dasfdfdsfasfd.aewr435r
cdadsfs......................
cdfCD.........................43R324FR

Assignment 2:

Write egrep to match all valid email address in a file

egrep '^[[:alnum:].]+@[[:alpha:]]+\.com?(.uk)?' f13


regex:
	chars
	char set
	meta char (dot)
	anchors: ^ , $
	Modifiers :  * + and ?
	() : round paranthesis


[a-z]
a
b
c
d

sddvSDV2314213512c12
[a-z][0-9][0-9]$
a00
b01


str: aZ0122acb
^[a-z][A-Z]
aA
bA
cZ


()
grouping 

memory

(abcd)+
abcdabcdabcd
a(123)*
0 or more times 123
a
a123
a123123



AA : (.)\1
CD
LL

DAD
MOM
TRY
ABC
POP

NITIN


a((b)(d))

\1 : bd
\2 : b
\3 : d

egrep -v
invert match


grep -E -v
egrep -v


egrep -i

	enable case insensitivity

e: extended
grep: globally search for regular expression patterns



egrep -c


counts no of matched lines


egrep -w:
	word match 

egrep -w 'pine'
egrep '\<pine\>'

egrep -l
	retrun only file name which has the match

egrep -R : recursive switch

cmd : unix :         egrep :       universal in all shell
but cmd can be shell specific
set : bash shell
bash
====
check integers
-eq
-neq
-gt
-lt
-ge
-le

n=4
if [[ $n -gt 5 ]] ;  then
	echo $n
elif [[ $n -lt 10 ]] ; then
	echo $n
elif [[ $n -ge 10 ]] ; then
	echo $n
	echo $n
else 
	echo 
fi

if [[ cond ]] ; then
	if [[ cond ]] ;then
		#body
	fi
fi




string compare
==
!=
>
<
>=
<=

t/false
&&                logical AND
if [[ $marks -gt 60 && $marks -lt 80 ]] ; then
	echo "fisr div"
fi

||	logical OR

if [[ $marks -gt 60 || $marks -lt 80 ]] ; then
	echo "fisr div"
fi


if [[ -f f1 ]] ; then
	rm f1
fi



[[ -f file ]] && rm file
[[ -f file ]] ; rm file
ls nofile || touch nofile


if [[ -f file && ( -f f1 || -f f2 ) ]] ; then


egrep/grep

egrep -R
	recursive

egrep -w
egrep '\<word\>' file

egrep -o 
	--
only-matching


-A
-B
-C


license file log

	total lic of tool:     virtuoso 25/15
	u1 1
	u2 2
	u3 3


grep/egrep
	covered all switches


12/Nov/2025
-----------
sed cmd


read cmd
IFS in bash shell
To read file line by line using bash shell script


read cmd is bash shell specific
IFS : internal field seperator in BASH
WS
IFS=$' \t\n'

IFS it decides the fields (or word)

str="a b c"

word=3 (field =3)

printf "%q\n" "$IFS"


read


trailing spaces
leading spaces


cmd substitution

s=$(expr 1 + 2)
echo $s
3


-z (empty string/var)
-n (non emptty string/var)
-f (file existence)
-d (dir existence)
bash specific switch

var=10
[[ -n $var ]] && echo "pass"

[[ -z $a ]] && echo "pass"


if [[ -z $var ]] ; then
	echo
fi


read:
	-p prompt
	-r to preserve \
	
IFS='-'
	read a b <<< "i j-p"

-s : hide stdin

-t timeout of read in seconds
-t 5

-n 1

read -a arr <<< "hi there"

echo ${arr[0]}
echo ${arr[1]}


next class:
while/read file reading
cat 
sed


[[ "abc" =~ ^a ]]




16th nov 2025
-------------

IFS in bash

IFS=' '
str="a b c"
for 
a
b
c


while true ; do
echo
done


read -v <<< "  this is str"
echo $v


break : break the inner most loop
	for while until

cnt=5
	while [[ $cnt -gt 1 ]] ; do
		echo $cnt
		#break
			while [[ $cnt -gt 4 ]] ; do
				#echo $cnt
					if [[ $cnt -gt 0 ]] ; then
						break
					fi
				echo $cnt
				cnt=$(expr $cnt - 1)
			done
		cnt=$(expr $cnt - 1)
	done


break (loop)
continue (loop)
exit



until [ ] ; do

done


cnt=1
while ! [ $cnt -gt 5 ] ; do
	echo $cnt
	cnt = $(expr $cnt + 1 )
done

until [ $cnt -gt 5 ] ; do
	echo $cnt
	cnt = $(expr $cnt + 1 )
done

bourne shell : sh 
		/usr/bin/sh
bash:
bash: bourne again shell
		/usr/bin/bash


if [ $cnt -gt 10 ] ; then

if [
if [[
while [[ $cnt -gt 10 ]] ; 




sed cmd in next class


read a file using bash scripting and print only those
line which :

	start with alphabets
	and
	lines start with #


$line

[[ $line =~  ]]



fgrep : fixed grep 

zgrep 



sed: stream editor


file input

sed f1 f2
a
b
c
d

sed:
	print data matching regex
	print data based on lines + regex
	delete data
	modify data


cat f1 | while IFS= read -r ; do
	#
	#
	done



sed

standard input

cat f1
a
b

sed f1

input
line 1
a 

a
b

sed 'cmd1;cmd2;cmd3' f1

read a (line 1)
a : pattern space (PS)

PS -> stdout

f1:
a
b


p: print cmd in sed (print the entire data which is present in PS)
sed 'p' f1
stdin  |   ps 	| stdout

a	   	   a
		   a
b		   b
	           b

sed -n 'p' f1
a	a	a
b	b	b


f1
a
b

sed 'p;p' f1
		a
		a
		a
		b
		b
		b

sed -n 'p;p' f1
		a
		a
		b
		b

sed -e 'p' f1 -e 'p'


sed -r :
-r enables advanced regex
	|
	+
	?
	{}



sed -rn '/^a|^b/p' f
sed -rn '/^a|^b/p;p' f
sed -rn '/^a|^b/{p;p}' f

sed -rn '2{/^a/p}' f



23 nov 2025
=============
print last line by sed
sed -rn '$p' file

p : print PS data to stdout
P
= : print line no of PS data to stdout

	a
		p
		=


	a
	b
		= : line no of b
		p
		a
		b


d : delete PS data
D


sed -ri.bk '/a/d' f1
f1 change
f1.bk



a
b
c
sed -r 'p;d' f


sed -ri.bk 'd' file
		

a
b
c

cp by sed 
file.bk
a
b
c

file : no data


sed cmd:
p (print PS)
= (print line no of PS)
d (delete PS)
s (substitute)

sed switch:
-n
-i
-r

a a a a
s/a/A/1
A a a a
s/a/A/2


s/REGEX/pine/g

aaaaab
aaab
aab

sed -r 's/a+/a/g' file
ab
ab
ab


ab ab ab


26 nov 2025
-----------
sed cmd:
p : print PS data
= : line no of data in PS
s : substitute
d : delete

switch
-r : regex
-n : stop buffer data to go to stdout
-e : multiple cmds
-i : change inside the file

line address
regex cond


file:
a
A
b
B
a
A

sed -rn '/^[aA]$/p' file
a
A
a
A

sed -rn '${/^a$|^A$/p}' file
sed -r '${/^a$|^A$/p}' file

sed -rn '1,+2p' f
line1
+
next two lines

sed -rn '1~2p' f
line 1
line 3
line 5
and so on

sed -rn '2~2p' f
line2
line4
line6

sed -rn '${/^a/p;=}' f9
sed -rn '${/^a/{p;=}}' f9



file
a

sed -r 's/a/A/' file

PS: a
s/a/A
PS: A
		A

sed -rn 's/a/A/;p' file

abc def

PS:
abc def
s/^ +//
abc def
	abc def



file
a a a
a a
a

s/a/A/
a a a
A a a
	A a a
s/a/A/g
A A A
	A A A
file:
abcabc123abc567abc
s/abc/ABC/
s/(abc)+/ABC
s/(abc)+/ABC/g

   sed 's/abc/ABC/g' <<< "abcabc123abc567abc"
   sed 's/abc/ABC/1' <<< "abcabc123abc567abc"
   sed 's/abc/ABC/2' <<< "abcabc123abc567abc"
   sed 's/abc/ABC/3' <<< "abcabc123abc567abc"
   sed 's/abc/ABC/4' <<< "abcabc123abc567abc"
   sed 's/abc/ABC/5' <<< "abcabc123abc567abc"
   sed 's/abc/ABC/g' <<< "abcabc123abc567abc"
   sed 's/(abc)+/ABC/1' <<< "abcabc123abc567abc"
   sed -r 's/(abc)+/ABC/1' <<< "abcabc123abc567abc"
   sed -r 's/(abc)+/ABC/2' <<< "abcabc123abc567abc"
   sed -r 's/(abc)+/ABC/3' <<< "abcabc123abc567abc"
   sed -r 's/(abc)+/ABC/g' <<< "abcabc123abc567abc"


\U : upper case conversion
\L : lower case conversion
\u : upper case conversion
\l : lower case conv
\E : stops cov started by \U or \L


sed -r 's/regex/replacement/FLAG' file
FLAG: g (global occurance)
      p (print ps) only for sucessful substitution

sed -r 's/a/A/gp' <<< "abc"

sed -rn 's/d/z/gp' <<< "abc"
p flag wont work


\Uab
AB

\uab
Ab



assignment
use sed on a file
convert first lower char to upper
ignore other first char if they are numeric/space or anyother char


convert first word to upper case of each line


covert first complete line to uper case of a file


delete all lines of a file which start with # except first line


not 

sed -rn '1!p' file
print all lines except line 1
sed -rn '1,3!p' file
print all lines except line 1 to 3


sed -r '1! s/a/A/g/' file

sed -r '/^#/s/#/_/g' file

sed -r '/\.$/ d' file



6th Dec 2025
============

q cmd
quit
echo $?

print 4 lines and quit with exit status 10
sed '4q 10'
echo $? : 10


a\  append cmd
i\  insert
c\  change

sed 'a hello' file
it will append hello after every line of ip

sed '3,5 a hello' file

sed '1 i this is header'

Assignment1:
cwd files .sh
line 1 : !#/usr/bin/bash do nothing
line1 : !#/usr/bin/bash

seq 10 | sed -e '1 i START' -e '$ a END'


sed '1 c TEXT' file


-f sedfile


n : read next input line to PS and print current PS data if -n is not used
N : append next line to PS 


a
b
c

sed 'n' file


	PS
		a	
		b	

		c


a
b
c
d

sed '=;n' file
a	PS
	a (cycle started =;n)
					1
					a
					b
					3
					c

sed '=;n;n' file

PS
a
		1
		a
		b
		c
		4
		d

sed '=;=;n' file

		1
		1
		a
		b
	
		3
		3
		c

		d
sed -n '=;=;n' file

		1
		1
	c
		3
		3
	d



N: append in current PS

a
b
c
d

sed 'N;N;='

PS:a
   b
   c
		3
		a
		b
		c
		d

sed 'N;N;p' file

		a
		b
		c
		a
		b
		c
		d


n/N
d : delete entire data of PS and ends the cycle
D : delete data of PS but only first line
P : print first line of PS
p : complete PS data

a/i/c

--debug

-f sedfile


10th Dec 2025
=============

sed substitute flag
g
I
\U
\u
\l
\L
\E


-s
--seperate

& : represents the regex match

echo "abc123abc" | sed -r 's/^[a-z]+/&&/'


ab12cd34ef56

sed -r 's/[0-9]+/0/g' 



(.*) : \1
(.*) : &

echo "abc def" | sed -r 's/(.*)( )(.*)/\3\2\1/g'

sed -r 's/regex/replace/g'
sed -r 's:regex:replace:g'
ser -r 's|regex|replace|g'


sed -r 's|a|A|g' file



branching
	b (uncondtional branch)
	t (runs if prev substition is sucessful)
	T (runs if prev substition is not sucessful)
loop



sed 'b;p;=' file

sed -r 'cmd1;cmd2;cmd3'

sed 'b;p' file



b LBL  :LBL
t MYLABEL    :
T





a
b
c


a b c 

sed 's/\n/ /g' file
a
b
c


PS
	a
		a
		b
		c


a
b
c
s/\n/ /g 

a b c 

a
b
c
d

sed -r 'N;N;s/\n/ /g'
	a
	b
	c 
	a b c
		a b c

	d




14/12/2025
==========
sed 
awk 

	Bell Labs
	Aho
	Weinberger
	Kernighan
AWK

awk -f awkfile inputfile


why awk?
	text processing
			fetch info
			change info
			data print
		sed/grep => awk
offer
	complete programming
		loops
		function
		if else
		built-in function
		regex
		array
		variable


awk has its own interpreter
/usr/bin/awk

#!/usr/bin/awk


#!/usr/bin/bash
egrep
sed '
	N;p
	'
awk '
	awk syntax
'



awk: bash term
awk script
awk -f awk.script inputfile

awk script:
run.awk
#!/usr/bin/awk


chmod +x run.awk
./run.awk



awk -option 'cmd' infile


awk
	3 block
		BEGIN block
	awk process BEGIN block first before reading in input from a file

	you can have one or more BEGIN


	MAIN block
	no KW for MAIN
	{

		MIAN block
	}

	you can have one or more MAIN


		END block
	END is used after input(s) file is processed


Recommendation:
	use one BEGIN (optional)
	use one or more MAIN (optional)
	use one END (optional)


BEGIN (optional)
you can use BEGIN in that case as well where you dont have to
process any input file


BEGIN{ }

{ }


END{ }


awk:	
	print (echo): new line is added automatically not formatting
	printf: you have add \n and you can also format your op

file
a
b
c

	{}
	{cmd on main block}

	run for line 1 which is a
	run for line 2 which is b
	run for line 3 which is c
	exit from main


print $0
line of the file in main block

line: record

default: 
a
b
c

by default
record 1 : a
record 2 : b
record 3: c

Input record seperator
Def val
IRS : \n

Output record seperator 
ORS
Def val
ORS: \n



AWK
	main block
	record 
	field

IFS: input field seperator: WS
OFS : def val space

main block:

	$0 : complete record
	$1 : field1 of that record
	$2 : field 2 of that record
	${10} : field 10 of that record
	and so on



print in main 
	print $1,$2

here , is OFS value

only valid for print cmd


NF : number of field in each record
NR : number of record


awk 'BEGIN{OFS="_"} {print $1,$}' f


awk 'END{print $0}'
awk 'END{print NR}'




1 2 3
4 5 6
8 1 12


record: sum all fields
record 1: sum=6
record 2: sum=1




2nd Jan 2026
=============

awk is a cmd, but it provides lots of programming capabilities


AWK
	BEGIN
	{}
	END

BEGIN->MAIN->END


FS :   input field seperator
OFS:   o/p field seperator
NF :   no of field in each record
NR :   no of record
FNR:  
RS :   input record seperator
ORS:   output record seperator
FILENAME


OFS :      def value space
print $1,$2
comma: OFS val =  space
a b



awk -F"," 'BEGIN{FS="_"};{print $1,NF}' f4.csv
a,b,c,d 1
i,l,k,h,p 1
1,2,3,4,5,6,7 1
a,1,d,4,g 1


FS inside BEGIN will be the final valu
it will overwrite -F value


-F'[ ]'
to make FS as single space

def
FS='[ \t\n]+'

FS='[ ]'
a b c d
a b  d
FS='[ ]+'


cat f6
ab1234552451cdeee1341235215abcccweq
dasagfasgf452352455fadfdsd857484hghsgshg
awk -F'[0-9]+' '{print $1,$2,$3}' f6 | awk '{print $NF}'
abcccweq
hghsgshg


awk -F'[0-9]+' '{print $NF}' f6
abcccweq
hghsgshg


RS record seperator: def val : \n


line1\nline2
line1
line2



ORS (def val new line \n)


fn
ln

fn
ln

fn
ln

Get above data in following format using awk:
fn ln
fn ln
fn ln


fn ln

fn ln

fn ln

fn ln



practise:
FS
OFS
RS
ORS


$0 ~ /^p/{
}

$1 ~ /^[0-9]/{
}

$NF !~ /[0-9]{
}

/^abc/{
}


/abc$ | ^def/{
}


$0 ~ /^a/ || $NF == "pine"{
}


$NF ~ /^[0-9]+$/ && $1 !~  /[0-9]/{
print $0
}


{
	if( $0 ~ /^p/ ) {
		print $0
	} else {
		print "NO"
	}
}


Last field:
	$NF


Second last field:
	$(NF-1)

and so on




exit cmd can usd in awk


loops
array
built-in functions of awk
functions


7th Jan 2026
============

built-in functions
------------------

sqrt(n)
int(n)
exp(n)
log(n)

length: length of string

task:
smallest length record



task:
shortest
and
longest
string from a file


RS="\n\n"
a
b

c d
e


task
ssassa  fsasargqrqrg 543253326646326
45235234523 254125343452345 dsfasfasd



(1)
length function

length("string")
->6


length(ARGUMENT)



(2)
index

pine
p=index 1
i=index 2
n=index 3
e=index 4

index("pine","i")
2

index("hello","h")
1
index("123","a")
0 (when substr is not found in main string)
x
index("this is pine training","is")
3
 
this is pine training

for(i=1 ; i<=NF ; i++) {
	print(index($i,"is"))
)
3
1
0
0


find if a file has "and"

egrep "and" file


{
find=index($0,"and")
if( find > 0 ) {
	print "and is found at index : find in record $0"
}
#exit
}


#RS="\n\n\n\n"
{
for(i=1 ; i <=NF ; i++) {
	find=index($i,"and")
	if ( find > 0 ) {
		print "and found at index:" find "for the field" $i
	}
}
print ""
}


(3)
substr

BEGIN{
print( substr("hello",2,2))
}



awk 'BEGIN{v1=substr("A234def",1,3);v2=substr("A234def",5);v=v1 v2;print v }'
A23def



match
split
sub
gsub
gensub


array





