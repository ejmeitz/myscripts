from abc import ABC, abstractmethod

class AbstractParsingStrategy(ABC):

    '''
    An interface to be implemented in derived classes by the user. Objects 
    derived from this class can be used to customize the parsing strategy for
    certain output files. Generic output files like log.lammps can be predictably
    parsed, but files created by custom dump or fix commands cannot be generically
    parsed. This class is provides a framework necessary for your parsing strategy to 
    work with the rest of the code base.

    Expects data to be parsed into a dictonary.

    See SimpleParsingStrategy.py as an example implementation of this class.
    '''

    def __init__(self,):
        pass

    @abstractmethod
    def parse(self, path : str, comments = "#", delimiter = ' ') -> dict:
        pass