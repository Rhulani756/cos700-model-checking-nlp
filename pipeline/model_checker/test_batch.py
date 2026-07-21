from pathlib import Path
from cbmc_runner import CBMCRunner
from esbmc_runner import ESBMCRunner


def run_all_tests():
    # Resolve project root path
    project_root = Path(__file__).resolve().parents[2]
    programs_dir = project_root / "data" / "programs"
    
    cbmc_out_dir = project_root / "data" / "model_checker_outputs" / "cbmc"
    esbmc_out_dir = project_root / "data" / "model_checker_outputs" / "esbmc"

    # Ensure output directories exist
    cbmc_out_dir.mkdir(parents=True, exist_ok=True)
    esbmc_out_dir.mkdir(parents=True, exist_ok=True)
    
    cbmc_runner = CBMCRunner(unwind_limit=5, timeout_seconds=30)
    esbmc_runner = ESBMCRunner(unwind_limit=5, timeout_seconds=30)

    # Find all test files recursively inside data/programs/
    cpp_files = list(programs_dir.rglob("*.cpp"))
    print(f"Found {len(cpp_files)} C++ programs to verify.\n")

    if not cpp_files:
        print("❌ No C++ files found in data/programs/. Please check your directory.")
        return

    for cpp_file in cpp_files:
        print(f"🔄 Verifying: {cpp_file.name}...")
        
        # 1. Run CBMC
        cbmc_output = cbmc_runner.run(cpp_file)
        cbmc_path = cbmc_out_dir / f"{cpp_file.stem}_trace.txt"
        with open(cbmc_path, "w", encoding="utf-8") as f:
            f.write(cbmc_output)

        # 2. Run ESBMC
        esbmc_output = esbmc_runner.run(cpp_file)
        esbmc_path = esbmc_out_dir / f"{cpp_file.stem}_trace.txt"
        with open(esbmc_path, "w", encoding="utf-8") as f:
            f.write(esbmc_output)

        print(f"  ✅ CBMC trace -> {cbmc_path.name}")
        print(f"  ✅ ESBMC trace -> {esbmc_path.name}\n")

    print("🎉 Batch verification complete! All outputs generated.")


if __name__ == "__main__":
    run_all_tests()