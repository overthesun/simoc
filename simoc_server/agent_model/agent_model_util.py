from simoc_server.agent_model.global_model_constants import global_model_constants

def mass_to_moles(mass_kg, molar_mass):
    """Convert kilograms to moles

    Parameters
    ----------
    mass_kg : float
        The mass of the substance to convert in *kilograms*
    molar_mass : float
        The molar mass of the substance to convert in *g/mol*

    Returns
    -------
    float
        The number of moles of the mass
    """
    return (mass_kg * 1000.0) / molar_mass

def mass_o2_to_moles(mass_kg):
    """Convert kilograms of oxygen to moles

    Parameters
    ----------
    mass_kg : float
        The mass of oxgen to convert

    Returns
    -------
    float
        The number of moles of oxygen
    """
    return mass_to_moles(mass_kg, global_model_constants["oxygen_molar_mass"])

def mass_co2_to_moles(mass_kg):
    """Convert kilograms of carbon dioxide to moles

    Parameters
    ----------
    mass_kg : float
        The mass of carbon dioxide to convert

    Returns
    -------
    float
        The number of moles of carbon dioxide
    """
    return mass_to_moles(mass_kg, global_model_constants["carbon_dioxide_molar_mass"])

def mass_nitrogen_to_moles(mass_kg):
    """Convert kilograms of nitrogen to moles

    Parameters
    ----------
    mass_kg : float
        The mass of nitrogen to convert

    Returns
    -------
    float
        The number of moles of nitrogen
    """
    return mass_to_moles(mass_kg, global_model_constants["nitrogen_molar_mass"])

def mass_argon_to_moles(mass_kg):
    """Convert kilograms of argon to moles

    Parameters
    ----------
    mass_kg : float
        The mass of argon to convert

    Returns
    -------
    float
        The number of moles of argon
    """
    return mass_to_moles(mass_kg, global_model_constants["argon_molar_mass"])

def mass_water_to_moles(mass_kg):
    """Convert kilograms of water to moles

    Parameters
    ----------
    mass_kg : float
        The mass of water to convert

    Returns
    -------
    float
        The number of moles of water
    """
    return mass_to_moles(mass_kg, global_model_constants["water_molar_mass"])

def mass_o2_to_pressure(mass_kg, temp, volume):
    """Get the pressure of a oxygen from a given mass
    using the ideal gas law

    Parameters
    ----------
    mass_kg : float
        The mass of oxygen convert in kg
    temp : float
        The temperature of the system
    volume : float
        The volume the gas is contained in

    Returns
    -------
    float
        The pressure of the oxygen in kPa

    """
    return mass_to_pressure(mass_kg, global_model_constants["oxygen_molar_mass"], temp, volume)

def mass_co2_to_pressure(mass_kg, temp, volume):
    """Get the pressure of a carbon dioxide from a given mass
    using the ideal gas law

    Parameters
    ----------
    mass_kg : float
        The mass of carbon dioxide convert in kg
    temp : float
        The temperature of the system
    volume : float
        The volume the gas is contained in

    Returns
    -------
    float
        The pressure of the carbon dioxide in kPa

    """
    return mass_to_pressure(mass_kg, global_model_constants["carbon_dioxide_molar_mass"], temp, volume)

def mass_nitrogen_to_pressure(mass_kg, temp, volume):
    """Get the pressure of a nitrogen from a given mass
    using the ideal gas law

    Parameters
    ----------
    mass_kg : float
        The mass of nitrogen convert in kg
    temp : float
        The temperature of the system
    volume : float
        The volume the gas is contained in

    Returns
    -------
    float
        The pressure of the nitrogen in kPa

    """
    return mass_to_pressure(mass_kg, global_model_constants["nitrogen_molar_mass"], temp, volume)

def mass_argon_to_pressure(mass_kg, temp, volume):
    """Get the pressure of a argon from a given mass
    using the ideal gas law

    Parameters
    ----------
    mass_kg : float
        The mass of argon convert in kg
    temp : float
        The temperature of the system
    volume : float
        The volume the gas is contained in

    Returns
    -------
    float
        The pressure of the argon in kPa

    """
    return mass_to_pressure(mass_kg, global_model_constants["argon_molar_mass"], temp, volume)

def mass_to_pressure(mass_kg, molar_mass, temp, volume):
    """Get the pressure of a gas from a given mass
    using the ideal gas law and the molar mass of
    the gas

    Parameters
    ----------
    mass_kg : float
        The mass to convert in kg
    molar_mass : float
        The molar mass of the the gas in g/mol
    temp : float
        The temperature of the system
    volume : float
        The volume the gas is contained in

    Returns
    -------
    float
        The pressure of the gas in kPa

    """

    # PV = nRT
    n = mass_to_moles(mass_kg, molar_mass)

    return (n * global_model_constants["gas_constant"] * temp) / volume

def moles_of_gas(pressure, volume, temp):
    """Get the moles of a gas given the pressure,
    volume and temperature

    Parameters
    ----------
    pressure : float
        Pressure of the gas
    volume : float
        Volume of the gas
    temp : float
        Temperature of the gas

    Returns
    -------
    float
        The number of moles of the gas
    """

    # PV = nRT
    # n = (PV)/(RT)
    return (pressure * volume) / (global_model_constants["gas_constant"] * temp)