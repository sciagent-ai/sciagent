"""Simple S4 + FastAPI test"""
from fastapi import FastAPI
import S4

app = FastAPI()

# Test S4 on startup
print("Testing S4...")
S = S4.New(Lattice=500, NumBasis=11)
S.AddMaterial('Air', 1.0)
S.AddMaterial('Si', 15.0)
S.AddLayer('Inc', 0, 'Air')
S.AddLayer('Grating', 200, 'Air')
S.SetRegionRectangle('Grating', 'Si', (0, 0), 0, (125, 0.5))
S.AddLayer('Sub', 0, 'Si')
S.SetExcitationPlanewave(IncidenceAngles=(45, 0), sAmplitude=1, pAmplitude=0)
S.SetFrequency(1.0 / 633)
fwd, back = S.GetPowerFlux('Inc')
print(f"S4 works! Reflection: {abs(back):.4f}")

@app.get("/")
def root():
    return {"s4": "available", "test": "passed"}

@app.get("/simulate")
def simulate():
    S = S4.New(Lattice=500, NumBasis=11)
    S.AddMaterial('Air', 1.0)
    S.AddMaterial('Si', 15.0)
    S.AddLayer('Inc', 0, 'Air')
    S.AddLayer('Grating', 200, 'Air')
    S.SetRegionRectangle('Grating', 'Si', (0, 0), 0, (125, 0.5))
    S.AddLayer('Sub', 0, 'Si')
    S.SetExcitationPlanewave(IncidenceAngles=(45, 0), sAmplitude=1, pAmplitude=0)
    S.SetFrequency(1.0 / 633)
    fwd, back = S.GetPowerFlux('Inc')
    return {"reflection": abs(back), "transmission": abs(fwd)}
