class Shipping(object):
    def run(self):
        print "Shipping package !!!"

    def ship_all(self):
        for number in range(1,10): 
	    print "shipping package " + str(number)

if __name__ == '__main__':
    Shipping().ship_all()
