# Stateful.
# state of the battery.
# v_battery - Live battery voltage.
# v_max - Maximum voltage that the battery can handle without degrading lifespan.
# c_max - Maximum current that the battery can handle without degrading lifespan.
# v_const - Constant charging voltage after initial charging reaches v_max.
# RETURN an appropriate charging current for the current state.






# Stateless
# v_battery - Live battery voltage.
# v_max - Maximum voltage that the battery can handle without degrading its lifespan.
# v_thresh - Threshold voltage where charging is slowed down.
# c_max - Maximum current that the battery can handle without degrading its lifespan.
# c_low - Starting current of the slower charging phase where v_max is reached.
# RETURN an appropriate charging current for the current state.
def charging_manager(v_battery, v_max, v_threshold, c_max):
    return