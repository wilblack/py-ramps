from roller import RollerConfig, Roller

config = RollerConfig(12 * 12.0, 18.0)

roller = Roller(config)
roller.draw_image()
