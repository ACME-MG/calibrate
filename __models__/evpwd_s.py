"""
 Title:         The Elastic Visco Plastic Work Damage Model (Separated)
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

# The Elastic Visco Plastic Work Damage (Separated) Class
class EVPWD_S(model.Model):

    # Constructor
    def __init__(self, exp_curves):
        super().__init__(
            name = "evpwd_s",
            param_info = [
                {"name": "wd_wc",   "min": 0.0e1,   "max": 1.0e2},
                {"name": "wd_n",    "min": 0.0e1,   "max": 1.0e2},
            ],
            exp_curves = exp_curves
        )

    # Prepares the model
    def prepare(self, args):
        self.elastic_model = elasticity.IsotropicLinearElasticModel(YOUNGS, "youngs", POISSONS, "poissons")
        self.yield_surface = surfaces.IsoJ2()
        self.evp_s0 = 0.671972514
        self.evp_R = 25.74997349
        self.evp_d = 43.16881374
        self.evp_n = 4.487884698
        self.evp_eta = 1669.850786

    # Gets the predicted curves
    def get_prd_curves(self, wd_wc, wd_n):

        # Define model
        iso_hardening   = hardening.VoceIsotropicHardeningRule(self.evp_s0, self.evp_R, self.evp_d)
        g_power         = visco_flow.GPowerLaw(self.evp_n, self.evp_eta)
        visco_model     = visco_flow.PerzynaFlowRule(self.yield_surface, iso_hardening, g_power)
        integrator      = general_flow.TVPFlowRule(self.elastic_model, visco_model)
        evp_model       = models.GeneralIntegrator(self.elastic_model, integrator, verbose=False)
        wd_model        = damage.WorkDamage(self.elastic_model, wd_wc, wd_n)
        evpwd_model     = damage.NEMLScalarDamagedModel_sd(self.elastic_model, evp_model, wd_model, verbose=False)

        # Iterate through predicted curves
        prd_curves = super().get_prd_curves()
        for i in range(len(prd_curves)):

            # Get stress and temperature
            stress = self.exp_curves[i]["stress"]
            temp = self.exp_curves[i]["temp"]
            type = self.exp_curves[i]["type"]

            # Get predictions
            try:
                if type == "creep":
                    with model.BlockPrint():
                        creep_results = drivers.creep(evpwd_model, stress, S_RATE, HOLD, T=temp, verbose=False, check_dmg=False, dtol=0.95, nsteps_up=150, nsteps=NUM_STEPS, logspace=False)
                    prd_curves[i]["x"] = list(creep_results['rtime'] / 3600)
                    prd_curves[i]["y"] = list(creep_results['rstrain'])
                elif type == "tensile":
                    with model.BlockPrint():
                        tensile_results = drivers.uniaxial_test(evpwd_model, E_RATE, T=temp, emax=0.5, nsteps=NUM_STEPS)
                    prd_curves[i]["x"] = list(tensile_results['strain'])
                    prd_curves[i]["y"] = list(tensile_results['stress'])
            except MaximumIterations:
                return []

            # Make sure predictions contain more than MIN_DATA data points
            if len(prd_curves[i]["x"]) <= MIN_DATA or len(prd_curves[i]["y"]) <= MIN_DATA:
                return []

        # Return predicted curves
        return prd_curves