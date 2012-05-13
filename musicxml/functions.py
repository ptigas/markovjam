#!/usr/bin/python2.5
#
# Copyright 2012 - ptigas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

def chord_simplification( chord ):
    third = 3 # minor
    fifth = 7 # normal fifth
    _type = 'minor'
    
    ch = chord.split('-')
    
    if ch[0] == 'minor' :       # type 1
        third = 3
        fifrth = 7
        _type = 'minor'
    elif ch[0] == 'major' :     # type 2
        third = 4
        fifth = 7
        _type = 'major'
    elif ch[0] == 'dominant' :
        third = 4
        fifth = 7
        _type = 'major'
    elif ch[0] == 'maj69':
        third = 4
        fifth = 7
        _type = 'major'
    elif ch[0] == 'dominant' :  # type 3
        third = 3
        fifth = 6
        _type = 'dominant'
    elif (ch[0] == 'half' and ch[1] == 'diminished') or ch[0] == 'diminished':
        third = 3
        fifth = 6
        _type = 'dominant'
    elif ch[0] == 'augmented' : # type 4
        third = 4
        fifth = 8
        _type = 'augmented'
    elif ch[0] == 'suspended' and ch[1] == 'fourth' :
        third = 5
        fifth = 7
        _type = 'suspended'
    elif ch[0] == 'suspended' and ch[1] == 'second' :
        third = 2
        fifth = 7
        _type = 'suspended'
    else :
        print ch
        raise NameError("Weird chord!")
        
    return (_type, [0, third, fifth])

def transpose( fifths ):
    """ A function to transpose everything to C
    """
    
    # we use shift to transpose to C
    # according the following rules
    # fifths < 0 = a perfect fourth down
    # fifths > 0 = a fifth up
    shift = 0
    if fifths < 0 :
        shift = fifths*5
    else :
        shift = -fifths*7
        
    return shift