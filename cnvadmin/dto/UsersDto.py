class userFilterDto:
    def __init__(self, emailFilter, deletedFilter):
        self.emailFilter = emailFilter
        self.deletedFilter = deletedFilter        

class userDto:
    def __init__(self, id, email, phone, deleted):
        self.id = id
        self.email = email
        self.phone = phone
        self.deleted = deleted