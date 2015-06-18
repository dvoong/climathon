import json
import urllib2
import pprint as pp

print 'Sites'
sites = urllib2.urlopen('http://api.erg.kcl.ac.uk/Airquality/Information/MonitoringSites/GroupName=London/Json').read()
sites = json.loads(sites)
sites = sites['Sites']['Site']
pp.pprint(sites[:3])
print

print 'AirQualitySpecies'
species = urllib2.urlopen('http://api.erg.kcl.ac.uk/Airquality/Information/Species/Json').read()
species = json.loads(species)
species = species['AirQualitySpecies']['Species']
pp.pprint(species[:3])
print

print 'AirQualityObjective'
objectives = urllib2.urlopen('http://api.erg.kcl.ac.uk/Airquality/Information/Objective/Json').read()
objectives = json.loads(objectives)
objectives = objectives['AirQualityObjectives']['Species']
pp.pprint(objectives[:3])
print

print 'AirQualityIndexHealthAdvice'
advice = urllib2.urlopen('http://api.erg.kcl.ac.uk/Airquality/Information/IndexHealthAdvice/Json').read()
advice = json.loads(advice)
advice = advice['AirQualityIndexHealthAdvice']['HealthAdvice']
pp.pprint(advice[:3])
print

print 'MonitoringIndex'
# Barking and Dagenham - Rush Green
monitoring_index = urllib2.urlopen('http://api.erg.kcl.ac.uk/Airquality/Hourly/MonitoringIndex/SiteCode=BG1/Json').read()
monitoring_index = json.loads(monitoring_index)
pp.pprint(monitoring_index)
print

print  'MonitoringIndices - Hourly'
monitoring_indices = urllib2.urlopen('http://api.erg.kcl.ac.uk/AirQuality/Hourly/MonitoringIndex/GroupName=London/Json').read()
monitoring_indices = json.loads(monitoring_indices)
monitoring_indices = monitoring_indices['HourlyAirQualityIndex']
pp.pprint(monitoring_indices['LocalAuthority'][:1])
print

print 'MonitoringIndices - Daily'
monitoring_indices = urllib2.urlopen('http://api.erg.kcl.ac.uk/AirQuality/Daily/MonitoringIndex/GroupName=London/Date=2014-12-31/Json').read()
monitoring_indices = json.loads(monitoring_indices)
monitoring_indices = monitoring_indices['DailyAirQualityIndex']
pp.pprint(monitoring_indices['LocalAuthority'][:1])
print

# print 'MonitoringIndices - Annual'
# monitoring_indices = urllib2.urlopen('http://api.erg.kcl.ac.uk/AirQuality/Annual/MonitoringIndex/GroupName=London/Year=2014/Json').read()
# monitoring_indices = json.loads(monitoring_indices)
# monitoring_indices = monitoring_indices['AnnualAirQualityIndex']
# pp.pprint(monitoring_indices['LocalAuthority'][:1])
# print

# only maps and monitoring objectives available as annual data
