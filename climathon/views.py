import datetime
import json
import urllib2
import django
import geopy
from django.http import HttpResponse
from django.shortcuts import render
from geopy.distance import vincenty

def index(request):
    return render(request, 'climathon/index.html')

def postcode_search(request):
    postcode = request.GET['postcode']
    postcode_info = urllib2.urlopen('http://www.uk-postcodes.com/postcode/{}.json'.format(postcode)).read()
    postcode_info = json.loads(postcode_info)
    longitude = postcode_info['geo']['lng']
    latitude = postcode_info['geo']['lat']
    sites = urllib2.urlopen('http://api.erg.kcl.ac.uk/Airquality/Information/MonitoringSites/GroupName=London/Json').read()
    sites = json.loads(sites)
    sites = sites['Sites']['Site']
    ordered_sites = []
    for site in sites:
        site_lat = site['@Latitude']
        site_lng = site['@Longitude']
        site['dist'] = vincenty((latitude, longitude), (site_lat, site_lng)).kilometers
    ordered_sites = sorted(sites, key=lambda x: x['dist'])[:1]
#     for site in ordered_sites:
#         monitoring_index = urllib2.urlopen('http://api.erg.kcl.ac.uk/Airquality/Hourly/MonitoringIndex/SiteCode={}/Json'.format(site['@SiteCode'])).read()
#         monitoring_index = json.loads(monitoring_index)
#         try:
#             site['monitoring_index'] = monitoring_index['HourlyAirQualityIndex']['LocalAuthority']['Site']['species']
#         except TypeError:
#             site['monitoring_index'] = None
    output2 = []
    current_date = datetime.datetime.now()
    for site in ordered_sites:
        output = {}
        output["site_name"] = site["@SiteName"]
        output["site_code"] = site["@SiteCode"]
        output["site_distance"] = site["dist"]
        output["daily_no2_index"] = []
#         for i in range(30):
        for i in range(365):
            date = (current_date - datetime.timedelta(days=1) - datetime.timedelta(days=i)).date()
            try:
                daily_air_quality = urllib2.urlopen("http://api.erg.kcl.ac.uk/Airquality/Daily/MonitoringIndex/SiteCode={}/Date={}/Json".format(output["site_code"], date)).read()
            except:
                continue
            daily_air_quality = json.loads(daily_air_quality)
            no2_index = None
            print daily_air_quality["DailyAirQualityIndex"]
            print daily_air_quality["DailyAirQualityIndex"]["LocalAuthority"]["Site"]
            species = daily_air_quality["DailyAirQualityIndex"]["LocalAuthority"]["Site"]["Species"]
            if type(species) == list:
                for x in species:
                    if x["@SpeciesCode"] == "NO2":
                        no2_index = x["@AirQualityIndex"]
                output["daily_no2_index"] += [{"date": str(date), "no2_index": no2_index}]
            elif type(species) == dict:
                if species["@SpeciesCode"] == "NO2":
                    no2_index = species["@AirQualityIndex"]
#         if site["monitoring_index"] == None:
#             print "no data"
#             continue
#         else:
#             if type(site["monitoring_index"]) == dict:
#                 if site["monitoring_index"]["@SpeciesCode"] == "NO2":
#                     output["NO2Index"] = site["monitoring_index"]["@AirQualityIndex"]
#             elif type(site["monitoring_index"]) == list:
#                 print "type list"
#                 for x in site["monitoring_index"]:
#                     if x["@SpeciesCode"] == "NO2":
#                         output["NO2Index"] = x["@AirQualityIndex"]
#                     break
#             else:
#                 continue
        output2 += [output]
    return HttpResponse("{}".format(output2), content_type="application/json")
