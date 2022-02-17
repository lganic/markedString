def _mask(s: str, chrC: int = 100)-> str:#for error reporting
    if len(s)<chrC:
        return s
    return s[:chrC-3]+'...'

class markedString:
    def __init__(self, sourceString: str, marks: list = None, allowedTypes: list = [int,bool,type(None)][:])-> 'markedString':
        self.__size=len(sourceString)
        self.allowedTypes=allowedTypes
        if marks is not None:
            #if default marks have been passed, check if given mark list is valid
            if len(marks)!=self.__size:
                raise IndexError(f"Given mark list and given string size do not match: {_mask(sourceString)}  {_mask(str(marks))}")
            for item in marks:
                #check that all items in given mark list are valid mark types
                if not type(item) in self.allowedTypes:
                    raise TypeError("Type not recognized as mark: ("+str(type(item)).split("'")[1]+"), change allowedTypes to fix")
        if marks is None:
            #no default marks, initalize mark list to all None
            self.__marks=[None]*self.__size
        else:
            #default marks have been passed, copy into mark list
            self.__marks=marks[:]
        self.__sourceString=sourceString
    def __len__(self)-> int:
        return self.__size
    def __setitem__(self, r: 'slice or index',newVal: 'str object or any type in allowedTypes')-> None:
        p=lambda x:abs(x)-1 if x<0 else x
        #<- function to account for negative index
        if type(r)==slice:
            #if a slice is given, check that the slice is within bounds of string
            f, t, step=r.indices(self.__size)
            if p(f)>=self.__size:
                raise IndexError(f"From range index out of range: {f}, markedString is {self.__size} characters long")
            if p(t-1)>=self.__size:
                raise IndexError(f"To range index out of range: {t}, markedString is {self.__size} characters long")
        if type(r)==int and p(r)>=self.__size:
            #if index is explitly given, check that it falls within markedString
            raise IndexError(f"Index out of range: {r}, markedString is {self.__size} characters long")
        if type(newVal)==list:
            #a list of marks was passed for batch assignment
            #check that a slice was passed, as currently a slice is required for batch assignment
            if type(r)==slice:
                temp=[type(a) in self.allowedTypes for a in newVal]
                #check that all types in input mark list are valid types
                if False in temp:
                    raise TypeError("Type in mark assignment list is not allowed: "+str(type(newVal[temp.index(False)])).split("'")[1])
                del temp
                #check that length of input list and length of slice match
                if t-f!=len(newVal):
                    raise IndexError(f"Mark assignment list length doest not match assigned range: Attempted to store {_mask(str(newVal))} to indices [{f},{t})")
                for sourceIndex, targetIndex in enumerate(range(f,t,step)):
                    #copy data in input mark list to mark list
                    self.__marks[targetIndex]=newVal[sourceIndex]
                return
            if type(r)==int:#error case, see below
                #(might change this later so that when passed batch and index,
                #batch is assigned to elements following and including index)
                raise TypeError(f"Attempting to assign mark assignment list to single index: Attempted to store {_mask(str(newVal))} to index {r}")
                return
            raise TypeError("Index type not recognized: "+str(type(r)).split("'")[1])
        if type(newVal) in self.allowedTypes:
            #a mark type was passed
            if type(r)==slice:
                #index is slice, put new data in all slice indices
                for index in range(f,t,step):
                    self.__marks[index]=newVal
                return
            if type(r)==int:
                #index given, save new mark to index given
                self.__marks[r]=newVal
                return
            raise TypeError("Index type not recognized: "+str(type(r)).split("'")[1])
        if type(newVal)==str:
            #string was passed as data
            if type(r)==slice:
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
            if type(r)==int:
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
            raise TypeError("Index type not recognized: "+str(type(r)).split("'")[1])
        raise TypeError("Input datatype not recognized: "+str(type(newVal)).split("'")[1])
    def __getitem__(self, r: 'slice or index')-> 'mark(s) at index/indices':
        #return mark data at index given
        #if index is int, return element at index
        #if index is slice, return list of elements across slice
        if type(r)==int:
            return self.__marks[r]
        if type(r)==slice:
            return self.__marks[r][:]
        #type was not slice or index, throw error
        raise TypeError("Index type not recognized: "+str(type(r)).split("'")[1])
    def __str__(self)-> str:
        return self.__sourceString
    def __iadd__(self, otherMarkedString: 'markedString')-> None:
        #check that otherMarkedString is of type markedString
        if type(otherMarkedString)!=markedString:
            raise TypeError("Attempting to add "+str(type(otherMarkedString)).split("'")[1]+" to markedString object, only markedString objects can be added together")
        self.__size+=len(otherMarkedString)
        self.__sourceString+=str(otherMarkedString)
        self.__marks+=otherMarkedString[:]
        return self
    def __add__(self, otherMarkedString: 'markedString')-> 'markedString':
        #check that otherMarkedString is of type markedString
        if type(otherMarkedString)!=markedString:
            raise TypeError("Attempting to add "+str(type(otherMarkedString)).split("'")[1]+" to markedString object, only markedString objects can be added together")
        tempStr=self.__sourceString+str(otherMarkedString)
        tempMarks=self.__marks+otherMarkedString[:]
        out=markedString(tempStr,tempMarks)
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
            raise TypeError("Attempting to check equal: "+str(type(otherMarkedString)).split("'")[1]+" to markedString object, only markedString objects can be tested together")
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
    def __ne__(self, other: 'markedString')-> bool:
        #check that type of input is markedString
        if type(other)!=markedString:
            raise TypeError("Attempting to check equal: "+str(type(other)).split("'")[1]+" to markedString object, only markedString objects can be tested together")
        #check that the sizes of the given markedString matches
        #(this would be caught in the main check but its way faster when they are different sizes)
        if self.__size!=len(other):
            return True
        #main not equals check
        return self.__sourceString!=str(other) or self.__marks!=other[:]
    def __repr__(self):
        return self.__sourceString
    def __sizeof__(self):
        return self.__sourceString.__sizeof__()+self.__marks.__sizeof__()+self.__size.__sizeof__()+self.allowedTypes.__sizeof__()
#    def capitalize(self):

#DOCUMENTATION
#--------------------------------------------------------------------
markedString.__add__.__doc__="Add two markedString objects together"
markedString.__contains__.__doc__="""Check if data in contained in markedString
If a string is passed, function returns whether data is in internal string
If data is in allowedTypes, function returns if data is in mark list
If a list of allowedTypes is passed function returns whether list is contained within mark list"""
markedString.__eq__.__doc__="Test if markedString object is equal"
markedString.__len__.__doc__="Return length of internal string"
markedString.__setitem__.__doc__="Assign data to either internal string, or internal mark list\nIf values are of string type, the internal string will be modified\nIf the value is of a type contained in allowedTypes, the internal mark list will be modified.\nslice indexing and assignment is supported\nAssigning a single mark or character to a slice will result in all elements in the slice being updated"
markedString.__doc__="Creates new markedString object from input string\nMarks can be passed, but will default to all None\nallowedTypes are the types which the markedString will recognize as marks when passed as data"
#--------------------------------------------------------------------



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
