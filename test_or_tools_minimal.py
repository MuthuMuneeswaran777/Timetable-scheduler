from ortools.sat.python import cp_model

def test_minimal_or_tools():
    print("🧪 Testing minimal OR-Tools functionality")

    # Create a simple model
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()

    # Simple variables
    x = model.NewBoolVar('x')
    y = model.NewBoolVar('y')

    # Simple constraint
    model.Add(x + y >= 1)

    # Simple objective
    model.Maximize(x + y)

    # Solve
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print("✅ OR-Tools working correctly")
        print(f"x = {solver.Value(x)}, y = {solver.Value(y)}")
        print(f"Objective = {solver.ObjectiveValue()}")
    else:
        print("❌ OR-Tools not working")

if __name__ == "__main__":
    test_minimal_or_tools()
