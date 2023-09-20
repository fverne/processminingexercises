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
