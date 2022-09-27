from roller import RollerConfig, MultiDrawRollers

configs = [
    RollerConfig(8 * 12.0, 18.0),
    RollerConfig(10 * 12.0, 18.0),
    RollerConfig(12 * 12.0, 18.0),
]

roller = MultiDrawRollers(configs)
roller.draw_image()
