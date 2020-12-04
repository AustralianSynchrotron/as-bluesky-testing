import bluesky, databroker

from bluesky.plans import fly, count
from bluesky.preprocessors import fly_during_wrapper

from ophyd.sim import det, flyer1, flyer2

from bluesky_testing.devices.flyers import BaseFlyer, Flyer1

# set up loggers, bluesky and databroker
# logger = logging.getLogger()
RE = bluesky.RunEngine({})
db = databroker.temp()
RE.subscribe(db.insert)


# create instance of the flyer
flyer0 = Flyer1(name='flyer0', steps=3)
flyer1 = Flyer1(name='flyer1', steps=5)

# inspect some parts of the flyer
# print(ifly.describe_collect())
# print(list(ifly.collect()))

# run the fly plan
RE(bluesky.plans.fly([flyer0, flyer1]))


# inspect the data
h = db[-1]

for n in h.stream_names:
    print("=================")
    print(f"data for {n}")
    print(h.table(n))


print("========= Fly Asynchronously =============")
    

from bluesky.preprocessors import fly_during_wrapper

RE(fly_during_wrapper(count([det], num=5), [flyer0, flyer1]))

h = db[-1]

for n in h.stream_names:
    print("=================")
    print(f"data for {n}")
    print(h.table(n))

# print(list(db[-1].documents()))





