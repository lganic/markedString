class markedString:#temporary markedString class, gets overwritten
    pass

def _mask(s: str, chrC: int = 100)-> str:#for error reporting
    if len(s)<chrC:
        return s
    return s[:chrC-3]+'...'

#determine type of variable passed, and return str version for error reporting
def _typeToStr(variable):
    if type(variable)==type:
        return str(variable).split("'")[1]
    return str(type(variable)).split("'")[1]

class markedString:
    def __init__(self, sourceString: str, marks: list = None, allowedTypes: list = [int,bool,type(None)][:])-> markedString:
        self.__size=len(sourceString)
        self.allowedTypes=allowedTypes
        if marks is not None:
            #if default marks have been passed, check if given mark list is valid
            if len(marks)!=self.__size:
                raise IndexError(f"Given mark list and given string size do not match: {_mask(sourceString)}  {_mask(str(marks))}")
            for item in marks:
                #check that all items in given mark list are valid mark types
                if not type(item) in self.allowedTypes:
                    raise TypeError(f"Type not recognized as mark: ({_typeToStr(item)}), change allowedTypes to fix")
        if marks is None:
            #no default marks, initalize mark list to all None
            self.__marks=[None]*self.__size
        else:
            #default marks have been passed, copy into mark list
            self.__marks=marks[:]
        self.__sourceString=sourceString
    def marks(self):
        #return copy of mark list
        return self.__marks[:]
    def __len__(self)-> int:
        return self.__size
    def __setitem__(self, r: 'slice or index',newVal: 'str object or any type in allowedTypes')-> None:
        p=lambda x:abs(x)-1 if x<0 else x
        #<- function to account for negative index
        rType=type(r)
        nType=type(newVal)
        if rType==slice:
            #if a slice is given, check that the slice is within bounds of string
            f, t, step=r.indices(self.__size)
            if p(f)>=self.__size:
                raise IndexError(f"From range index out of range: {f}, markedString is {self.__size} characters long")
            if p(t-1)>=self.__size:
                raise IndexError(f"To range index out of range: {t}, markedString is {self.__size} characters long")
        if rType==int and p(r)>=self.__size:
            #if index is explitly given, check that it falls within markedString
            raise IndexError(f"Index out of range: {r}, markedString is {self.__size} characters long")
        if nType==list:
            #a list of marks was passed for batch assignment
            #check that a slice was passed, as currently a slice is required for batch assignment
            if rType==slice:
                temp=[type(a) in self.allowedTypes for a in newVal]
                #check that all types in input mark list are valid types
                if False in temp:
                    raise TypeError(f"Type in mark assignment list is not allowed: {_typeToStr(newVal[temp.index(False)])}")
                del temp
                #check that length of input list and length of slice match
                if t-f!=len(newVal):
                    raise IndexError(f"Mark assignment list length doest not match assigned range: Attempted to store {_mask(str(newVal))} to indices [{f},{t})")
                for sourceIndex, targetIndex in enumerate(range(f,t,step)):
                    #copy data in input mark list to mark list
                    self.__marks[targetIndex]=newVal[sourceIndex]
                return
            if rType==int:#error case, see below
                #(might change this later so that when passed batch and index,
                #batch is assigned to elements following and including index)
                raise TypeError(f"Attempting to assign mark assignment list to single index: Attempted to store {_mask(str(newVal))} to index {r}")
                return
            raise TypeError(f"Index type not recognized: {_typeToStr(rType)}")
        if nType in self.allowedTypes:
            #a mark type was passed
            if rType==slice:
                #index is slice, put new data in all slice indices
                for index in range(f,t,step):
                    self.__marks[index]=newVal
                return
            if rType==int:
                #index given, save new mark to index given
                self.__marks[r]=newVal
                return
            raise TypeError(f"Index type not recognized: {_typeToStr(rType)}")
        if nType==str:
            #string was passed as data
            if rType==slice:
                #index given is a slice
                if len(newVal)!=1:#<-check if str is single char
                    #check if str size and slice size match
                    if t-f!=len(newVal):
                        raise IndexError(f"String length does not match assigned range: Attempted to store '{_mask(newVal)}' to indices [{f},{t})")
                    #convert str into list of chars
                    unpacked=[a for a in self.__sourceString]
                    #copy new data into storage string
                    for sourceIndex, targetIndex in enumerate(range(f,t,step)):
                        unpacked[targetIndex]=newVal[sourceIndex]
                    #repack list of chars into single string
                    self.__sourceString=''.join(unpacked)
                else:
                    #given str is a single char, assign to all values in slice
                    #convert string into list of chars
                    unpacked=[a for a in self.__sourceString]
                    #assign new char to all indices in slice
                    for index in range(f,t,step):
                        unpacked[index]=newVal
                    #repack string from char list
                    self.__sourceString=''.join(unpacked)
                return
            if rType==int:
                #single index given
                if len(newVal)!=1:
                    #a multiple char str was given as data so throw error
                    raise IndexError(f"Attempting to assign multiple characters to single index:  Attempted '{_mask(newVal)}' -> Index {r}")
                #unpack str into list of chars
                unpacked=[a for a in self.__sourceString]
                #assign char to index
                unpacked[r]=newVal
                #repack str from list of chars
                self.__sourceString=''.join(unpacked)
                return
            raise TypeError(f"Index type not recognized: {_typeToStr(rType)}")
        raise TypeError(f"Input datatype not recognized: {_typeToStr(nType)}")
    def __getitem__(self, r: 'slice or index')-> '(ch,mark) or markedString':
        #return mark and data at index given
        #if index is int, return (ch,mark) at index
        #if index is slice, return markedString
        if type(r)==int:
            return (self.__sourceString[r],self.__marks[r])
        if type(r)==slice:
            return markedString(self.__sourceString[r],self.__marks[r][:],allowedTypes=self.allowedTypes)
        #type was not slice or index, throw error
        raise TypeError(f"Index type not recognized: {_typeToStr(r)}")
    def __str__(self)-> str:
        return self.__sourceString
    def __iadd__(self, otherMarkedString: markedString)-> None:
        #check that otherMarkedString is of type markedString
        if type(otherMarkedString)!=markedString:
            raise TypeError(f"Attempting to add {_typeToStr(otherMarkedString)} to markedString object, only markedString objects can be added together")
        self.__size+=len(otherMarkedString)
        self.__sourceString+=str(otherMarkedString)
        self.__marks+=otherMarkedString[:]
        return self
    def __add__(self, otherMarkedString: markedString)-> markedString:
        #check that otherMarkedString is of type markedString
        if type(otherMarkedString)!=markedString:
            raise TypeError(f"Attempting to add {_typeToStr(otherMarkedString)} to markedString object, only markedString objects can be added together")
        tempStr=self.__sourceString+str(otherMarkedString)
        tempMarks=self.__marks+otherMarkedString[:]
        out=markedString(tempStr,tempMarks,allowedTypes=self.allowedTypes)
        return out
    def __contains__(self, data: 'datatype in allowedTypes or str or list of allowedTypes')-> bool:
        if type(data) in self.allowedTypes:
            #data is a mark, check if the mark is currently in the mark list
            return data in self.__marks
        if type(data)==str:
            #data is str or char, check if data is in current string
            return data in self.__sourceString
        if type(data)==list:
            #data is list of marks check if this pattern of marks exists in the mark list
            if len(data)>len(self.__marks):
                for index in range(0,len(self.__marks)-len(data)+1):
                    if self.__marks[index:index+len(data)]==data:
                        return True
        return False
    def __eq__(self, otherMarkedString: 'datatype in allowedTypes or str')-> bool:
        #check that type of input is markedString
        if type(otherMarkedString)!=markedString:
            raise TypeError(f"Attempting to check equal: {_typeToStr(otherMarkedString)} to markedString object, only markedString objects can be tested together")
        #check that the sizes of the given markedString matches
        #(this would be caught in the main check but its way faster when they are different sizes)
        if self.__size!=len(otherMarkedString):
            return False
        #main equals check
        return self.__sourceString==str(other) and self.__marks==other[:]
    def __iter__(self)-> 'iterator -> (character, mark)':
        #loop over all elements in both string and list, concurrently
        for mark, ch in zip(self.__marks,self.__sourceString):
            yield (ch,mark)
        raise StopIteration
    def __ne__(self, other: markedString)-> bool:
        #check that type of input is markedString
        if type(other)!=markedString:
            raise TypeError(f"Attempting to check not equal: {_typeToStr(other)} to markedString object, only markedString objects can be tested together")
        #check that the sizes of the given markedString matches
        #(this would be caught in the main check but its way faster when they are different sizes)
        if self.__size!=len(other):
            return True
        #main not equals check
        return self.__sourceString!=str(other) or self.__marks!=other[:]
    def __repr__(self)-> str:
        return self.__sourceString
    def __sizeof__(self)-> int:
        return self.__sourceString.__sizeof__()+self.__marks.__sizeof__()+self.__size.__sizeof__()+self.allowedTypes.__sizeof__()
    def capitalize(self)-> markedString:
        tempstr=self.__sourceString.capitalize()
        return markedString(tempStr,self.__marks,allowedTypes=self.allowedTypes)
    def endswith(self,other)-> bool:
        if self.__size==0:
            #if current length of self is 0, self cannot end in other
            return False
        dType=type(other)
        if dType in self.allowedTypes:
            return self.__marks[-1]==other
        if dType==list:
            if len(other)>self.__size:
                return False
            return self.__marks[-len(other):]==other
        if dType==str:
            if len(other)>self.__size:
                return False
            return self.__sourceString[-len(other):]==other
        raise TypeError(f"Type given has no correlation to this markedString, given type: {_typeToStr(dType)}, Expected types: str or any in list:{str([_typeToStr(a) for a in self.allowedTypes])}")
