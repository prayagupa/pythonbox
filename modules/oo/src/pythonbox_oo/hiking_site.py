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


class WalkingSite(HikingSite, object):
    def __init__(self, started_at):
        super(WalkingSite, self).__init__(started_at)


if __name__ == '__main__':
    print("normal OO: ")
    site = HikingSite("2020-12-26")
    print(site.started_at)

    ## inheritence
    print("Walking site: ")
    walking_site = WalkingSite(started_at="2020-12-27")
    print(walking_site.started_at)
