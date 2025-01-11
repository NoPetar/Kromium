from . import exe
from backend import __version__
import platform
import sys

def main():
    
    print(f'Kromium ({__version__}) running on {sys.platform}({platform.system()})')
    while True:
        try:
            _ = input("Kromium >>> ")
            res, err = exe.run("<stdin>", _)
            if err: print(err.as_str())
            elif res: 
                if len(res.elements) == 1:
                    print(repr(res.elements[0]))
                else:
                    print(repr(res))
            
        except (KeyboardInterrupt, EOFError):
            print('Exiting Kromium...')
            sys.exit()
    
