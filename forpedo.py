#!/usr/bin/env python

import sys
import re

#----------------------------
# General functions
#----------------------------
def combine(*seqin):
    """
    Returns a list of all combinations of argument sequences.
    For example: combine((1,2),(3,4)) returns [[1, 3], [1, 4], [2, 3], [2, 4]]
    """
    def rloop(seqin,listout,comb):
        """recursive looping function"""
        if seqin:                       # any more sequences to process?
            for item in seqin[0]:
                newcomb=comb+[item]     # add next item to current comb
                rloop(seqin[1:],listout,newcomb)
        else:                           # processing last sequence
            listout.append(comb)        # comb finished, add to list
    listout=[]                      # listout initialization
    rloop(seqin,listout,[])         # start recursive process
    return listout

#----------------------------
# Grammatical classes
#----------------------------
class GrammaticalEntityParser:
    """
    Abstract base class for a grammatical entity parser. A grammatical entity is
    anything in the source code that you might want to extract or modify.
    Subclasses of this class recognise such entities, and are responsible for
    extracting or modifying them.
    """

    def __init__(self, regExString, maxMatchesPerLine = None):
        self.regEx = re.compile( regExString )
        self.maxMatchesPerLine = maxMatchesPerLine

    def processLine( self, line, processFunc ):
        count = 0
        newLines = []
        changedLine = line
        retLines = None
        startSearchIndex = 0
        while True:
            m = self.regEx.search(changedLine, startSearchIndex)
            if not m: break
            startSearchIndex = m.start(0) + 1
            count = count + 1
            if self.maxMatchesPerLine and count > self.maxMatchesPerLine: break
            retLines = processFunc(self, changedLine, m )
            if retLines: changedLine = retLines[0]
        if retLines and len(retLines) > 0:
            newLines = retLines
        else:
            newLines = None
        return newLines

    def processFirstPassLine( self, line ):
        return self.processLine( line, lambda item, line, match: item.processFirstPassMatch( line, match ) )

    def processSecondPassLine( self, line ):
        return self.processLine( line, lambda item, line, match: item.processSecondPassMatch( line, match ) )

    def processFirstPassMatch(self, line, match):
        return None

    def processSecondPassMatch(self, line, match):
        return None


class ImportStatementParser (GrammaticalEntityParser):
    """
    An import statement parser. Imports the file given by the file named. 

    Form: #import "FileName"
    """

    def __init__(self):
        GrammaticalEntityParser.__init__(self, r'^\s*\#import\s*[\'\"](\w+)[\'\"]', 1)

    def processFirstPassMatch( self, line, matchObject ):
        f = open(matchObject.group(1))
        newLines = f.readlines()
        f.close()
        return newLines


class DefineTypeStatementParser (GrammaticalEntityParser):
    """
    The definetype statement, which defines an instaniation of a generic type.

    Form: #definetype TypeName TypeTag ConcreteFortranType

    Replaces Typename with the fortran type in the code instance. The TypeTag
    can be used to name things in the global namespace, to avoid naming conflicts.
    For example, a module XYZ could be named XYZ<TypeName>, and the tag would
    be appended to the name XYZ in the generated source code.
    """

    def __init__(self):
        GrammaticalEntityParser.__init__(self, r'^\s*\#definetype\s+(\w+)\s+(\w+)\s+(.+)' , 1)
        self.instancesPerType = {}
        self.instancesPerAbbrev = {}

    def processFirstPassMatch( self, line, matchObject ):
        label = matchObject.group(1)
        abbrev = matchObject.group(2)
        type = matchObject.group(3)
        inst = Instantiation( label, abbrev, type )
        self.instancesPerType.setdefault(label, []).append(inst)
        return None

    def processSecondPassMatch( self, line, matchObject ):
        return [""]


class DefinedTypeDeclParser (GrammaticalEntityParser):
    """
    This is a generic type declaration. It will be replaced by the concrete types defined in the
    #definetype construct when generating fortran source.

    Form: @TypeName :: variable

    The #definetype construct defines different instances of a given generic type. The preprocessor
    will generate a separate block of source code for each instance, replacing the generic type
    declarations in each one with the concrete fortran type.
    """

    def __init__(self, instantiationPerTypeName):
        GrammaticalEntityParser.__init__(self, r'@(\w+)')
        self.instantiationPerTypeName = instantiationPerTypeName

    def processSecondPassMatch( self, line, matchObject ):
        typeLabel = matchObject.group(1)
        newLine = line[:matchObject.start(0)] + self.instantiationPerTypeName[typeLabel].type + line[matchObject.end(0):]
        return [newLine]


class DefinedTypeTagParser (GrammaticalEntityParser):
    """
    A tag associated with a particular instance of a generic type. This can be used to avoid naming
    conflicts.

    Form: SomeGlobalIdentifier<DefinedTypeName>

    In an instance of the DefinedTypeName with the tag equal to "R", the above identifier will be replaced
    with "SomeGlobalIdentifierR". 
    """

    def __init__(self, instantiationPerTypeName):
        GrammaticalEntityParser.__init__(self,  r'<(\w+)>')
        self.instantiationPerTypeName = instantiationPerTypeName

    def processSecondPassMatch( self, line, matchObject ):
        typeLabel = matchObject.group(1)
        newLine = line[:matchObject.start(0)] + self.instantiationPerTypeName[typeLabel].abbrev + line[matchObject.end(0):]
        return [newLine]


#----------------------------
# Template instantiations
#----------------------------
class Instantiation:
    """
    Simple data storage class, used to store details of a single template instantiation.
    Could also use a dictionary.
    """

    def __init__(self, typeName, abbrev, type):
        self.typeName = typeName
        self.abbrev = abbrev
        self.type = type


#----------------------------
# Preprocessing functions
#----------------------------
def ProcessLines( lines, entities, processFunc ):
    """
    Process lines one at a time, processing each line with each grammatical
    entity. The processFunc is the particular processing function to use. It
    takes the entity and line as arguments.
    This function is called by the FirstPass and SecondPass functions.
    """
    lineIndex = 0
    newLines = lines[:]
    while lineIndex < len(newLines):
        for item in entities:
            line = newLines[lineIndex]
            retLines = processFunc(item, line)
            if retLines: newLines[lineIndex:lineIndex+1] = retLines
        lineIndex = lineIndex + 1
    return newLines


def FirstPass( lines ):
    "Perform first pass processing"
    definetypeStmt = DefineTypeStatementParser()
    entities = [ ImportStatementParser(), definetypeStmt ]
    newLines = ProcessLines( lines, entities, lambda item, line: item.processFirstPassLine(line) )
    return newLines, definetypeStmt


def SecondPass( lines, definetypeStmt ):
    "Perform second pass processing"
    types = definetypeStmt.instancesPerType.keys()
    instancesArray = []
    for t in types: instancesArray.append( definetypeStmt.instancesPerType[t] )
    combinations = combine(*instancesArray)
    newLines = []
    for c in combinations:
        entities = [definetypeStmt]
        instDict = {}
        for inst in c: instDict[inst.typeName] = inst
        entities.append( DefinedTypeDeclParser(instDict) )
        entities.append( DefinedTypeTagParser(instDict) )
        instanceLines = ProcessLines( lines, entities, lambda item, line: item.processSecondPassLine(line) )
        newLines.extend( instanceLines )
    return newLines


#----------------------------
# Main
#----------------------------
lines = sys.stdin.readlines()
lines, definetypeStmt = FirstPass( lines )
lines = SecondPass( lines, definetypeStmt )
for l in lines: print l,


