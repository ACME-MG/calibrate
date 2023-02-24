from modules.api import API
api = API("evpwd", 0)
api.read_files(["inl_1/AirBase_800_80_G25.csv", "inl_1/AirBase_800_70_G44.csv"], ["inl_1/AirBase_800_65_G33.csv", "inl_1/AirBase_800_60_G32.csv"])
api.define_model("evpwd")
# api.define_model("evpwd_s", [41.51219348, 26.94208619, 0.382454248, 2.54294033, 18404.70135])
api.define_errors(["dy_area", "y_area", "x_end", "y_end"])
api.define_constraints(["dec_x_end", "inc_y_end"])
api.define_recorder(10, 10)
api.optimise(10000, 200, 100, 0.65, 0.35)
