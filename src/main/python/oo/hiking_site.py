class HikingSite:
    ## class variable
    hiking_sites = [
        "walking",
        "hiking"
    ]

    def __init__(self):
        ## instance variable
        self.started_at = "2020-12-26"
        self.ended_at = "2020-12-26"

    def __init__(self, started):
        self.started_at = started

    def end_visit(self, ended):
        self.ended_at = ended
        return self

if __name__ == '__main__':
    site = HikingSite("2020-12-26")
    print site.started_at
