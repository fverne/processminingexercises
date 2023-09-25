import csv
from itertools import tee, islice, chain
import xml.etree.ElementTree as ET
import datetime


class PetriNet():

    def __init__(self):
        self.places = []
        self.transitions = []
        self.edges = []
        self.markings = []

    def add_place(self, name):
        self.places.append(name)

    def add_transition(self, name, id):
        self.transitions.append([name, id])

    def add_edge(self, source, target):
        self.edges.append([source, target])
        return self

    def get_tokens(self, place):
        return self.markings.count(place)

    def is_enabled(self, transition):
        enabled = False
        prevPlaces = 0
        markedPlaces = 0

        for edge in self.edges:
            if edge[1] == transition:
                prevPlaces = prevPlaces + 1

                if self.markings.count(edge[0]) > 0:
                    markedPlaces = markedPlaces + 1

        if prevPlaces == markedPlaces:
            enabled = True

        return enabled

    def add_marking(self, place):
        self.markings.append(place)

    def fire_transition(self, transition):
        for edge in self.edges:
            if edge[0] == transition:
                self.markings.append(edge[1])

        for edge in self.edges:
            if edge[1] == transition:
                while (self.markings.count(edge[0])):
                    self.markings.remove(edge[0])

    def transition_name_to_id(self, name):
        for transition in self.transitions:
            if transition[0] == name:
                return transition[1]
            
        self.transitions.append()


def read_from_file(filename):
    
    # init
    dict = {}

    xmllog = ET.parse(filename)
    xmlroot = xmllog.getroot()
    traces = xmlroot

    #get traces
    for trace in traces:

        # first find case ID
        caseid = False
        for tracetag in trace:
            if tracetag.tag.find("event") != -1:
                continue

            if tracetag.tag.find("string") and tracetag.attrib.get("key") == "concept:name":
                caseid = tracetag.attrib["value"]
                dict[caseid] = {}

        if trace.tag.find("trace") == -1:
            continue
        
        #get events
        eventamt = 0
        for event in trace:
            if event.tag.find("event") == -1:
                continue
            

            dict[caseid][eventamt] = {}

            for tag in event:
                if tag.tag.find("int") != -1:
                    dict[caseid][eventamt][tag.attrib["key"]] = int(tag.attrib["value"])
                elif tag.tag.find("date") != -1:
                    newtime = datetime.datetime.fromisoformat(tag.attrib["value"])
                    dict[caseid][eventamt][tag.attrib["key"]] = newtime.replace(tzinfo=None)
                else:
                    dict[caseid][eventamt][tag.attrib["key"]] = tag.attrib["value"]


            eventamt += 1

    return dict

def alpha(log):
    print(log)