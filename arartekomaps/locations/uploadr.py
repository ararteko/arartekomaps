#* - encoding: utf-8 -*
import os
import codecs
from arartekomaps.locations.models import Location

# Cities uploader based on csv herriak.csv
def get_cities():
    loc_file = codecs.open('src/arartekomaps/arartekomaps/locations/herriak.csv','r','utf-8')
    locs = {}
    for line in loc_file.readlines():
        a,b = line.strip().split(',')
        prov,city = a.strip(),b.strip()
        if locs.has_key(prov):
            locs[prov].append(city)
        else:
            locs[prov]=[city]
    
    euskadi=Location(name=u"Euskadi")
    euskadi.save()
    for prob in locs.keys():
        myprob=Location(name=prob,parent=euskadi)
        myprob.save()
        print prob
        for city in locs[prob]:
            mycity = Location(name=city,parent=myprob)
            mycity.save()
            print city
