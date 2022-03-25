fType=type

class markedString:#temporary markedString class, gets overwritten. Only here to make type hinting cleaner
    pass

def _mask(s: str, chrC: int = 100)-> str:#for error reporting
    if len(s)<chrC:
        return s
    return s[:chrC-3]+'...'

#determine type of variable passed, and return str version for error reporting
def _typeToStr(variable: type)-> str:
    if fType(variable)==type:
        return str(variable).split("'")[1]
    return str(fType(variable)).split("'")[1]

#convert list to string, but withought padding spaces
def _bLstStr(lst: list)-> str:
    if fType(lst)!=list:
        return str(lst)
    if len(lst)==0:
        return '[]'
    out='['+_bLstStr(lst[0])
    for a in lst[1:]:
        out+=','+_bLstStr(a)
    out+=']'
    return out



class markedString:
    def __init__(self, sourceString: str, marks: list = None, allowedTypes: list = [int,bool,fType(None)][:])-> markedString:
        self.__size=len(sourceString)
        self.allowedTypes=allowedTypes
        if marks is not None:
            #if default marks have been passed, check if given mark list is valid
            if len(marks)!=self.__size:
                raise IndexError(f"Given mark list and given string size do not match: {_mask(sourceString)}  {_mask(_bLstStr(marks))}")
            for item in marks:
                #check that all items in given mark list are valid mark types
                if not fType(item) in self.allowedTypes:
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
        rType=fType(r)
        if fType(newVal)==tuple:
            newVal=list(newVal)
        nType=fType(newVal)
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
                temp=[fType(a) in self.allowedTypes for a in newVal]
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
                self.__size=len(self.__sourceString)
                return
            if rType==int:
                self.__sourceString=self.__sourceString[:r]+str(newVal)+self.__sourceString[r+1:]
                self.__marks=self.__marks[:r]+newVal.marks()+self.__marks[r+1:]
                self.__size=len(self.__sourceString)
                return

        raise TypeError(f"Input datatype not recognized: {_typeToStr(nType)}")
    def __getitem__(self, r: 'index or slice')-> '(ch,mark) or markedString':
        #return mark and data at index given
        #if index is int, return (ch,mark) at index
        #if index is slice, return markedString
        if fType(r)==int:
            return (self.__sourceString[r],self.__marks[r])
        if fType(r)==slice:
            return markedString(self.__sourceString[r],self.__marks[r][:],allowedTypes=self.allowedTypes)
        #type was not slice or index, throw error
        raise TypeError(f"Index type not recognized: {_typeToStr(r)}")
    def __str__(self)-> str:
        return self.__sourceString
    def __iadd__(self, otherMarkedString: markedString)-> None:
        #check that otherMarkedString is of type markedString
        if fType(otherMarkedString)!=markedString:
            raise TypeError(f"Attempting to add {_typeToStr(otherMarkedString)} to markedString object, only markedString objects can be added together")
        self.__size+=len(otherMarkedString)
        self.__sourceString+=str(otherMarkedString)
        self.__marks+=otherMarkedString.marks()
        return self
    def __add__(self, otherMarkedString: markedString)-> markedString:
        #check that otherMarkedString is of type markedString
        if fType(otherMarkedString)!=markedString:
            raise TypeError(f"Attempting to add {_typeToStr(otherMarkedString)} to markedString object, only markedString objects can be added together")
        tempStr=self.__sourceString+str(otherMarkedString)
        tempMarks=self.__marks+otherMarkedString.marks()
        out=markedString(tempStr,tempMarks,allowedTypes=self.allowedTypes)
        return out
    def __contains__(self, data: 'str, markedString, list of allowedTypes, or type in allowedTypes')-> bool:
        dType=fType(data)
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
    def __eq__(self, otherMarkedString: markedString)-> bool:
        if otherMarkedString is None:
            return False
        #check that type of input is markedString
        if fType(otherMarkedString)!=markedString:
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
        if otherMarkedString is None:
            return True
        #check that type of input is markedString
        if fType(other)!=markedString:
            raise TypeError(f"Attempting to check not equal: {_typeToStr(other)} to markedString object, only markedString objects can be tested together")
        #check that the sizes of the given markedString matches
        #(this would be caught in the main check but its way faster when they are different sizes)
        if self.__size!=len(other):
            return True
        #main not equals check
        return self.__sourceString!=str(other) or self.__marks!=other.marks()
    def __repr__(self)-> str:
        if len(self)<1000:
            return f"'{self.__sourceString}' : {_bLstStr(self.__marks)}"#<- this creates cleaner output, but is super slow for large output
        return f"'{self.__sourceString}' : {str(self.__marks)}"
    def __sizeof__(self)-> int:
        return self.__sourceString.__sizeof__()+self.__marks.__sizeof__()+self.__size.__sizeof__()+self.allowedTypes.__sizeof__()
    def __lt__(self,other: 'str or markedString')-> bool:
        if fType(other)==markedString:
            return self.__sourceString<str(other)
        if fType(other)==str:
            return self.__sourceString<other
        raise TypeError(f"Type not recognized for less than comparison: '{_typeToStr(other)}' type must be either str or markedString")
    def __le__(self,other: 'str or markedString')-> bool:
        if fType(other)==markedString:
            return self.__sourceString<=str(other)
        if fType(other)==str:
            return self.__sourceString<=other
        raise TypeError(f"Type not recognized for less than/eq comparison: '{_typeToStr(other)}' type must be either str or markedString")
    def __gt__(self,other: 'str or markedString')-> bool:
        if fType(other)==markedString:
            return self.__sourceString>str(other)
        if fType(other)==str:
            return self.__sourceString>other
        raise TypeError(f"Type not recognized for less than comparison: '{_typeToStr(other)}' type must be either str or markedString")
    def __ge__(self,other: 'str or markedString')-> bool:
        if fType(other)==markedString:
            return self.__sourceString>=str(other)
        if fType(other)==str:
            return self.__sourceString>=other
        raise TypeError(f"Type not recognized for less than/eq comparison: '{_typeToStr(other)}' type must be either str or markedString")
    def __mod__(self,other)->markedString:
        if fType(other)!=tuple and fType(other)!=list:
            other=(other,)
        if len(other)!=self.__sourceString.count("%"):
            raise TypeError(f"Number of format options does not equal number of arguments given: '{_mask(self.__sourceString)}' given {len(other)} arguments")
        selfCopy=self[:]
        letterCodes={'f':float,'d':int,'s':str,'m':markedString}
        for index, item in enumerate(other):
            fInd=self.__sourceString.find('%')
            lTy=self.__sourceString[fInd+1]
            if fType(item)!=letterCodes[lTy]:
                raise TypeError(f"Mod string not given correct types, item:{index} expected: '{_typeToStr(letterCodes[lTy])}' but got '{_typeToStr(item)}'")
            if fType(item)!=markedString:
                item=markedString(str(item),allowedTypes=self.allowedTypes)
            selfCopy=selfCopy[:fInd]+item+selfCopy[fInd+2:]
        return selfCopy
    def __rmod__(self,other)->markedString:
        if fType(other)!=tuple and fType(other)!=list:
            other=(other,)
        other=other[::-1]
        if len(other)!=self.__sourceString.count("%"):
            raise TypeError(f"Number of format options does not equal number of arguments given: '{_mask(self.__sourceString)}' given {len(other)} arguments")
        selfCopy=self[:]
        letterCodes={'f':float,'d':int,'s':str,'m':markedString}
        for index, item in enumerate(other):
            fInd=self.__sourceString.find('%')
            lTy=self.__sourceString[fInd+1]
            if fType(item)!=letterCodes[lTy]:
                raise TypeError(f"Mod string not given correct types, item:{index} expected: '{_typeToStr(letterCodes[lTy])}' but got '{_typeToStr(item)}'")
            if fType(item)!=markedString:
                item=markedString(str(item),allowedTypes=self.allowedTypes)
            selfCopy=selfCopy[:fInd]+item+selfCopy[fInd+2:]
        return selfCopy
    def __mul__(self,value:int)->markedString:
        if fType(value)!=int:
            raise TypeError(f"Requires int type for markedString multiplication, got type: '{_typeToStr(value)}'")
        if value<=0:
            return markedString("")
        mLst=self.__marks[:]*value
        mStr=self.__sourceString*value
        return markedString(mStr,mLst,allowedTypes=self.allowedTypes[:])
    def __rmul__(self,value:int)->markedString:
        if fType(value)!=int:
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
        if fType(other)==tuple:
            other=list(other)
        dType=fType(other)
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
        if fType(other)==tuple:
            other=list(other)
        dType=fType(other)
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
    def rfind(self,other: 'str, markedString, list of allowedTypes, or type in allowedTypes',start=None,end=None)-> int:
        if start==None:
            start=0
        if end==None:
            end=self.__size
        if fType(other)==tuple:
            other=list(other)
        dType=fType(other)
        if dType in self.allowedTypes:#if datatype is mark check if mark list contains data
            try:
                return self.__marks.rindex(other,start,end)#attempt list index
            except ValueError:
                return -1#item not in list, return -1
        if dType==list:
            if len(other)<=len(self.__marks):#check if input is larger than mark list size
                for index in range(end-len(other),start-1,-1):#loop over possible indicies for sublist
                    if self.__marks[index:index+len(other)]==other:#check list
                        return index
            return -1
        if dType==str:
            return self.__sourceString.rfind(other,start,end)
        if dType==markedString:
            searchList=other.marks()#load substring data, for optimization
            searchStr=str(other)
            searchListSize=len(searchList)
            while True:
                fI=self.__sourceString.rfind(searchStr,start,end)#find substring index in source string
                if fI==-1 or fI>=end:#check if substring found, and that found substring is in range
                    return -1
                #check if list at index matches target list
                if self.__marks[fI:fI+len(searchList)]==searchList:
                    return fI
                end=fI
        raise TypeError(f"Type given has no correlation to this markedString, given type: {_typeToStr(dType)}, Expected types: str,list or any in list:{str([_typeToStr(a) for a in self.allowedTypes])}")
    def index(self,other: 'str, markedString, list of allowedTypes, or type in allowedTypes',start=None,end=None)-> int:
        if start==None:
            start=0
        if end==None:
            end=self.__size
        if fType(other)==tuple:
            other=list(other)
        dType=fType(other)
        if dType in self.allowedTypes:#if datatype is mark check if mark list contains data
            try:
                return self.__marks.index(other,start,end)#attempt list index
            except ValueError:
                raise ValueError(f"Item not in mark list")#item not in list, return -1
        if dType==list:
            if len(other)<=len(self.__marks):#check if input is larger than mark list size
                for index in range(start,min(len(self.__marks)-len(other)+1,end)):#loop over possible indicies for sublist
                    if self.__marks[index:index+len(other)]==other:#check list
                        return index
            raise ValueError(f"List substring not found in markedString")
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
    def rindex(self,other: 'str, markedString, list of allowedTypes, or type in allowedTypes',start=None,end=None)-> int:
        if start==None:
            start=0
        if end==None:
            end=self.__size
        if fType(other)==tuple:
            other=list(other)
        dType=fType(other)
        if dType in self.allowedTypes:#if datatype is mark check if mark list contains data
            try:
                return self.__marks.rindex(other,start,end)#attempt list index
            except ValueError:
                raise ValueError("Mark not found in mark list")
        if dType==list:
            if len(other)<=len(self.__marks):#check if input is larger than mark list size
                for index in range(end-len(other),start-1,-1):#loop over possible indicies for sublist
                    if self.__marks[index:index+len(other)]==other:#check list
                        return index
            raise ValueError("Sublist not found in mark list")
        if dType==str:
            return self.__sourceString.rindex(other,start,end)
        if dType==markedString:
            searchList=other.marks()#load substring data, for optimization
            searchStr=str(other)
            searchListSize=len(searchList)
            while True:
                fI=self.__sourceString.rfind(searchStr,start,end)#find substring index in source string
                if fI==-1 or fI>=end:#check if substring found, and that found substring is in range
                    raise ValueError("markedString not found in markedString")
                #check if list at index matches target list
                if self.__marks[fI:fI+len(searchList)]==searchList:
                    return fI
                end=fI
        raise TypeError(f"Type given has no correlation to this markedString, given type: {_typeToStr(dType)}, Expected types: str,list or any in list:{str([_typeToStr(a) for a in self.allowedTypes])}")
    def isalnum(self) -> bool:
        return self.__sourceString.isalnum(data)
    def isnum(self) -> bool:
        return self.__sourceString.replace(".","",1).isdigit()
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
        if fType(iterable)==str:
            #if iterable is string, convert to markedString
            iterable=markedString(iterable,allowedTypes=self.allowedTypes)
        if fType(iterable)==markedString:
            tS=self.__sourceString.join(str(iterable[:]))#create output string using string join
            tml=iterable.marks()#load iterables mark list
            tL=[tml[0]]#create output mark list object from first object in mark list
            for mark in tml[1:]:#loop over all marks except the first
                tL+=self.__marks#add copy of mark list
                tL+=[mark]#add next mark
            return markedString(tS,tL,allowedTypes=self.allowedTypes)
        if fType(iterable)==tuple:
            iterable=list(tuple)
        if fType(iterable)==list:
            #I assume 1 dimensional list that is not jagged
            if len(iterable)==0:
                #account for empty input list
                return markedString("",[],allowedTypes=self.allowedTypes)
            if fType(iterable[0])==str:
                #iterable is list of strings, convert all strings in list to markedString
                for i, a in enumerate(iterable):
                    iterable[i]=markedString(a,allowedTypes=self.allowedTypes)
            elif fType(iterable[0])!=markedString:#iterable is not of recognized type, throw error
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
    def replace(self,old: 'str,markedString,list of allowedTypes, or type in allowedTypes',new: markedString,count: int =None)->markedString:
        #check input types
        if fType(new)!=markedString:
            raise TypeError(f"New string must be markedString, type: '{_typeToStr(new)}' is not recognized")
        oT=fType(old)
        if oT!=str and oT!=markedString and oT!=list and not oT in self.allowedTypes:
            raise TypeError(f"Type not recognized for markedString replace: '{_typeToStr(oT)}'")
        #create copy of self for output
        selfCopy=self[:]
        #'infinity' class for infinite replace count
        class inf:
            def __isub__(self,o):
                return self
            def __gt__(self,o):
                return True
        if count==None:
            count=inf()
        lR=0
        #if oT in self.allowedTypes old is a mark, and therefore only has len 1
        if oT in self.allowedTypes:
            oldSize=1
        else:
            oldSize=len(old)
        newSize=len(new)
        #if count is inf count>0 is always true
        while count>0:
            count-=1
            #find next index
            fInd=selfCopy.find(old,lR)
            #substring not found, return current markedString
            if fInd==-1:
                return selfCopy
            #crop around substring, and insert new string
            selfCopy=selfCopy[:fInd]+new+selfCopy[fInd+oldSize:]
            #update lower range for find
            lR=fInd+newSize
        return selfCopy
    def split(self,sep : 'str,markedString,list of allowedTypes, type in allowedTypes'=None,maxSplit : int = None)->'list of markedString':
        #determine type of the seperator now, for optimization purposes
        sT=fType(sep)
        if sT!=str and sT!=markedString and sT!=list and not sT in self.allowedTypes:
            raise TypeError(f"Type not recognized for markedString split: '{_typeToStr(sT)}'")
        #if the seperator is none, return copy of self in list
        if sep==None:
            return [self[:]]
        #'infinity' class for infinite split count
        class inf:
            def __isub__(self,o):
                return self
            def __gt__(self,o):
                return True
        if maxSplit==None:
            maxSplit=inf()
        lR=0
        outputList=[]
        #is sT in self.allowedTypes seperator is a single element, so length 1
        if sT in self.allowedTypes:
            sepLen=1
        else:
            sepLen=len(sep)
        #if maxSplit is inf maxSplit>0 is always true
        while maxSplit>0:
            maxSplit-=1
            #get index of next seperator
            index=self.find(sep,lR)
            #if seperator not found break out of loop
            if index==-1:
                break
            else:
                #seperator found, append substring to output
                outputList.append(self[lR:index])
            #assign index after current seperator to lower find range
            lR=index+sepLen
        #get string after last found seperator
        outputList.append(self[lR:])
        return outputList
    def rsplit(self,sep : 'str,markedString,list of allowedTypes, type in allowedTypes'=None,maxSplit : int = None)->'list of markedString':
        #determine type of the seperator now, for optimization purposes
        sT=fType(sep)
        if sT!=str and sT!=markedString and sT!=list and not sT in self.allowedTypes:
            raise TypeError(f"Type not recognized for markedString split: '{_typeToStr(sT)}'")
        #if the seperator is none, return copy of self in list
        if sep==None:
            return [self[:]]
        #'infinity' class for infinite split count
        class inf:
            def __isub__(self,o):
                return self
            def __gt__(self,o):
                return True
        if maxSplit==None:
            maxSplit=inf()
        uR=self.__size
        outputList=[]
        #is sT in self.allowedTypes seperator is a single element, so length 1
        if sT in self.allowedTypes:
            sepLen=1
        else:
            sepLen=len(sep)
        #if maxSplit is inf maxSplit>0 is always true
        while maxSplit>0:
            maxSplit-=1
            #get index of next seperator
            index=self.rfind(sep,0,uR)
            #if seperator not found break out of loop
            if index==-1:
                break
            else:
                #seperator found, prepend substring to output
                print(self[index+sepLen:uR])
                outputList=[self[index+sepLen:uR]]+outputList#Why is this not reversed
            #assign index after current seperator to lower find range
            uR=index
        #get string after last found seperator
        outputList=[self[:uR]]+outputList
        return outputList
    def title(self):
        return markedString(self.__sourceString.title(),self.__marks[:],allowedTypes=self.allowedTypes)
    def center(self,width,fillMarkedString=None):
        width-=self.__size
        #copy self for output
        selfCopy=self[:]
        #"error" case
        if width<=0:
            return selfCopy
        #if fillMarkedString is not defined, create a new markedString with 1 char space
        if fillMarkedString is None:
            fillMarkedString=markedString(" ",allowedTypes=self.allowedTypes)
        elif len(fillMarkedString)!=1:#check error
            raise TypeError("fill string must be 1 character long")
        #create output string
        selfCopy=fillMarkedString*(width//2)+selfCopy+fillMarkedString*(width//2+width%2)
        return selfCopy
    def count(self,sub:'str,markedString,allowedType,list of allowedTypes')-> int:
        #get type of input
        sT=fType(sub)
        if sT==str:
            return self.__sourceString.count(sub)
        if sT in self.allowedTypes:
            return self.__marks.count(sub)
        if sT==list:
            #determine length of sub given
            lSo=len(sub)
            index=0
            count=0
            while index+lSo<=self.__size:#loop over all possible list locations
                if self.__marks[index]==sub[0]:#if first index corrent
                    for b in range(1,lSo):
                        index+=1
                        if self.__marks[index]!=sub[b]:#if next element of sublist is not valid, stop checking
                            count-=1
                            index-=1
                            break
                    count+=1
                index+=1
            return count
        if sT==markedString:
            #determine length of sub given
            lSo=len(sub)
            index=0
            count=0
            while index+lSo<=self.__size:#loop over all possible list locations
                if self[index]==sub[0]:#if first index corrent
                    for b in range(1,lSo):
                        index+=1
                        if self[index]!=sub[b]:#if next element of sublist is not valid, stop checking
                            count-=1
                            index-=1
                            break
                    count+=1
                index+=1
            return count
        raise TypeError(f"Type not recognized for markedString count, expected str,markedString,allowedType or list of allowedType. Got: '{_typeToStr(sT)}'")
    def ljust(self,width,fillMarkedString=None):
        width-=self.__size
        #copy self for output
        selfCopy=self[:]
        #"error" case
        if width<=0:
            return selfCopy
        #if fillMarkedString is not defined, create a new markedString with 1 char space
        if fillMarkedString is None:
            fillMarkedString=markedString(" ",allowedTypes=self.allowedTypes)
        elif len(fillMarkedString)!=1:#check error
            raise TypeError("fill string must be 1 character long")
        #create output string
        selfCopy=selfCopy+fillMarkedString*width
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
markedString.partition.__doc__="""Partition markedString into 3 pieces by searching for delimiter
First element of tuple is markedString containing string and marks before delimiter
Second element is delimiter
Third element is markedString following delimiter
If delimiter is not found in markedString, markedString followed by two empty markedStrings are returned
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
markedString.replace.__doc__="""Replace old value with markedString
Count describes number of replacements, if it is None all old values will be replaced"""
markedString.split.__doc__="""Split markedString by seperator
maxSplit is number of splits which will occur, if maxSplit is None, there is not limit"""
markedString.rfind.__doc__="""Find substring, sublist or mark, from back of markedString
Return -1 if not found"""
markedString.rindex.__doc__="""Find substring, sublist or mark, from back of markedString
Raise ValueError if not found"""
markedString.rsplit.__doc__="""Split string by delimiter, starting from the back
maxSplit describes number of splits to occur, if None there is no limit"""
markedString.title.__doc__="""Return new markedString where all words have their first
letter capitalized"""
markedString.center.__doc__="""Return new markedString where string is centered with padding spaces
if fillMarkedString is passed, the padding will be the markedString
fillMarkedString must be length 1, if it is not TypeError is thrown"""
markedString.count.__doc__="""Return number of non overlapping occurences of input"""
markedString.ljust.__doc__="""Return new markedString, justified to the left by padding spaces
if fillMarkedString is passed, the padding will be the markedString
fillMarkedString must be length 1, if it is not TypeError is thrown"""
#--------------------------------------------------------------------

if __name__=="__main__":
    ignores=['__getattribute__','__new__',"encode","casefold","expandtabs"]
    s=['STR:']
    for a in str.__dict__:
        if not a in markedString.__dict__ and not a in s and not a in ignores:
            s.append(a)
    s.append("LIST:")
    for a in list.__dict__:
        if not a in markedString.__dict__ and not a in s and not a in ignores:
            s.append(a)
    if len(s)>0:
        print("Needs implementing")
        for a in s:
            print(a)
    else:
        help(markedString)
