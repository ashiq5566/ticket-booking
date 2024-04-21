from bookings.models import Station

def get_station_list(start_station):
    stations = Station.objects.filter(is_deleted=False).order_by('date_added')
    if start_station is not None:
        stations = stations.exclude(slug=start_station)
    stations_list = [station.slug for station in stations]
    
    return stations_list
    
    