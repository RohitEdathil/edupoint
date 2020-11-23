# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 14:05:58 2019

@author: Rohit V
"""

class CORE(object):
    
    def __init__(self,Triggers,TriggerLists):
        self._Out = Triggers
        self._Prob = TriggerLists
        self._Prob.insert(0,[1])
        self._Out.insert(0,None)
        
    def match(self,List,sort=False):
        Prob_list = []
        for TriggerList in self._Prob:
            Trigger_prob = 0
            for word in List:
                if word in TriggerList:
                    Trigger_prob += 1
            Prob_list.append(Trigger_prob)
        if not sort:    
            return self._Out[Prob_list.index(max(Prob_list))]     
        else:
            out_list=[]
            while max(Prob_list)!=0:
                out_list.append(self._Out[Prob_list.index(max(Prob_list))])
                Prob_list.pop(Prob_list.index(max(Prob_list)))
            return out_list      
       
        