"""
 Title:         The Elastic Visco Plastic Creep Damage Model
 Description:   Predicts primary, secondary, and tertiary creep
 Author:        Janzen Choi

"""

# Libraries
import __model__ as model
from neml import models, elasticity, drivers, surfaces, hardening, visco_flow, general_flow, damage
from neml.nlsolvers import MaximumIterations

# Model Parameters
YOUNGS       = 157000.0
POISSONS     = 0.3
S_RATE       = 1.0e-4
E_RATE       = 1.0e-4
HOLD         = 11500.0 * 3600.0
NUM_STEPS    = 501
MIN_DATA     = 50

# The Elastic Visco Plastic Creep Damage Class
class EVPCD(model.Model):

    # Constructor
    def __init__(self, exp_curves):
        super().__init__(
            name = "evpcd",
            param_info = [
                {"name": "evp_s0",  "min": 0.0e1,   "max": 1.0e2},
                {"name": "evp_R",   "min": 0.0e1,   "max": 1.0e2},
                {"name": "evp_d",   "min": 0.0e1,   "max": 1.0e2},
                {"name": "evp_n",   "min": 2.0e0,   "max": 1.0e1},
                {"name": "evp_eta", "min": 0.0e1,   "max": 1.0e6},
                {"name": "cd_A",    "min": 0.0e1,   "max": 1.0e4},
                {"name": "cd_xi",   "min": 0.0e1,   "max": 1.0e2},
                {"name": "cd_phi",  "min": 0.0e1,   "max": 1.0e2},
            ],
            exp_curves = exp_curves
        )

    # Prepares the model
    def prepare(self, args):
        self.elastic_model      = elasticity.IsotropicLinearElasticModel(YOUNGS, "youngs", POISSONS, "poissons")
        self.yield_surface      = surfaces.IsoJ2()
        self.effective_stress   = damage.VonMisesEffectiveStress()
    
    # Gets the predicted curves
    def get_prd_curves(self, evp_s0, evp_R, evp_d, evp_n, evp_eta, cd_A, cd_xi, cd_phi):

        # Define model

        elastic_model       = elasticity.IsotropicLinearElasticModel(YOUNGS, "youngs", POISSONS, "poissons")
        yield_surface       = surfaces.IsoJ2()
        effective_stress    = damage.VonMisesEffectiveStress()
        iso_hardening       = hardening.VoceIsotropicHardeningRule(evp_s0, evp_R, evp_d)
        g_power             = visco_flow.GPowerLaw(evp_n, evp_eta)
        visco_model         = visco_flow.PerzynaFlowRule(yield_surface, iso_hardening, g_power)
        integrator          = general_flow.TVPFlowRule(elastic_model, visco_model)
        evp_model           = models.GeneralIntegrator(elastic_model, integrator)
        cd_model            = damage.ModularCreepDamage(elastic_model, cd_A, cd_xi, cd_phi, effective_stress)
        evpcd_model         = damage.NEMLScalarDamagedModel_sd(elastic_model, evp_model, cd_model)

        # Iterate through predicted curves
        prd_curves = super().get_prd_curves()
        for i in range(len(prd_curves)):

            # Get stress and temperature
            stress = self.exp_curves[i]["stress"]
            temp = self.exp_curves[i]["temp"] + 273.15 # Kelvin
            type = self.exp_curves[i]["type"]

            # Get predictions
            try:
                if type == "creep":
                    with model.BlockPrint():
                        creep_results = drivers.creep(evpcd_model, stress, S_RATE, HOLD, T=temp, verbose=False, check_dmg=False, dtol=0.95, nsteps_up=150, nsteps=NUM_STEPS, logspace=False)
                    prd_curves[i]["x"] = list(creep_results['rtime'] / 3600)
                    prd_curves[i]["y"] = list(creep_results['rstrain'])
                elif type == "tensile":
                    with model.BlockPrint():
                        tensile_results = drivers.uniaxial_test(evpcd_model, E_RATE, T=temp, emax=0.5, nsteps=NUM_STEPS)
                    prd_curves[i]["x"] = list(tensile_results['strain'])
                    prd_curves[i]["y"] = list(tensile_results['stress'])
            except MaximumIterations:
                return []

            # Make sure predictions contain more than MIN_DATA data points
            if len(prd_curves[i]["x"]) <= MIN_DATA or len(prd_curves[i]["y"]) <= MIN_DATA:
                return []

        # Return predicted curves
        return prd_curves