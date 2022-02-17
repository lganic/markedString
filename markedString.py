def _mask(s: str, chrC: int = 100)-> str:
    if len(s)<chrC:
        return s
    return s[:chrC-3]+'...'

class markedString:
    def __init__(self,sourceString: str,marks: list = None,allowedTypes: list = [int,bool,type(None)][:])-> 'markedString':
        self.__size=len(sourceString)
        self.allowedTypes=allowedTypes
        if marks is not None:
            if len(marks)!=self.__size:
                raise IndexError(f"Given mark list and given string size do not match: {_mask(sourceString)}  {_mask(str(marks))}")
            for item in marks:
                if not type(item) in marks:
                    raise TypeError("Type not recognized as mark: "+str(type(item)).split("'")[1]+" change allowedTypes to fix")
        if marks==None:
            self.__marks=[None]*self.__size
        else:
            self.__marks=marks[:]
        self.__sourceString=sourceString
    def __len__(self)-> int:
        return self.__size
    def __setitem__(self,r: 'slice or index',newVal: 'str object or any type in allowedTypes')-> None:
#        f, t, step=(None,None,None)
        if type(r)==slice:
            p=lambda x:abs(x)-1 if x<0 else x
            f, t, step=r.indices(self.__size)
            if p(f)>=self.__size:
                raise IndexError(f"From range index out of range: {f}, markedString is {self.__size} characters long")
            if p(t-1)>=self.__size:
                raise IndexError(f"To range index out of range: {t}, markedString is {self.__size} characters long")
        if type(r)==int:
            if _procIndex(r)>=self.__size:
                raise IndexError(f"Index out of range: {r}, markedString is {self.__size} characters long")
        if type(newVal)==list:
            if type(r)==slice:
                temp=[type(a) in self.allowedTypes for a in newVal]
                if False in temp:
                    raise TypeError("Type in mark assignment list is not allowed: "+str(type(newVal[temp.index(False)])).split("'")[1])
                del temp
                if t-f!=len(newVal):
                    raise IndexError(f"Mark assignment list length doest not match assigned range: Attempted to store {_mask(str(newVal))} to indices [{f},{t})")
                for sourceIndex, targetIndex in enumerate(range(f,t,step)):
                    self.__marks[targetIndex]=newVal[sourceIndex]
                return
            if type(r)==int:
                raise TypeError(f"Attempting to assign mark assignment list to single index: Attempted to store {_mask(str(newVal))} to index {r}")
                return
            raise TypeError("Index type not recognized: "+str(type(r)).split("'")[1])
        if type(newVal) in self.allowedTypes:
            if type(r)==slice:
                for index in range(f,t,step):
                    self.__marks[index]=newVal
                return
            if type(r)==int:
                self.__marks[r]=newVal
                return
            raise TypeError("Index type not recognized: "+str(type(r)).split("'")[1])
        if type(newVal)==str:
            if type(r)==slice:
                if len(newVal)!=1:
                    if t-f!=len(newVal):
                        raise IndexError(f"String length does not match assigned range: Attempted to store '{_mask(newVal)}' to indices [{f},{t})")
                    unpacked=[a for a in self.__sourceString]
                    for sourceIndex, targetIndex in enumerate(range(f,t,step)):
                        unpacked[targetIndex]=newVal[sourceIndex]
                    self.__sourceString=''.join(unpacked)
                else:
                    unpacked=[a for a in self.__sourceString]
                    for index in range(f,t,step):
                        unpacked[index]=newVal
                    self.__sourceString=''.join(unpacked)
                return
            if type(r)==int:
                if len(newVal)!=1:
                    raise IndexError(f"Attempting to assign multiple characters to single index:  Attempted '{_mask(newVal)}' -> Index {r}")
                unpacked=[a for a in self.__sourceString]
                unpacked[r]=newVal
                self.__sourceString=''.join(unpacked)
                return
            raise TypeError("Index type not recognized: "+str(type(r)).split("'")[1])
        raise TypeError("Input datatype not recognized: "+str(type(newVal)).split("'")[1])
    def __getitem__(self,r: 'slice or index')-> 'mark(s) at index/indices':
        if type(r)==int:
            return self.__marks[r]
        if type(r)==slice:
            return self.__marks[r][:]
        raise TypeError("Index type not recognized: "+str(type(r)).split("'")[1])
    def __str__(self)-> str:
        return self.__sourceString
    def __iadd__(self,other: 'markedString')-> None:
        if type(other)!=markedString:
            raise TypeError("Attempting to add "+str(type(other)).split("'")[1]+" to markedString object, only markedString objects can be added together")
        self.__size+=len(other)
        self.__sourceString+=str(other)
        self.__marks+=other[:]
        return self
    def __add__(self,other: 'markedString')-> 'markedString':
        if type(other)!=markedString:
            raise TypeError("Attempting to add "+str(type(other)).split("'")[1]+" to markedString object, only markedString objects can be added together")
        tempStr=self.__sourceString+str(other)
        tempMarks=self.__marks+other[:]
        out=markedString(tempStr)
        out[:]=tempMarks
        return out
    def __contains__(self,data: 'datatype in allowedTypes or str or list of allowedTypes')-> bool:
        if type(data) in self.allowedTypes:
            return data in self.__marks
        if type(data)==str:
            return data in self.__sourceString
        if type(data)==list:
            if len(data)>len(self.__marks):
                for index in range(0,len(self.__marks)-len(data)+1):
                    if self.__marks[index:index+len(data)]==data:
                        return True
        return False
    def __eq__(self,other,data: 'datatype in allowedTypes or str')-> bool:
        if type(other)!=markedString:
            raise TypeError("Attempting to check equal: "+str(type(other)).split("'")[1]+" to markedString object, only markedString objects can be tested together")
        if self.__size!=len(other):
            return False
        return self.__sourceString==str(other) and self.__marks==other[:]
    def __iter__(self)-> 'iterator -> (character, mark)':
        for mark, ch in zip(self.__marks,self.__sourceString):
            yield (ch,mark)
        raise StopIteration
    def __ne__(self,other: 'markedString')-> bool:
        if type(other)!=markedString:
            raise TypeError("Attempting to check equal: "+str(type(other)).split("'")[1]+" to markedString object, only markedString objects can be tested together")
        if self.__size!=len(other):
            return True
        return self.__sourceString!=str(other) or self.__marks!=other[:]
    def __repr__(self):
        return self.__sourceString
    def __sizeof__(self):
        return self.__sourceString.__sizeof__()+self.__marks.__sizeof__()+self.__size.__sizeof__()+self.allowedTypes.__sizeof__()
#    def capitalize(self):

markedString.__add__.__doc__="Add two markedString objects together"
markedString.__contains__.__doc__="Check if data in contained in markedString\nIf a string is passed, function returns whether data is in internal string\nIf data is in allowedTypes, function returns if data is in mark list\nIf a list of allowedTypes is passed function returns whether list is contained within mark list"
markedString.__eq__.__doc__="Test if markedString object is equal"

markedString.__len__.__doc__="Return length of internal string"
markedString.__setitem__.__doc__="Assign data to either internal string, or internal mark list\nIf values are of string type, the internal string will be modified\nIf the value is of a type contained in allowedTypes, the internal mark list will be modified.\nslice indexing and assignment is supported\nAssigning a single mark or character to a slice will result in all elements in the slice being updated"
markedString.__doc__="Creates new markedString object from input string\nMarks can be passed, but will default to all None\nallowedTypes are the types which the markedString will recognize as marks when passed as data"




#capitalize
#endswith
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



if __name__=="__main__":
    help(markedString)
