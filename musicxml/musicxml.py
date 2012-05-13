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

import sys
from functions import chord_simplification
from functions import transpose
from xml.dom.minidom import parse, parseString

VERBOSE = False

_notes = {
    'C' : 0,
    'C#' : 1,
    'D' : 2,
    'D#' : 3,
    'E' : 4,
    'F' : 5,
    'F#' : 6,
    'G' : 7,
    'G#' : 8,
    'A' : 9,
    'A#' : 10,
    'B' : 11
}
_notes_r = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

class Music(object) :
    
    """ A class that handle MusicXML information
    
    This will by our main class. This class will contain
    the measures, the attributes, chords and lotes        
    """
    
    def __init__(self, filename, transpose = False):
        """Inits Music
        
        Args:
        filename: the MusicXML file
        """

        f = open( filename, 'r' )
        data = f.read()
        f.close()

        self.dom = parseString( data )
        self.divisions = 24
        self.fifths = []
        self.mode = 'major'
        self.key_changes = 0
        self.current_fifths = 0
        self.chords_per_fifth = {}
        self.transpose = transpose
        self.measures = []
        self.chord_seqs = []   
        self.repeats = []     
        
    '''
    TODO:I don't handle cases where the measures in the end are like 'repeat those 2 3 times etc'
    '''        
    def parse(self):
        measures = self.dom.getElementsByTagName("measure")
        
        current_chord = ''
        
        if measures :
            if VERBOSE :            
                print len(measures)
                        
            first_key_change = True
            chord_list = []
            repeats = []
            
            last_chord = None
                                 
            measure_counter = 1
            # for each measure in measures
            for m in measures :                
                notes = []   
                #print measure_counter
                
                no_chord_in_this_measure = True                
                
                # There are attributes in the current measure.
                # That might be key modulations or mode changes.
                attributes = m.getElementsByTagName("attributes")
                if attributes :
                    for attr in attributes :
                        for child in attr.childNodes :

                            if child.nodeName == 'divisions' :
                                self.divisions = child.firstChild.data

                            if child.nodeName == 'key' :
                                self.key_changes += 1
                                for c in child.childNodes :
                                    if c.nodeName == 'fifths' :
                                        self.current_fifths = int(c.firstChild.data)
                                        if self.current_fifths not in self.fifths :
                                            self.fifths.append(self.current_fifths)
                                            
                                        if self.current_fifths not in self.chords_per_fifth :
                                            self.chords_per_fifth[self.current_fifths] = []
                                            
                                        if first_key_change :
                                            first_key_change = False
                                        else :                                            
                                            # each time the key change append the chords                           
                                            self.chord_seqs.append(chord_list)                                            
                                        chord_list = []
                                            
                                    if c.nodeName == 'mode' :
                                        self.mode = c.firstChild.data
                                
                for e in m.childNodes :

                    if e.nodeName == 'barline' :                        
                        location = e.getAttributeNode('location').nodeValue
                        
                        if e.getElementsByTagName("repeat") :                        
                            direction = e.getElementsByTagName("repeat")[0].getAttributeNode('direction').nodeValue                          
                            repeats.append([measure_counter, location, direction])
                        
                    if e.nodeName == 'harmony' :
                        harmony = e
                        root = 'F'
                        alter = 0
                        kind_full = ''
                        kind_text = ''
                        root = harmony.getElementsByTagName("root")
                        if root :
                            for r in root[0].childNodes :
                                if r.nodeName == 'root-step' :
                                    root = r.firstChild.data
                                if r.nodeName == 'root-alter' :
                                    alter = int(r.firstChild.data)
                        kind = harmony.getElementsByTagName("kind")
                        if kind :
                            kind_full = kind[0].firstChild.data
                            if 'text' in kind[0].attributes.keys() :
                                kind_text = kind[0].attributes['text'].value
                            
                        # we use shift to transpose to C
                        # according the following rules
                        # fifths < 0 = a perfect fourth down
                        # fifths > 0 = a fifth up
                        shift = 0
                        if self.transpose :
                            shift = transpose( self.current_fifths )
                        
                        chord_root = _notes_r[(_notes[root]+alter+shift)%12]
                        
                        if not root.strip() == '' :
                            no_chord_in_this_measure = False
                            simple = chord_simplification(kind_full)
                            #print "%s: %s"%(current_chord, ','.join(notes))
                            current_chord = "%s%s"%(chord_root, simple[0])
                            #print current_chord,
                            notes = []                            
                            last_chord = current_chord
                            #chord_list.append(current_chord)
                            #print "%s%s\t%s"%(chord_root, simple[0], kind_full)
                        #self.chords_per_fifth[self.current_fifths].append( "%s%s"%(chord_root, kind_text) )
                
                    if e.nodeName == 'note' :        
                        note = e

                        alter = 0
                        note_pitch = 0
                        duration = 0
                        is_rest = False
                        is_chord = False

                        if note.getElementsByTagName("rest") :
                            is_rest = True
                        if note.getElementsByTagName("chord") :
                            is_chord = True

                        dur = note.getElementsByTagName("duration") or None
                        if dur :
                            duration = dur[0].firstChild.data

                        al = note.getElementsByTagName("alter") or None
                        if al :
                            alter = int(al[0].firstChild.data)

                        pitch = note.getElementsByTagName("pitch") or None
                        if pitch :
                            step = pitch[0].getElementsByTagName("step") or None
                            octave = pitch[0].getElementsByTagName("octave") or None
                            if step :
                                note_pitch = step[0].firstChild.data

                        # if transpose then shift to C
                        shift = 0
                        if self.transpose :
                            shift = transpose( self.current_fifths )
                        if not is_rest :
                            notes.append(_notes_r[(_notes[note_pitch]+alter+shift)%12])

                        # print current_chord,                        
                        '''
                        if not is_rest :
                            _note = _notes[note_pitch] + alter
                            print "%s(%d)\t%s"%(_notes_r[(_notes[note_pitch]+alter+shift)%12], int(duration), current_chord)
                        '''
                    
                    '''
                    if no_chord_in_this_measure :
                        if current_chord <> '' :
                            chord_list.append(current_chord)
                    '''
                     
                measure_counter += 1
                #chord_list.append(current_chord)
                chord_list.append(last_chord)
            #print

            
            self.chord_seqs.append(chord_list)
        else:
            sys.exit("Error! No measures found.")
        
        self.repeats = self.process_repeats( repeats )

    def process_repeats( self, repeats ) :
        repeat_tuples = []

        if len(repeats) == 0 :
            return []

        if len(repeats) == 1 and repeats[0][2] == 'forward' :
            return []

        # there is a backward without a forward thus
        # assume the first measure as a forward repeat
        if repeats[0][2] == 'backward' :
            repeats.insert(0, [1,'left','forward'])

        for i in range(0, len(repeats), 2) :
            repeat_tuples.append( (repeats[i+1][0], repeats[i][0]) )

        return repeat_tuples
        
    def __str__(self):
        return ("divisions:%s\nkey:%s\nmode:%s")%(self.divisions, self.fifths, self.mode)
     
def __main__() :
    music = Music(sys.argv[1], transpose = True)
    music.parse()
    
    chordlist = []
    for chords in music.chord_seqs :
        for chord in chords :
            chordlist.append(chord)      

    bar = 1
    res = []
    while bar <= len(chordlist) :
        if chordlist[bar-1] == None :
            chordlist[bar-1] = 'None'
        res.append( chordlist[bar-1] )
        #print bar, chordlist[bar-1]
        if music.repeats <> [] :            
            if bar == music.repeats[0][0] :
                bar = music.repeats[0][1]
                music.repeats.pop(0)
                continue
                #for j in range(music.repeats[0][1],music.repeats[0][0]+1) :
                #    print j

        bar += 1

    print ','.join( res )


__main__()   