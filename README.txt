Forpedo (v0.1) -- a Fortran preprocessor for generics
-----------------------------------------------------
Author:        Drew McCormack
Created:       26 Nov 2004
Last Modified: 26 Nov 2004

'Forpedo' is a preprocessor for Fortran 90 code, written in python. 
(The name is inspired by the flipper feet himself.) It can handle
some typical preprocessing tasks, like including code from one file in
another, but it is mostly designed to provide C++ like generics (templates).

The output of Forpedo is pure Fortran code, which should work with any
standard compiler.

To use Forpedo, you will need access to a recent version of Python (2.3 or later).
Python is commonly available these days, on almost all platforms (see http://www.python.org)

Forpedo is very new software, and may contain bugs. Please report them
to drewmccormack@mac.com. The Forpedo web site is http://www.maniacalextent.com/forpedo

New functionality should be added to Forpedo in good time. Suggestions and offers
of support are always welcome.


Using forpedo
-------------

To run forpedo, simply pipe your source code into forpedo.py. Generated code will
be written to standard output. 
Eg.

forpedo.py < myFile.f90t > myFile.f90
f90 myFile.f90


Directives Reference
--------------------

import
------
Include the source of one file in another (like C's include directive).

Example:
#import "OtherFile.fh"


definetype
----------
Used to define generic types, and type definitions (like C's typedef's).  

Example of simple type definition:
#definetype  RealParamType   none   real(8), parameter

Example of using this defined type:
@RealParamType :: r = 10
print *, r


Example of generic type definition:
#definetype T   Int   integer
#definetype T   Real  real

Example of using this generic type:
@T var<T>
var<T> = 10
print *, var<T>

A definetype directive has a type name, a tag, and a concrete fortran type.
The typename should be used, after an @ symbol, anywhere in the code that  
the type is required. 

The tag can be accessed in the code by putting the 
type name between triangular parentheses (ie <typename>). The tag is often 
required to avoid name clashes, particularly for variables with global scope.
So, for example, you would generally need to use the tag for a module name,
otherwise multiple modules may get the same name.

Eg.
module MyModule<T>

this will be replaced with

module MyModuleInt
and
module MyModuleReal

When you are using definetype for a type definition, rather than generic
types, the tag is not really needed, and you can simply set it to some
string like 'none'.
