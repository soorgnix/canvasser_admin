from firebase_admin import firestore

class FireStoreUtils:
    def __init__(self):
        self.db = firestore.client()
    
    def GetLocationDataDict(self):
        locationDocs = self.db.collection('locations').stream()
        locationDataDict = {}

        for locationDoc in locationDocs:
            locationData = locationDoc.to_dict()
            customerCode = locationData.get('customerCode')
            if customerCode is not None:
                if customerCode not in locationDataDict:
                    locationDataDict[customerCode] = []
                    locationDataDict[customerCode].append(locationData)
        return locationDataDict