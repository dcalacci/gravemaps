from ariadne import QueryType, MutationType
from uuid import uuid4
from map import plot_map
query = QueryType()
mutation = MutationType()

maps = []


@query.field("hello")
def resolve_hello(_, info):
    return "Hi there"


class Map:
    def __init__(self, xmin, ymin, xmax, ymax, nGraveyards):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        # SMALL, MEDIUM, or LARGE, indicating # of graveyards to include
        self.nGraveyards = nGraveyards
        self.id = uuid4()
        imageUrl, allGraveyards, totalGraveyards = self.createMapImage()
        self.imageUrl = imageUrl
        self.totalGraveyards = totalGraveyards
        self.allGraveyards = allGraveyards

    def createMapImage(self):
        imageurl, cemeteries, n_graveyards = plot_map([self.ymax, self.ymin, self.xmax,
                                                       self.xmin], self.nGraveyards)
        # imageurl, cemeteries, n_graveyards = plot_map([-71.1929535654,42.2912856611,-70.9781663877,42.4024328423], 'SMALL')
        graveyards = [Graveyard(d) for d in cemeteries]
        # imageurl = "https://go-home-george"
        return (imageurl, graveyards, n_graveyards)


class Graveyard:
    def __init__(self, lat, lng, id, name):
        self.lat = lat
        self.lng = lng
        self.id = id
        self.name = name

    def __init__(self, d):
        self.lat = d['lat']
        self.lng = d['lng']
        self.id = d['id']
        self.name = d['name']


@mutation.field("submitMap")
def resolve_submit_map(_, info, xmin, ymin, xmax, ymax, nGraveyards, mapType):
    print("creating map...")
    newMap = Map(xmin, ymin, xmax, ymax, nGraveyards)
    print("created map! returning...")
    maps.append(newMap)
    return newMap
