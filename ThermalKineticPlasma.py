from turbopy import Simulation, Module, Diagnostic
import numpy as np

from pathlib import Path
class KineticSpecies:
    def __init__(self,name,charge,mass):
        self.name = name
        self.mass = mass
        self.charge = charge
        self.weights = np.ones(0)
        self.positions = np.zeros(0)
        self.momenta = np.zeros(0)
        self.energies = np.zeros(0)
    
    def __repr__(self):
        return '(' + ', '.join(["Species: " + self.name,
                          "Mass: " + str(self.mass),
                          "Charge: " + str(self.charge)]) + ')'
    
    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False

    def __hash__(self):
        return hash(self.name)

class ThermalKineticPlasma(Module):
    def __init__(self, owner: Simulation, input_data: dict):
        super().__init__(owner, input_data)
        self.particle_pusher = self.owner.find_tool_by_name(input_data["Pusher"]).push
        if input_data["Interpolator"] == '1D':
            self.interpolator = self.owner.find_tool_by_name("Interpolators").interpolate1D
        self.eedf = 0.0
        self.Jp =  self.owner.grid.generate_field(1)
        name = self.input_data['species_name']
        charge = self.input_data['species_charge']
        mass   = self.input_data['species_mass']
#        self.species = {"name":name,"charge":charge,"mass":mass,"weights":np.zeros(0),"position":np.zeros(0),"momentum":np.zeros(0),"energy":np.zeros(0)}
        self.species = KineticSpecies(name,charge,mass)

    def initialize(self):
        self.grid = self.owner.grid.r
        self.dt =  self.owner.clock.dt
        print("dt:",self.dt)
        print(self.grid)

        self.species.weights=np.ones(10)
        self.species.positions=np.zeros((10,3))
        self.species.momenta=np.zeros((10,3))
        self.species.energies=np.zeros(10)
        
    def inspect_resource(self, resource):
        if "FieldModel:E" in resource:
            print("adding E-field resource")
            self.E = resource["FieldModel:E"]
        if "FieldModel:B" in resource:
            print("adding B-field resource")
            self.B = resource["FieldModel:B"]

    def exchange_resources(self):
        """Tell other modules about the electric field, in case the need it"""
        self.publish_resource({"ThermalKineticPlasma:eedf": self.eedf})
        self.publish_resource({"ResponseModel:J": self.Jp})

    def ParticlePusher(self):
        """
        Take a particle list and perform a Lorentz-force update
        """
        x = self.species.positions
        r = x[:,0]
        p = self.species.momenta

        Efld = self.interpolator(self.grid, self.E)
        Ez = Efld(r)
        Evec = np.array([np.zeros_like(Ez),np.zeros_like(Ez),Ez]).T

        Bfld = self.interpolator(self.grid, self.B)
        Bth = Bfld(r)
        Bvec = np.array([np.zeros_like(Bth),Bth,np.zeros_like(Bth)]).T

        self.particle_pusher(x, p, self.species.charge, self.species.mass, Evec, Bvec) 

    def AllocateCurrent(self):
        """
        Take a particle list and allocate current to the grid and update Jp
        """
        print("AllocateCurrent does not do anything yet")

    def EnforceBCs(self):
        """
        Take a list of particles that have crossed a boundary and process them 
        """
        print("EnforceBCs does not do anything yet")
                
    # def AddParticle(self, List):
    #     """
    #     Add particles to the list of active particles
    #     """
    #     for key in List.keys():
    #         self.species[key] = np.append(self.species[key],List[key])
    #     print("species",self.species)

    #   def KillParticle(self):
    #     """
    #     Remove particles from the list of active particles
    #     """
    #     print("this function does not do anything yet")

    # def AdaptiveParticleManagement(self):
    #     """
    #     Resample a particle list so that it has fewer particles but preserves
    #     charge and current density
    #     """
    #     print("AdaptiveParticleManagement does not do anything yet")
        
    def update(self):
        """This function updates all of the pieces that need to be updated for 
        particle list
        """
        self.ParticlePusher()
        # self.AllocateCurrent()
        # self.EnergyDistribution()
        # print("update does not do anything yet")
        # print('')
        
    def EnergyDistribution(self):
        """
        Take particle list and determine the energy distribtition function
        """
        self.eedf = 0.0
        print("EnergyDistribution does not do anything yet")
        
Module.register("ThermalKineticPlasma", ThermalKineticPlasma)        
##        
end_time = 150.E-9
dt = 0.1E-9
number_of_steps = int(end_time/dt)
#number_of_steps = 200
N_grid = 8        
sim_config = {"Modules": [
        {"name": "FieldModel",
             "solver": "PoissonSolver1DRadial",
         },
        {"name": "ThermalKineticPlasma",
        "species_name":"thermal_electrons",
        "species_charge":-1.602E-19,
        "species_mass":9.11E-31,
        "Pusher":"BorisPush",
        "Interpolator":"1D"
         },
        {"name": "RigidBeamCurrentSource",
             "peak_current": 1.0e5,
             "beam_radius": 0.05,
             "rise_time": 30.0e-9,
             "profile": "uniform",
         },
    ],
    "Tools": [
        {"type": "BorisPush"},
        {"type":"PoissonSolver1DRadial"},
        {"type":"Interpolators"},
        ],
    "Grid": {"N":N_grid ,
             "r_min": 0, "r_max": 0.1,
            },
    "Clock": {"start_time": 0,
              "end_time":  end_time, 
              "num_steps": number_of_steps,

              }
    }
    
sim = Simulation(sim_config)
#
sim.run()
            