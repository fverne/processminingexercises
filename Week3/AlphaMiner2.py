from itertools import tee, islice, chain
import xml.etree.ElementTree as ET
import datetime

def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)


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
        for origin, target in self.edges:
            if origin == transition:
                self.markings.append(target)

            if target == transition:
                while (self.markings.count(origin) != 0):
                    self.markings.remove(origin)

    def transition_name_to_id(self, name):
        for transition in self.transitions:
            if transition[0] == name:
                return transition[1]


def read_from_file(filename):
    
    # print(filename)
    # if filename == "loan-process.xes":
    #     with open(filename, 'r') as f:
    #         contents = f.read()
    #         print(contents)

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


def dependency_graph_file(log):
    dg = {}

    log = dict(sorted(log.items()))

    endvalue = None
    keytotrack = "concept:name"

    # create structure
    for key, value in log.items():
        for _, activity in value.items():

            dgvalue = activity[keytotrack]
            if dgvalue not in dg:
                dg[dgvalue] = {}

            for _, activity2 in value.items():
                dgvalue2 = activity2[keytotrack]
                endvalue = dgvalue2

                if dgvalue2 not in dg[dgvalue]:
                    dg[dgvalue][dgvalue2] = 0

    # add relations
    templist = []
    for key, value in log.items():
        for _, activities in value.items():
            templist.append(activities[keytotrack])

    for prev, item, nxt in previous_and_next(templist):
        if (item == endvalue):
            continue

        if nxt:
            dg[item][nxt] += 1

    # cleanup
    for key, value in list(dg.items()):
        for k, v in list(value.items()):
            if v == 0:
                value.pop(k)
        
        if value == {}:
            dg.pop(key)

    return dg


def alpha(log):
    petri_net = PetriNet()
    dg = dependency_graph_file(log)

    #build list of possible transitions
    transition_names = []
    for origin, targets in dg.items():
        if transition_names.count(origin) == 0:
            transition_names.append(origin)
        
        for target, _ in targets.items():
            if transition_names.count(target) == 0:
                transition_names.append(target)

    # add transitions
    transition_id = -1
    for transition_name in transition_names:
        petri_net.add_transition(transition_name, transition_id)
        transition_id = transition_id - 1


    # Add start and endplace
    startplace = 0
    place_id = 1
    endplace = 999999
    petri_net.add_place(startplace) #first
    petri_net.add_place(endplace) #last

    petri_net.add_edge(startplace, -1)

    for origin, targets in dg.items():
        for target, _ in targets.items():
            petri_net.add_edge(petri_net.transition_name_to_id(origin), place_id)
            petri_net.add_edge(place_id, petri_net.transition_name_to_id(target))
            petri_net.add_place(place_id)
            place_id = place_id + 1

    petri_net.add_edge(transition_id, endplace)

    return petri_net




