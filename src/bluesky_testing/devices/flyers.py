import logging
import threading 
import time

from collections import deque

import ophyd

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


class BaseFlyer(ophyd.Device):
    """
    Base flyer template
    """

    def __init__(self, *args, **kwargs):
        super().__init__('', parent=None, **kwargs)
        self.complete_status = None
        self.kickoff_status = None
        self.t0 = 0

    def _fly(self):
        """
        flyer activity goes here

        It's OK to use blocking calls here
        since this is called in a separate thread
        from the Bluesky RunEngine.
        """
        logger.info("flyer activity()")
        if self.complete_status is None:
            logger.info("leaving activity() - not complete")
            return

        # TODO: do the activity here

        # once started, we notify by updating the status object
        self.kickoff_status.set_finished()

        # TODO: wait for completion

        # after the wait, we declare victory
        self.complete_status.set_finished()
        logger.info("activity() complete. status = " + str(self.complete_status))

    def kickoff(self):
        """
        Start this flyer
        """
        logger.info("kickoff()")
        self.kickoff_status = ophyd.DeviceStatus(self)
        self.complete_status = ophyd.DeviceStatus(self)
        self.t0 = time.time()

        thread = threading.Thread(target=self._fly, daemon=True)
        thread.start()

        return self.kickoff_status
    
    def complete(self):
        """
        Wait for flying to complete
        """
        logger.info("complete()")
        if self.complete_status is None:
            raise RuntimeError("No collection in progress")

        return self.complete_status
    
    def collect(self):
        """
        Retrieve the data
        """
        logger.info("collect()")
        self.complete_status = None
        yield {'data':{}, 'timestamps':{}, 'time':time.time()}

    def describe_collect(self):
        """
        Describe details for ``collect()`` method
        """
        logger.info("describe_collect()")
        return {self.name: {}}


class Flyer1(BaseFlyer):
    """
    Flyer example
    """

    def __init__(self, steps=1, *args, **kwargs):
        super().__init__('', **kwargs)
        self.t0 = 0
        self._steps = steps
        self._data = deque()

    
    def _fly(self):
        """
        flyer activity goes here

        It's OK to use blocking calls here
        since this is called in a separate thread
        from the Bluesky RunEngine.
        """
        logger.info("flyer activity()")
        if self.complete_status is None:
            logger.info("leaving activity() - not complete")
            return

        # TODO: do the activity here
        logger.info("writing data... ")
        for step in range(self._steps):
            t = time.time()
            x = t - self.t0
            d = dict(
                time=t,
                data=dict(x=x),
                timestamps=dict(x=t)
            )
            self._data.append(d)
            time.sleep(.5)
        logger.info("done")

        # once started, we notify by updating the status object
        self.kickoff_status.set_finished()

        # TODO: wait for completion

        # after the wait, we declare victory
        # self.complete_status.set_finished()
        # logger.info("_fly() complete. status = " + str(self.complete_status))

    def kickoff(self):
        """
        Start this flyer
        """
        logger.info("kickoff()")
        self.kickoff_status = ophyd.DeviceStatus(self)
        self.complete_status = ophyd.DeviceStatus(self)
        self.t0 = time.time()
        self._data = deque()

        def flyer_worker():
            self._fly()
            self.complete_status.set_finished()
            logger.info("_fly() complete. status = " + str(self.complete_status))

        thread = threading.Thread(target=flyer_worker, daemon=True)
        thread.start()

        return self.kickoff_status

    def collect(self):
        """
        Retrieve/collect the data
        """
        logger.info("collect()")
        self.complete_status = None

        yield from self._data

    def describe_collect(self):
        """
        Describe details for `collect()` method
        """
        logger.info("describe_collect()")
        d = dict(
            source = "elapsed time, s",
            dtype = "number",
            shape = (1,)
        )
        return {
            self.name: {
                "x": d
            }
        }