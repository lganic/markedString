class markedString:#temporary markedString class, gets overwritten. Only here to make type hinting cleaner
    pass

def _mask(s: str, chrC: int = 100)-> str:#for error reporting
    if len(s)<chrC:
        return s
    return s[:chrC-3]+'...'

#determine type of variable passed, and return str version for error reporting
def _typeToStr(variable: type)-> str:
    if type(variable)==type:
        return str(variable).split("'")[1]
    return str(type(variable)).split("'")[1]

#convert list to string, but withought padding spaces
def _bLstStr(lst: list)-> str:
    if type(lst)!=list:
        return str(lst)
    if len(lst)==0:
        return '[]'
    out='['+_bLstStr(lst[0])
    for a in lst[1:]:
        out+=','+_bLstStr(a)
    out+=']'
    return out

class markedString:
    def __init__(self, sourceString: str, marks: list = None, allowedTypes: list = [int,bool,type(None)][:])-> markedString:
        self.__size=len(sourceString)
        self.allowedTypes=allowedTypes
        if marks is not None:
            #if default marks have been passed, check if given mark list is valid
            if len(marks)!=self.__size:
                raise IndexError(f"Given mark list and given string size do not match: {_mask(sourceString)}  {_mask(_bLstStr(marks))}")
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
    def __setitem__(self, r: 'slice or index',newVal: 'str, markedString, type in allowedTypes')-> None:
        p=lambda x:abs(x)-1 if x<0 else x #<- function to account for negative index
        rType=type(r)
        if type(newVal)==tuple:
            newVal=list(newVal)
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
                    raise IndexError(f"Mark assignment list length doest not match assigned range: Attempted to store {_mask(_bLstStr(newVal))} to indices [{f},{t})")
                for sourceIndex, targetIndex in enumerate(range(f,t,step)):
                    #copy data in input mark list to mark list
                    self.__marks[targetIndex]=newVal[sourceIndex]
                return
            if rType==int:#error case, see below
                #(might change this later so that when passed batch and index,
                #batch is assigned to elements following and including index)
                raise TypeError(f"Attempting to assign mark assignment list to single index: Attempted to store {_mask(_bLstStr(newVal))} to index {r}")
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
        if nType==markedString:
            if rType==slice:
                if t-f!=len(newVal):
                    raise IndexError(f"Given markedString is larger than the slice given: markedString is {len(newVal)} characters long, assigned to indices[{f},{t})")
                self.__sourceString=self.__sourceString[:f]+str(newVal)+self.__sourceString[t:]
                self.__marks=self.__marks[:f]+newVal.marks()+self.__marks[t:]
                return
            if rType==int:
                self.__sourceString=self.__sourceString[:r]+str(newVal)+self.__sourceString[r+1:]
                self.__marks=self.__marks[:r]+newVal.marks()+self.__marks[r+1:]
                return

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
        self.__marks+=otherMarkedString.marks()
        return self
    def __add__(self, otherMarkedString: markedString)-> markedString:
        #check that otherMarkedString is of type markedString
        if type(otherMarkedString)!=markedString:
            raise TypeError(f"Attempting to add {_typeToStr(otherMarkedString)} to markedString object, only markedString objects can be added together")
        tempStr=self.__sourceString+str(otherMarkedString)
        tempMarks=self.__marks+otherMarkedString.marks()
        out=markedString(tempStr,tempMarks,allowedTypes=self.allowedTypes)
        return out
    def __contains__(self, data: 'str, markedString, list of allowedTypes, or type in allowedTypes')-> bool:
        dType=type(data)
        if dType in self.allowedTypes:
            #data is a mark, check if the mark is currently in the mark list
            return data in self.__marks
        if dType==str:
            #data is str or char, check if data is in current string
            return data in self.__sourceString
        if dType==tuple:
            data=list(data)
        if dType==list:
            #data is list of marks check if this pattern of marks exists in the mark list
            if len(data)<=len(self.__marks):
                for index in range(0,len(self.__marks)-len(data)+1):
                    if self.__marks[index:index+len(data)]==data:
                        return True
        if dType==markedString:
            if len(data)<=self.__size:
                for index in range(0,self.__size-len(data)+1):
                    if self[index:index+len(data)]==data:
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
        return self.__sourceString==str(other) and self.__marks==other.marks()
    def __iter__(self)-> 'iterator -> (character, mark)':
        #loop over all elements in both string and list, concurrently
        for mark, ch in zip(self.__marks,self.__sourceString):
            yield (ch,mark)
    def __ne__(self, other: markedString)-> bool:
        #check that type of input is markedString
        if type(other)!=markedString:
            raise TypeError(f"Attempting to check not equal: {_typeToStr(other)} to markedString object, only markedString objects can be tested together")
        #check that the sizes of the given markedString matches
        #(this would be caught in the main check but its way faster when they are different sizes)
        if self.__size!=len(other):
            return True
        #main not equals check
        return self.__sourceString!=str(other) or self.__marks!=other.marks()
    def __repr__(self)-> str:
        return f"'{self.__sourceString}' : {_bLstStr(self.__marks)}"
    def __sizeof__(self)-> int:
        return self.__sourceString.__sizeof__()+self.__marks.__sizeof__()+self.__size.__sizeof__()+self.allowedTypes.__sizeof__()
    def __lt__(self,other: 'str or markedString')-> bool:
        if type(other)==markedString:
            return self.__sourceString<str(other)
        if type(other)==str:
            return self.__sourceString<other
        raise TypeError(f"Type not recognized for less than comparison: '{_typeToStr(other)}' type must be either str or markedString")
    def __le__(self,other: 'str or markedString')-> bool:
        if type(other)==markedString:
            return self.__sourceString<=str(other)
        if type(other)==str:
            return self.__sourceString<=other
        raise TypeError(f"Type not recognized for less than/eq comparison: '{_typeToStr(other)}' type must be either str or markedString")
    def __gt__(self,other: 'str or markedString')-> bool:
        if type(other)==markedString:
            return self.__sourceString>str(other)
        if type(other)==str:
            return self.__sourceString>other
        raise TypeError(f"Type not recognized for less than comparison: '{_typeToStr(other)}' type must be either str or markedString")
    def __ge__(self,other: 'str or markedString')-> bool:
        if type(other)==markedString:
            return self.__sourceString>=str(other)
        if type(other)==str:
            return self.__sourceString>=other
        raise TypeError(f"Type not recognized for less than/eq comparison: '{_typeToStr(other)}' type must be either str or markedString")
    def __mod__(self,other)->markedString:
        if type(other)!=tuple and type(other)!=list:
            other=(other,)
        if len(other)!=self.__sourceString.count("%"):
            raise TypeError(f"Number of format options does not equal number of arguments given: '{_mask(self.__sourceString)}' given {len(other)} arguments")
        selfCopy=self[:]
        letterCodes={'f':float,'d':int,'s':str,'m':markedString}
        for index, item in enumerate(other):
            fInd=self.__sourceString.find('%')
            lTy=self.__sourceString[fInd+1]
            if type(item)!=letterCodes[lTy]:
                raise TypeError(f"Mod string not given correct types, item:{index} expected: '{_typeToStr(letterCodes[lTy])}' but got '{_typeToStr(item)}'")
            if type(item)!=markedString:
                item=markedString(str(item),allowedTypes=self.allowedTypes)
            selfCopy=selfCopy[:fInd]+item+selfCopy[fInd+2:]
        return selfCopy
    def __mul__(self,value:int)->markedString:
        if type(value)!=int:
            raise TypeError(f"Requires int type for markedString multiplication, got type: '{_typeToStr(value)}'")
        if value<=0:
            return markedString("")
        mLst=self.__marks[:]*value
        mStr=self.__sourceString*value
        return markedString(mStr,mLst,allowedTypes=self.allowedTypes[:])
    def __rmul__(self,value:int)->markedString:
        if type(value)!=int:
            raise TypeError(f"Requires int type for markedString multiplication, got type: '{_typeToStr(value)}'")
        if value<=0:
            return markedString("")
        mLst=self.__marks[:]*value
        mStr=self.__sourceString*value
        return markedString(mStr,mLst,allowedTypes=self.allowedTypes[:])
    def capitalize(self)-> markedString:
        tempStr=self.__sourceString.capitalize()
        return markedString(tempStr,self.__marks,allowedTypes=self.allowedTypes)
    def endswith(self,other: 'str, markedString, list of allowedTypes, or type in allowedTypes')-> bool:
        if self.__size==0:
            #if current length of self is 0, self cannot end in other
            return False
        if type(other)==tuple:
            other=list(other)
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
        raise TypeError(f"Type given has no correlation to this markedString, given type: {_typeToStr(dType)}, Expected types: str,list or any in list:{_bLstStr([_typeToStr(a) for a in self.allowedTypes])}")
    def find(self,other: 'str, markedString, list of allowedTypes, or type in allowedTypes',start=None,end=None)-> int:
        if start==None:
            start=0
        if end==None:
            end=self.__size
        if type(other)==tuple:
            other=list(other)
        dType=type(other)
        if dType in self.allowedTypes:#if datatype is mark check if mark list contains data
            try:
                return self.__marks.index(other,start,end)#attempt list index
            except ValueError:
                return -1#item not in list, return -1
        if dType==list:
            if len(other)<=len(self.__marks):#check if input is larger than mark list size
                for index in range(start,min(len(self.__marks)-len(other)+1,end)):#loop over possible indicies for sublist
                    if self.__marks[index:index+len(other)]==other:#check list
                        return index
            return -1
        if dType==str:
            return self.__sourceString.find(other,start,end)
        if dType==markedString:
            searchList=other.marks()#load substring data, for optimization
            searchStr=str(other)
            searchListSize=len(searchList)
            while True:
                fI=self.__sourceString.find(searchStr,start)#find substring index in source string
                if fI==-1 or fI>=end:#check if substring found, and that found substring is in range
                    return -1
                #check if list at index matches target list
                if self.__marks[fI:fI+len(searchList)]==searchList:
                    return fI
                start=fI+searchListSize
        raise TypeError(f"Type given has no correlation to this markedString, given type: {_typeToStr(dType)}, Expected types: str,list or any in list:{str([_typeToStr(a) for a in self.allowedTypes])}")
    def index(self,other: 'str, markedString, list of allowedTypes, or type in allowedTypes',start=None,end=None)-> int:
        if start==None:
            start=0
        if end==None:
            end=self.__size
        if type(other)==tuple:
            other=list(other)
        dType=type(other)
        if dType in self.allowedTypes:#if datatype is mark check if mark list contains data
            try:
                return self.__marks.index(other,start,end)#attempt list index
            except ValueError:
                raise ValueError(f"Item not in mark list: {_mask(other)}")#item not in list, return -1
        if dType==list:
            if len(other)<=len(self.__marks):#check if input is larger than mark list size
                for index in range(start,min(len(self.__marks)-len(other)+1,end)):#loop over possible indicies for sublist
                    if self.__marks[index:index+len(other)]==other:#check list
                        return index
            raise ValueError(f"List substring not found in markedString: {_mask(_bLstStr(other))}")
        if dType==str:
            return self.__sourceString.find(other,start,end)
        if dType==markedString:
            searchList=other.marks()#load substring data, for optimization
            searchStr=str(other)
            searchListSize=len(other)
            while True:
                fI=self.__sourceString.find(searchStr,start)#find substring index in source string
                if fI==-1 or fI>=end:#check if substring found, and that found substring is in range
                    raise ValueError(f"markedString substring not found in markedString")
                #check if list at index matches target list
                if self.__marks[fI:fI+len(searchList)]==searchList:
                    return fI
                start=fI+searchListSize
        raise TypeError(f"Type given has no correlation to this markedString, given type: {_typeToStr(dType)}, Expected types: str,list or any in list:{_bLstStr([_typeToStr(a) for a in self.allowedTypes])}")
    def isalnum(self) -> bool:
        return self.__sourceString.isalnum(data)
    def isnum(self) -> bool:
        pC=self.__sourceString.count(".")
        if pC>1:#check if string contains multiple decimal points, ie: 12.34.56 is not a number
            return False
        return self.__sourceString.replace(".","").isalnum()
    def isalpha(self):
        return self.__sourceString.isalpha()
    def isascii(self):
        return self.__sourceString.isascii()
    def isdecimal(self):
        return self.__sourceString.isdecimal()
    def isdigit(self):
        return self.__sourceString.isdigit()
    def isidentifier(self):
        return self.__sourceString.isidentifier()
    def islower(self):
        return self.__sourceString.islower()
    def isnumeric(self):
        return self.__sourceString.isnumeric()
    def isprintable(self):
        return self.__sourceString.isprintable()
    def isspace(self):
        return self.__sourceString.isspace()
    def istitle(self):
        return self.__sourceString.istitle()
    def isupper(self):
        return self.__sourceString.isupper()
    def join(self,iterable: 'str, markedString, list of str, list of markedString')-> markedString:
        if type(iterable)==str:
            #if iterable is string, convert to markedString
            iterable=markedString(iterable,allowedTypes=self.allowedTypes)
        if type(iterable)==markedString:
            tS=self.__sourceString.join(str(iterable[:]))#create output string using string join
            tml=iterable.marks()#load iterables mark list
            tL=[tml[0]]#create output mark list object from first object in mark list
            for mark in tml[1:]:#loop over all marks except the first
                tL+=self.__marks#add copy of mark list
                tL+=[mark]#add next mark
            return markedString(tS,tL,allowedTypes=self.allowedTypes)
        if type(iterable)==tuple:
            iterable=list(tuple)
        if type(iterable)==list:
            #I assume 1 dimensional list that is not jagged
            if len(iterable)==0:
                #account for empty input list
                return markedString("",allowedTypes=self.allowedTypes)
            if type(iterable[0])==str:
                #iterable is list of strings, convert all strings in list to markedString
                for i, a in enumerate(iterable):
                    iterable[i]=markedString(a,allowedTypes=self.allowedTypes)
            elif type(iterable[0])!=markedString:#iterable is not of recognized type, throw error
                raise TypeError(f"List of type: '{_typeToStr(iterable[0])}' not joinable")
            out=iterable[0][:]#create output from first markedString in list
            for otherMarkedString in iterable[1:]:#loop over all but first markedString
                out+=self#add self to output
                out+=otherMarkedString#add next markedString to output
            return out
        raise TypeError(f"Type not recognized for markedString joining: '{_typeToStr(iterable)}'")
    def lower(self):
        return markedString(self.__sourceString.lower(),self.__marks[:],allowedTypes=allowedTypes)
    def partition(self,sep: 'str, markedString, list of allowedTypes, or type in allowedTypes')-> tuple:
        ind=self.find(sep)
        if ind==-1:
            return (self[:],markedString('',allowedTypes=self.allowedTypes),markedString('',allowedTypes=self.allowedTypes))
        return (self[:ind],self[ind:ind+len(sep)],self[ind+len(sep):])
    def replace(self,old: 'str,markedString,list of allowedTypes, or type in allowedTypes',new: 'str or markedString',count: int =None)->markedString:
        if type(new)!=str and type(new)!=markedString:
            raise TypeError(f"New string must be either str or markedString, type: '{_typeToStr(new)}' is not recognized")
        if type(new)==str:
            new=markedString(new,allowedTypes=self.allowedTypes)
        selfCopy=self[:]
        class inf:
            def __isub__(self,o):
                return self
            def __gt__(self,o):
                return True
        if count==None:
            count=inf()
        lR=0
        oldSize=len(old)
        newSize=len(new)
        while count>0:
            count-=1
            fInd=selfCopy.find(old,lR)
            if fInd==-1:
                return selfCopy
            selfCopy=selfCopy[:fInd]+new+selfCopy[fInd+oldSize:]
            lR=fInd+newSize
        return selfCopy

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
Assigning a single mark or character to a slice will result in all elements in the slice being updated
If a markedString is passed to a single index, markedString will be inserted at index,
thus replacing character and mark at index"""
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
markedString.endswith.__doc__="""Check if string or mark list ends with data given in 'other'
If str is passed, the internal string ending is checked
If type in allowedTypes is passed, the last element of the mark list will be checked"""
markedString.marks.__doc__="Return copy of mark list"
markedString.find.__doc__="""Return index of 'other' in markedString
If str is passed, the internal string is checked for the input data
When found, the index of the start of the substring is returned
If list is passed, the mark list is checked for the sublist pattern given
When found, the index of the start of the sublist is returned
If datatype in allowedTypes is passed, the index of the data in the mark list is returned
If the data is not found, -1 is returned
If the datatype is not one listed, an error is raised
If start is passed the indices >= start will be checked
If end is passed, the indices < end will checked"""
markedString.index.__doc__="""Return index of 'other' in markedString
If str is passed, the internal string is checked for the input data
When found, the index of the start of the substring is returned
If list is passed, the mark list is checked for the sublist pattern given
When found, the index of the start of the sublist is returned
If datatype in allowedTypes is passed, the index of the data in the mark list is returned
If the data is not found, error is raised
If the datatype is not one listed, an error is raised
If start is passed the indices >= start will be checked
If end is passed, the indices < end will checked"""
markedString.isnum.__doc__="""Check if internal string represents a valid number
For non floating-point numbers, this will work identically to markedString.isdigit
This function exists to check if a string is a number, taking into account decimal points"""
markedString.isalnum.__doc__=f"str.isalnum passthrough to internal string\n{str.isalnum.__doc__}"
markedString.isalpha.__doc__=f"str.isalpha passthrough to internal string\n{str.isalpha.__doc__}"
markedString.isascii.__doc__=f"str.isascii passthrough to internal string\n{str.isascii.__doc__}"
markedString.isdecimal.__doc__=f"str.isdecimal passthrough to internal string\n{str.isdecimal.__doc__}"
markedString.isdigit.__doc__=f"str.isdigit passthrough to internal string\n{str.isdigit.__doc__}"
markedString.isidentifier.__doc__=f"str.isidentifier passthrough to internal string\n{str.isidentifier.__doc__}"
markedString.islower.__doc__=f"str.islower passthrough to internal string\n{str.islower.__doc__}"
markedString.isnumeric.__doc__=f"str.isnumeric passthrough to internal string\n{str.isnumeric.__doc__}"
markedString.isprintable.__doc__=f"str.isprintable passthrough to internal string\n{str.isprintable.__doc__}"
markedString.isspace.__doc__=f"str.isspace passthrough to internal string\n{str.isspace.__doc__}"
markedString.istitle.__doc__=f"str.istitle passthrough to internal string\n{str.istitle.__doc__}"
markedString.isupper.__doc__=f"str.isupper passthrough to internal string\n{str.isupper.__doc__}"
markedString.join.__doc__="""Concatenate iterable elements
Source markedString is inserted inbetween elements of the iterable
Works identically to str.join
If a str is passed either on its own or in a list, it is converted into a markedString"""
markedString.lower.__doc__="Return copy of markedString where internal string is all lowercase"
markedString.partition.__doc__="""Partition markedString into 3 pieces by searching for delimeter
First element of tuple is markedString containing string and marks before delimeter
Second element is delimeter
Third element is markedString following delimeter
If delimeter is not found in markedString, markedString followed by two empty markedStrings are returned
If a str is passed, the marks are not taken into account
If a mark list or mark is passed, the string is not taken into account"""
markedString.__lt__.__doc__="Check internal string less than"
markedString.__le__.__doc__="Check internal string greater than"
markedString.__mod__.__doc__="""Replace string mod arguments with input arguments
Works like normal string modulo, extended to markedString
Example:  'Number:%d' % 10 = 'Number:10'
Multiple replacements can be done by passing a tuple or list
Example:  'Time : %d:%d' % (hour,minute)
%d = expected int type
%f = expected float type
%s = expected str type
%m = expected markedString type"""
markedString.__mul__.__doc__="Duplicate markedString for integer number of times"
markedString.__rmul__.__doc__="Duplicate markedString for integer number of times"
#--------------------------------------------------------------------

if __name__=="__main__":
    ignores=['__getattribute__','__rmod__','__new__']
    s=['STR:']
    for a in str.__dict__:
        if not a in markedString.__dict__ and not a in s and not a in ignores:
            s.append(a)
    s.append("LIST:")
    for a in list.__dict__:
        if not a in markedString.__dict__ and not a in s and not a in ignores:
            s.append(a)
    if len(s)>0:
        import os
        os.system("cls")
        print("Needs implementing")
        for a in s:
            print(a)
    else:
        help(markedString)
