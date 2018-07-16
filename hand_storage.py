# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 00:33:55 2018

@author: user
"""
import glob
import os

class HandStorage(object):
    
    def __init__(self, path=''):
        
        if path:
            if not os.path.exists(path):
                raise IOError
        
            self.path = path
        else: 
            self.path = os.getcwd()

    def read_hand(self):

        fi = glob.glob(f'{self.path}/**/*.txt', recursive=True)
  
        for file in fi:

            with open(file, encoding='utf-8') as f:

                try:
                    
                    s = f.read()
                    s = s.split('\n\n')
                    for ss in s:
                        if ss == '\n\n' or ss==None or ss=='': 
                            continue
                        yield ss
                        
                except:
                    continue
        
        
                
    
