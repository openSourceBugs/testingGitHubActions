import math

from page_objects.laser_calc_page import *
from examples.SeleniumBase.examples.boilerplates.base_test_case import BaseTestCase
from decimal import *


class TestLaserCalculator(BaseTestCase):
    """potential bugs with the calculator:
    Tophat and Gaussian radio buttons share the same ID.  this is not valid html
    possible precision/rounding error when all values are 5 (nothing special about the number 5)
    Negative values are allowed via copying and pasting
    https url redirects to a http website.  People might think you're trying to steal their amazon credit card info
    """

    """ TODO use a better arbitrary floating point strategy than Decimal"""
    ENERGY_UNITS = {
        "kJ": Decimal("1000"),
        "J": Decimal("1"),
        "mJ": Decimal(".001"),
        "uJ": Decimal("0.000001"),
        "nJ": Decimal("0.000000001"),
        "pJ": Decimal("0.000000000001"),
    }
    TIME_UNITS = {
        "s": Decimal("1"),
        "ms": Decimal(".001"),
        "us": Decimal("0.000001"),
        "ns": Decimal("0.000000001"),
        "ps": Decimal("0.000000000001"),
        "fs": Decimal("0.000000000000001"),
    }
    POWER_UNITS = {
        "kW": Decimal("1000"),
        "W": Decimal("1"),
        "mW": Decimal(".001"),
        "uW": Decimal("0.000001"),
        "nW": Decimal("0.000000001"),
        "pW": Decimal("0.000000000001"),
    }
    FREQUENCY_UNITS = {
        "MHz": Decimal("1000000"),
        "Hz": Decimal("1"),
        "kHz": Decimal("1000"),
        "Single": Decimal("1"),
    }

    # these are functions that represent the actual calculations performed
    """If I were to test this with access to code, these functions would be tested with unit tests.  The api endpoint which calls this function would also be used in the
    functional end to end test instead of hard coding it here.  This would be a TODO but is not mentioned in requirements"""

    def laser_power_calculation(
        self,
        time,
        time_unit,
        energy=1,
        power=1,
        energy_unit="J",
        power_unit="W",
        freq=1,
        hz="Hz",
    ):
        # forumla for calculating peak power of a laser
        val = (
            energy
            * power
            * self.ENERGY_UNITS[energy_unit]
            * self.POWER_UNITS[power_unit]
        ) / (time * self.TIME_UNITS[time_unit])
        return val / (freq * self.FREQUENCY_UNITS[hz])

    def power_density_calculation(self, power, diameter):
        # formula for calculating peak power density from total power over a given area

        return power / (Decimal(math.pi) * (diameter / 2) ** 2)

    # the actual test
    # The class and the test would be annotated with the suite and other catgories this test would run in but here it's just 1 test. A "TODO"
    def test_calculator(self):
        # user journey test for laser peak power calculator

        # this test data is hardcoded.
        """If further data is required to test (negative numbers, complex numbers etc) a fixture should be added
        this is a TODO testing feature that isn't mentioned in the requirements"""
        diameter = Decimal(1.5)
        max_average_power = Decimal(5)
        repetition_rate = 100
        pulse_width = Decimal(250)
        max_energy = Decimal(
            5
        )  # just in case we need to test max energy instead of average energy

        # the main testing steps
        peak_power = self.laser_power_calculation(
            power=max_average_power,
            power_unit="W",
            time=pulse_width,
            time_unit="ps",
            freq=repetition_rate,
            hz="kHz",
        )
        self.open(
            "https://www.ophiropt.com/laser--measurement/laser-power-energy-meters/services/peak-power-calculator"
        )  #  this is a http url but redirects to https.
        self.click(LaserCalculatorPage.tophat)
        self.click(LaserCalculatorPage.circular)
        self.type(LaserCalculatorPage.diameter_box, str(diameter))
        self.click(LaserCalculatorPage.max_power_avg)
        self.type(LaserCalculatorPage.max_power_avg_box, str(max_average_power))
        self.type(LaserCalculatorPage.repetition_rate_box, str(repetition_rate))
        self.select_option_by_text(LaserCalculatorPage.repetition_rate_dropdown, "kHz")
        self.type(LaserCalculatorPage.pulse_width_box, str(pulse_width))
        self.select_option_by_text(LaserCalculatorPage.pulse_width_dropdown, "ps")
        self.click(LaserCalculatorPage.calculate_button)
        power = self.find_element(LaserCalculatorPage.peak_power_result).get_attribute(
            "value"
        )
        self.assertEqual("{:.2f}".format(peak_power), str(power))
        power_density = self.power_density_calculation(peak_power, diameter / 10)
        density = self.find_element(
            LaserCalculatorPage.peak_power_density_result
        ).get_attribute("value")
        self.assertEqual(
            "{:.2f}".format(power_density), str(density)
        )  # forumla is result *pi * (diameter/2) for density
        self.click(LaserCalculatorPage.gaussian)
        self.assert_element_not_visible(LaserCalculatorPage.circular)
        self.assert_element_not_visible(LaserCalculatorPage.rectangular)
        self.click(LaserCalculatorPage.calculate_button)
        density = self.find_element(
            LaserCalculatorPage.peak_power_density_result
        ).get_attribute("value")
        self.assertEqual("{:.2f}".format(peak_power), str(power))
        self.assertEqual(
            "{:.2f}".format(
                2 * power_density
            ),  # TODO this 2 factor for Gaussian should probably be somewhere else
            density,
        )
