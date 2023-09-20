import csv
from itertools import tee, islice, chain
import xml.etree.ElementTree as ET
import datetime

# from stackoverflow
def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)


def log_as_dictionary(log):
    dict = {}
    reader = csv.reader(log.splitlines(), delimiter=";")
    for row in reader:
        if len(row) != 0:
            key = row[1]

            if key not in dict:
                dict[key] = list()

            dict[key].append([row[0], row[2], row[3]])

    return dict


def dependency_graph_inline(log):
    dg = {}

    # create structure
    for key, value in log.items():
        for activity in value:

            dgkey = activity[0]
            if dgkey not in dg:
                dg[dgkey] = {}

            for activity2 in value:
                dgkey2 = activity2[0]
                if dgkey2 not in dg[dgkey]:
                    dg[dgkey][dgkey2] = 0

    # add relations
    for key, value in log.items():
        for prev, item, nxt in previous_and_next(value):
            if nxt:
                dg[item[0]][nxt[0]] += 1


    # cleanup
    for key, value in list(dg.items()):
        for k, v in list(value.items()):
            if v == 0:
                value.pop(k)
        
        if value == {}:
            dg.pop(key)

    return dg



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


def dependency_graph_file(log):
    dg = {}

    endvalue = "issue completion"
    keytotrack = "concept:name"

    # create structure
    for key, value in log.items():
        for _, activity in value.items():

            dgvalue = activity[keytotrack]
            if dgvalue not in dg:
                dg[dgvalue] = {}

            for _, activity2 in value.items():
                dgvalue2 = activity2[keytotrack]
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
