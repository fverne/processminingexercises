from itertools import tee, islice, chain, permutations, combinations
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
    
    print(filename)
    # if filename == "loan-process.xes":
    # with open(filename, 'r') as f:
    #     contents = f.read()
    #     print(contents)

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
    
    # create transitions
    transitions = []
    transitions_start = []
    transitions_end = []
    activitykey = "concept:name"

    for caseid, case in log.items():
        for activityid, activity in case.items():

            # identify input transitions for later use
            if activityid == 0 and transitions_start.count(activity[activitykey]) == 0:
                transitions_start.append(activity[activitykey])
            
            # identify output transitions for later use
            if activityid == len(case) - 1 and transitions_end.count(activity[activitykey]) == 0:
                transitions_end.append(activity[activitykey])

            # add transitions to total list
            if transitions.count(activity[activitykey]) == 0:
                transitions.append(activity[activitykey])

    
    
    # figure out relations in pairs - direct succession, causal, parallel, choice
    ## direct succession
    direct_successions = set()
    for case in list(log.values()):
        activities = list(case.values())
        for a, b in zip(activities, activities[1:]):
            direct_successions.add((a[activitykey], b[activitykey]))

    ## causals
    causals = set()
    for pair in direct_successions:
        if pair[::-1] not in direct_successions:
            causals.add(pair)

    ## parallels
    parallels = set()
    for pair in direct_successions:
        if pair[::-1] in direct_successions:
            parallels.add(pair)
    
    ## choice
    choices = set()
    permuts = permutations(transitions, 2)
    for pair in permuts:
        if pair not in causals and pair[::-1] not in causals and pair not in parallels:
            choices.add(pair)
    
    # create X_w
    Xw = set()
    combis = (combinations(transitions, i) for i in range(1, len(transitions) + 1))
    subsets = chain.from_iterable(combis)
    
    for pair in transitions:
        

    # create places for each element in Y_w
    

    # create special place for input, output

    # define flow relationships



    return petri_net

alpha(read_from_file("extension-log-3.xes"))


