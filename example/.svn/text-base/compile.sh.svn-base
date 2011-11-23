#!/bin/sh

# Substitute your f90 compiler here
F90="xlf90 -qsuffix=f=f90"

../forpedo.py < dynamicarray.f90t > dynamicarray.f90
$F90 intArray.f90 dynamicarray.f90 main.f90

