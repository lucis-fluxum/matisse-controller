from ctypes import *
from bidict import bidict

from matisse_controller.shamrock_ple.utils import load_lib


# TODO: Note that for some reason the Shamrock will not be found unless SOLIS is installed. Probably a driver issue :(
class Shamrock:
    LIBRARY_NAME = 'ShamrockCIF.dll'
    DEVICE_ID = c_int(0)

    # Below constants are calculated using a pre-calibrated wavelength axis on SOLIS (end - start) / 1024
    GRATINGS_NM_PER_PIXEL = {
        300: 0.116523437,
        1200: 0.0273535156,
        1799: 0.01578125
    }

    # The offset to add, in nanometers, to data in a spectrum taken with a given grating.
    # These tend to change over time, so update accordingly. Offset is abs(pixel shift) * (nm per pixel)
    GRATINGS_OFFSET_NM = {
        300: 1.325,  # -11.4 px, last calibrated Aug 2019
        1200: 0.109,  # -4 px, last calibrated Apr 2015
        1799: 0.470  # -29.8 px, last calibrated Dec 2018
    }

    def __init__(self):
        try:
            self.lib = load_lib(Shamrock.LIBRARY_NAME)
            self.lib.ShamrockInitialize()

            num_devices = c_int()
            self.lib.ShamrockGetNumberDevices(pointer(num_devices))
            assert num_devices.value > 0, 'No spectrometer found.'

            self.gratings = bidict()
            self.setup_grating_info()
        except OSError as err:
            raise RuntimeError('Unable to initialize Andor Shamrock API.') from err

    def __del__(self):
        self.shutdown()

    def setup_grating_info(self):
        """
        Fill out the bidirectional dictionary responsible for holding information about spectrometer gratings.
        """
        number = c_int()
        self.lib.ShamrockGetNumberGratings(Shamrock.DEVICE_ID, pointer(number))
        blaze = create_string_buffer(8)
        for index in range(1, number.value + 1):
            lines, home, offset = c_float(), c_int(), c_int()
            self.lib.ShamrockGetGratingInfo(Shamrock.DEVICE_ID, c_int(index), pointer(lines), blaze, pointer(home),
                                            pointer(offset))
            self.gratings[round(lines.value)] = index

    def get_grating_grooves(self) -> int:
        """
        Returns
        -------
        int
            the number of grooves in the current spectrometer grating
        """
        index = c_int()
        self.lib.ShamrockGetGrating(Shamrock.DEVICE_ID, pointer(index))
        return self.gratings.inverse[index.value]

    def set_grating_grooves(self, num_grooves: int):
        """
        Use the spectrometer grating with the specified number of grooves.

        Parameters
        ----------
        num_grooves
            the desired number of grooves
        """
        if num_grooves != self.get_grating_grooves():
            self.lib.ShamrockSetGrating(Shamrock.DEVICE_ID, c_int(self.gratings[num_grooves]))

    def get_center_wavelength(self) -> float:
        """
        Returns
        -------
        float
            the current center wavelength of the spectrometer
        """
        wavelength = c_float()
        self.lib.ShamrockGetWavelength(Shamrock.DEVICE_ID, pointer(wavelength))
        return wavelength.value

    def set_center_wavelength(self, wavelength: float):
        """
        Set the spectrometer wavelength at the specified value.

        Parameters
        ----------
        wavelength
            the desired center wavelength to set
        """
        if wavelength != self.get_center_wavelength():
            self.lib.ShamrockSetWavelength(Shamrock.DEVICE_ID, c_float(wavelength))

    def shutdown(self):
        """Run Shamrock-related cleanup and shutdown procedures."""
        self.lib.ShamrockClose()