#    def find(self,other)-> int:






#find
#index
#isalnum
#isalpha
#isascii
#isdecimal
#isdigit
#isidentifier
#islower
#isnumeric
#isprintable
#isspace
#istitle
#isupper
#join
#lower
#partition
#replace?
#rfind
#rindex
#rpartition
#rsplit
#split
#splitlines
#startswith
#swapcase
#title
#translate?
#upper




#DOCUMENTATION
#--------------------------------------------------------------------
markedString.__add__.__doc__="Add two markedString objects together"
markedString.__contains__.__doc__="""Check if data in contained in markedString
If a string is passed, function returns whether data is in internal string
If data is in allowedTypes, function returns if data is in mark list
If a list of allowedTypes is passed function returns whether list is contained within mark list"""
markedString.__eq__.__doc__="Check if other markedString object is equal to self",
markedString.__len__.__doc__="Return length of internal string"
markedString.__setitem__.__doc__="""Assign data to either internal string, or internal mark list
If values are of string type, the internal string will be modified
If the value is of a type contained in allowedTypes, the internal mark list will be modified.
slice indexing and assignment is supported
Assigning a single mark or character to a slice will result in all elements in the slice being updated"""
markedString.__getitem__.__doc__="""Get mark and character at index
If single index is passed, return (character,mark) at index
If slice is passed, a markedString object will be returned
where the data over that range is copied"""
markedString.__doc__="""Creates new markedString object from input string
Marks can be passed, but will default to all None
allowedTypes are the types which the markedString will recognize as marks when passed as data"""
markedString.__str__.__doc__="Get current stored string"
markedString.__iadd__.__doc__="Add other markedString object to self"
markedString.__iter__.__doc__="""Return iterator object
Each element of the iterator corresponds to one index of the string
Element is a tuple in the form of (ch,mark)
Where ch is the character of the string and mark is the mark at that index"""
markedString.__ne__.__doc__="Check if other markedString object is not equal to self"
markedString.endswith.__doc__="""Check if string or mark list ends with given data
If str is passed, the internal string ending is checked
If type in allowedTypes is passed, the last element of the mark list will be checked
"""
markedString.marks.__doc__="Return copy of mark list"
#--------------------------------------------------------------------

if __name__=="__main__":
    help(markedString)
