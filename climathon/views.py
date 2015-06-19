import datetime
import json
import urllib2
import django
import geopy
from django.http import HttpResponse
from django.shortcuts import render
from geopy.distance import vincenty
import grequests

def index(request):
    return render(request, 'climathon/index.html')

def plots(request):
    return render(request, 'climathon/plots.html')

def search(request, lng, lat):
    postcode = None
    if 'postcode' in request.GET:
        postcode = request.GET['postcode']
        postcode_info = urllib2.urlopen('http://www.uk-postcodes.com/postcode/{}.json'.format(postcode)).read()
        postcode_info = json.loads(postcode_info)
    properties = [{'latitude': x.split(',')[0], 'longitude': x.split(',')[1]} for x in request.GET.getlist('property')]
    # print 'properties: {}'.format(properties)
    max_dist = 5.
    if 'max-dist' in request.GET:
        max_dist = float(request.GET['max-dist'])
    n_days = 14
    if 'n-days' in request.GET:
        n_days = int(request.GET['n-days'])
    sites = urllib2.urlopen('http://api.erg.kcl.ac.uk/Airquality/Information/MonitoringSites/GroupName=London/Json').read()
    sites = json.loads(sites)
    sites = sites['Sites']['Site']
    ordered_sites = []
    for site in sites:
        site_lat = site['@Latitude']
        site_lng = site['@Longitude']
        site['dist'] = vincenty((lat, lng), (site_lat, site_lng)).kilometers
    ordered_sites = sorted(sites, key=lambda x: x['dist'])
    # output2 = {'postcode': {'postcode': postcode, 'longitude': '{:.3f}'.format(lng), 'latitude': '{:.3f}'.format(lat)}, 'sites': []}
    output2 = {'location': {'longitude': '{:.3f}'.format(lng), 'latitude': '{:.3f}'.format(lat)}, 'sites': []}
    if postcode:
        output2['location']['postcode'] = postcode
    current_date = datetime.datetime.now()
    avg_no2 = {}
    counter = {}
    for site in ordered_sites:
        if site['dist'] > 1. * max_dist:
            continue
        output = {}
        output["site_name"] = site["@SiteName"]
        output["site_code"] = site["@SiteCode"]
        output["site_distance"] = '{:.2f}'.format(site["dist"])
        output['site_latitude'] = site['@Latitude']
        output['site_longitude'] = site['@Longitude']
        output["daily_no2_index"] = []
        daily_urls = []
        for i in range(n_days):
            date = (current_date - datetime.timedelta(days=1) - datetime.timedelta(days=i)).date()
            daily_urls.append("http://api.erg.kcl.ac.uk/Airquality/Daily/MonitoringIndex/SiteCode={}/Date={}/Json".format(output["site_code"], date))
        rs = (grequests.get(u) for u in daily_urls)
        all_air_quality = grequests.map(rs)
        valid_air_quality = [x for x in all_air_quality if x.status_code == 200]
        for i, daily_air_quality in enumerate(valid_air_quality):
            date = (current_date - datetime.timedelta(days=1) - datetime.timedelta(days=i)).date()
            daily_air_quality = json.loads(daily_air_quality.content)
            no2_index = None
            species = daily_air_quality["DailyAirQualityIndex"]["LocalAuthority"]["Site"]["Species"]
            if type(species) == list:
                for x in species:
                    if x["@SpeciesCode"] == "NO2":
                        no2_index = int(x["@AirQualityIndex"])
                        output["daily_no2_index"] += [{"date": str(date), "no2_index": no2_index}]
            elif type(species) == dict:
                if species["@SpeciesCode"] == "NO2":
                    no2_index = species["@AirQualityIndex"]
                    output["daily_no2_index"] += [{"date": str(date), "no2_index": no2_index}]
            if date not in avg_no2:
                avg_no2[date] = 0.
                counter[date] = 0
            if no2_index != None:
                avg_no2[date] += int(no2_index)
                counter[date] += 1
        output["daily_no2_index"] = list(reversed(output["daily_no2_index"]))
        site['daily_no2_index'] = output['daily_no2_index']
        output2['sites'] += [output]
    # averaged data
    avg_data = {'dist': 0.}
    # for site in output2['sites']:
    for site in ordered_sites:
        try:
            avg_data['dist'] += site['dist'] * 1. / len(output2['sites'])
        except ZeroDivisionError:
            avg_data['dist'] += 0
    avg_data['avg_no2'] = []
    for date in sorted(avg_no2):
        avg_no2[date] = avg_no2[date] * 1. / counter[date]
        avg_data['avg_no2'] += [{'date': str(date), 'avg_no2': avg_no2[date]}]
    output2['avg_data'] = avg_data

    # property specific results
    for p in properties:
        lat = p['latitude']
        lng = p['longitude']
        property_avg_no2_index = 0.
        total_distance = 0.
        n_sites_queried = 0
        for site in ordered_sites:
            if site['dist'] > 1. * max_dist:
                continue
            if len(site['daily_no2_index']) != 0:
                total_distance += site['dist']
                n_sites_queried += 1
                # print site['@SiteName'], site['dist']
        # print 'total_distance: {}'.format(total_distance)
        for site in ordered_sites:
            if site['dist'] > 1. * max_dist:
                continue
            avg_no2_index = 0.
            sum = 0
            for x in site['daily_no2_index']:
                sum += x['no2_index']
            if sum:
                avg_no2_index = sum * 1. / len(site['daily_no2_index'])
            property_avg_no2_index += avg_no2_index * site['dist'] * 1. / total_distance
        #     counter = 0
        #     for i, daily_air_quality in enumerate(valid_air_quality):
        #         date = (current_date - datetime.timedelta(days=1) - datetime.timedelta(days=i)).date()
        #         daily_air_quality = json.loads(daily_air_quality.content)
        #         no2_index = None
        #         species = daily_air_quality["DailyAirQualityIndex"]["LocalAuthority"]["Site"]["Species"]
        #         if type(species) == list:
        #             for x in species:
        #                 if x["@SpeciesCode"] == "NO2":
        #                     no2_index = int(x["@AirQualityIndex"])
        #         elif type(species) == dict:
        #             if species["@SpeciesCode"] == "NO2":
        #                 no2_index = species["@AirQualityIndex"]
        #         if no2_index != None:
        #             avg_no2_index += no2_index
        #             counter += 1
        #     if counter >= 0:
        #         avg_no2_index = 1. * avg_no2_index / counter
        #         property_avg_no2_index = property_avg_no2_index + avg_no2_index * site['dist'] * 1. / total_distance
        p['avg_no2_index'] = property_avg_no2_index
    output2['properties'] = properties
            
    return HttpResponse(json.dumps(output2), content_type="application/json")
    

def lng_lat_search(request):
    lng = float(request.GET['lng'])
    lat = float(request.GET['lat'])
    return search(request, lng, lat)
    
def postcode_search(request):
    postcode = request.GET['postcode']
    postcode_info = urllib2.urlopen('http://www.uk-postcodes.com/postcode/{}.json'.format(postcode)).read()
    postcode_info = json.loads(postcode_info)
    longitude = postcode_info['geo']['lng']
    latitude = postcode_info['geo']['lat']
    return search(request, longitude, latitude)
