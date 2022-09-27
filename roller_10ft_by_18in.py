from roller import RollerConfig, Roller

config = RollerConfig(10 * 12.0, 18.0)

roller = Roller(config)
roller.draw_image()
