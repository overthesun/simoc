import unittest

from simoc_server.tests.test_util import setup_db, clear_db
from simoc_server.agent_model import agent_model_util

class AgentModelUtilTestCase(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        setup_db()

    @classmethod
    def tearDownClass(cls):
        clear_db()

    def testMassToMoles(self):
        # methane molar mass 16.043
        molar_mass = 16.043
        mass_kg = 12.3
        expected = 766.68952191
        moles = agent_model_util.mass_to_moles(mass_kg, molar_mass)
        self.assertAlmostEqual(moles, expected, delta=.001, msg="Incorrect conversion from kg to moles")

    def testO2MassToMoles(self):
        mass_kg = 14.343
        expected = 448.246765423
        moles = agent_model_util.mass_o2_to_moles(mass_kg)
        self.assertAlmostEqual(moles, expected, delta=.001, msg="Incorrect conversion from kg o2 to moles")

    def testCO2MassToMoles(self):
        mass_kg = 23.411
        expected = 531.959371947
        moles = agent_model_util.mass_co2_to_moles(mass_kg)
        self.assertAlmostEqual(moles, expected, delta=.001, msg="Incorrect conversion from kg co2 to moles")

    def testNitrogenMassToMoles(self):
        mass_kg = 1223.344
        expected = 43669.0226315
        moles = agent_model_util.mass_nitrogen_to_moles(mass_kg)
        self.assertAlmostEqual(moles, expected, delta=.001, msg="Incorrect conversion from kg nitrogen to moles")

    def testArgonMassToMoles(self):
        mass_kg = 223.212
        expected = 5587.56383298
        moles = agent_model_util.mass_argon_to_moles(mass_kg)
        self.assertAlmostEqual(moles, expected, delta=.001, msg="Incorrect conversion from kg argon to moles")

    def testWaterMassToMoles(self):
        mass_kg = 61.233
        expected = 3399.00083264
        moles = agent_model_util.mass_water_to_moles(mass_kg)
        self.assertAlmostEqual(moles, expected, delta=.001, msg="Incorrect conversion from kg water to moles")

    def testMassToPressure(self):
        mass_kg = 66.145
        molar_mass = 16.043
        temp_k = 211
        volume_kL = 500
        expected = 14.46678453731
        pressure = agent_model_util.mass_to_pressure(mass_kg, molar_mass, temp_k, volume_kL)
        self.assertAlmostEqual(pressure, expected, delta=.001, msg="Incorrect conversion from mass to moles.")

    def testMolesOfGas(self):
        pressure_kpa = 144.15
        volume_kL = 1200.223
        temp_k = 288.199
        expected = 72201.7933069
        moles = agent_model_util.moles_of_gas(pressure_kpa, volume_kL, temp_k)
        self.assertAlmostEqual(moles, expected, delta=.001, msg="Incorrect mole calculation from temp, volume, pressure.")

    def testMolesToMass(self):
        # methane molar mass 16.043
        molar_mass = 16.043
        moles = 766.68952191
        expected = 12.3
        mass_kg = agent_model_util.moles_to_mass(moles, molar_mass)
        self.assertAlmostEqual(mass_kg, expected, delta=.001, msg="Incorrect conversion from kg to moles")

    def testMolesO2ToMass(self):
        moles = 448.246765423
        expected = 14.343
        mass_kg = agent_model_util.moles_o2_to_mass(moles)
        self.assertAlmostEqual(mass_kg, expected, delta=.001, msg="Incorrect conversion from kg o2 to moles")

    def testMolesCO2ToMass(self):
        moles = 531.959371947
        expected = 23.411
        mass_kg = agent_model_util.moles_co2_to_mass(moles)
        self.assertAlmostEqual(mass_kg, expected, delta=.001, msg="Incorrect conversion from kg co2 to moles")

    def testMolesNitrogenToMass(self):
        moles = 43669.0226315
        expected = 1223.344
        mass_kg = agent_model_util.moles_nitrogen_to_mass(moles)
        self.assertAlmostEqual(mass_kg, expected, delta=.001, msg="Incorrect conversion from kg nitrogen to moles")

    def testMolesArgonToMass(self):
        moles = 5587.56383298
        expected = 223.212
        mass_kg = agent_model_util.moles_argon_to_mass(moles)
        self.assertAlmostEqual(mass_kg, expected, delta=.001, msg="Incorrect conversion from kg argon to moles")

    def testMolesWaterToMass(self):
        moles = 3399.00083264
        expected = 61.233
        mass_kg = agent_model_util.moles_water_to_mass(moles)
        self.assertAlmostEqual(mass_kg, expected, delta=.001, msg="Incorrect conversion from kg water to moles")


if __name__ == "__main__":
    unittest.main()
