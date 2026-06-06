import logging

class Test:
    try: 
        b = 100
        a = 1 / 0
    except Exception as e:
        ## basic error logging
        ## logging.error(e)
        ## logging.critical(e)

        logging.exception(e)
        ## raise Exception("I know Python!", e)

    def __init__(self):
        self.name = "test"

    def doSome(self):
        print("date: " + str(self.b))

t = Test()
t.doSome()
