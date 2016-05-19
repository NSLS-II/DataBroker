
import logging
import pytest
from io import StringIO

from ophyd import (SimDetector, TIFFPlugin, HDF5Plugin, SingleTrigger)
from ophyd.areadetector.util import stub_templates
from ophyd.device import (Component as Cpt, )

logger = logging.getLogger(__name__)



prefix = 'XF:31IDA-BI{Cam:Tbl}'
ad_path = '/epics/support/areaDetector/1-9-1/ADApp/Db/'


def test_basic():
    class MyDetector(SingleTrigger, SimDetector):
        tiff1 = Cpt(TIFFPlugin, 'TIFF1:')

    det = MyDetector(prefix)
    det.wait_for_connection()
    det.stage()
    det.trigger()
    det.unstage()


def test_stubbing():
    try:
        for line in stub_templates(ad_path):
            logger.debug('Stub line: %s', line)
    except OSError:
        # self.fail('AreaDetector db path needed to run test')
        pass


def test_detector():
    det = SimDetector(prefix)

    det.find_signal('a', f=StringIO())
    det.find_signal('a', use_re=True, f=StringIO())
    det.find_signal('a', case_sensitive=True, f=StringIO())
    det.find_signal('a', use_re=True, case_sensitive=True, f=StringIO())
    det.signal_names
    det.report

    cam = det.cam

    cam.image_mode.put('Single')
    # plugins don't live on detectors now:
    # det.image1.enable.put('Enable')
    cam.array_callbacks.put('Enable')

    det.get()
    st = det.trigger()
    repr(st)
    det.read()

    # values = tuple(det.gain_xy.get())
    cam.gain_xy.put(cam.gain_xy.get(), wait=True)

    # fail when only specifying x
    with pytest.raises(ValueError):
        cam.gain_xy.put((0.0, ), wait=True)

    det.describe()
    det.report


def test_tiff_plugin():
    # det = AreaDetector(prefix)
    class TestDet(SimDetector):
        p = Cpt(TIFFPlugin, 'TIFF1:')

    det = TestDet(prefix)
    plugin = det.p

    plugin.file_template.put('%s%s_%3.3d.tif')

    plugin.array_pixels
    plugin


def test_hdf5_plugin():

    class MyDet(SimDetector):
        p = Cpt(HDF5Plugin, suffix='HDF1:')

    d = MyDet(prefix)
    d.p.file_path.put('/tmp')
    d.p.file_name.put('--')
    d.p.warmup()
    d.stage()


def test_subclass():
    class MyDetector(SimDetector):
        tiff1 = Cpt(TIFFPlugin, 'TIFF1:')

    det = MyDetector(prefix)
    det.wait_for_connection()

    print(det.describe())
    print(det.tiff1.capture.describe())


def test_getattr():
    class MyDetector(SimDetector):
        tiff1 = Cpt(TIFFPlugin, 'TIFF1:')

    det = MyDetector(prefix)
    assert getattr(det, 'tiff1.name') == det.tiff1.name
    assert getattr(det, 'tiff1') is det.tiff1
    # raise
    # TODO subclassing issue


from . import main
is_main = (__name__ == '__main__')
main(is_main)
