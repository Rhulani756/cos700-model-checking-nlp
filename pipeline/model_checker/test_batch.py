from pathlib import Path
from cbmc_runner import CBMCRunner
from esbmc_runner import ESBMCRunner


def run_all_tests():
    # Resolve project root path
    project_root = Path(__file__).resolve().parents[2]
    programs_dir = project_root / "data" / "programs"
    
    cbmc_base_dir = project_root / "data" / "model_checker_outputs" / "cbmc"
    esbmc_base_dir = project_root / "data" / "model_checker_outputs" / "esbmc"

    runner_cbmc = CBMCRunner(unwind_limit=15, timeout_seconds=30)
    runner_esbmc = ESBMCRunner(unwind_limit=15, timeout_seconds=30)

    # rglob recursively searches all subdirectories (array_bounds, div_zero, etc.)
    cpp_files = list(programs_dir.rglob("*.cpp"))
    print(f"Found {len(cpp_files)} C++ programs across subfolders to verify.\n")

    if not cpp_files:
        print("❌ No C++ files found in data/programs/. Check directory structure.")
        return

    for cpp_file in cpp_files:
        # Preserve subfolder structure (e.g., 'array_bounds' or 'div_zero')
        relative_folder = cpp_file.relative_to(programs_dir).parent
        
        cbmc_out_dir = cbmc_base_dir / relative_folder
        esbmc_out_dir = esbmc_base_dir / relative_folder
        
        cbmc_out_dir.mkdir(parents=True, exist_ok=True)
        esbmc_out_dir.mkdir(parents=True, exist_ok=True)

        print(f"🔄 Verifying: [{relative_folder}] {cpp_file.name}...")
        
        # 1. Run CBMC
        cbmc_output = runner_cbmc.run(cpp_file)
        cbmc_path = cbmc_out_dir / f"{cpp_file.stem}_trace.txt"
        with open(cbmc_path, "w", encoding="utf-8") as f:
            f.write(cbmc_output)

        # 2. Run ESBMC
        esbmc_output = runner_esbmc.run(cpp_file)
        esbmc_path = esbmc_out_dir / f"{cpp_file.stem}_trace.txt"
        with open(esbmc_path, "w", encoding="utf-8") as f:
            f.write(esbmc_output)

        print(f"  ✅ Saved CBMC  -> {cbmc_path.relative_to(project_root)}")
        print(f"  ✅ Saved ESBMC -> {esbmc_path.relative_to(project_root)}\n")

    print("🎉 Batch verification complete! All subfolder outputs generated.")


if __name__ == "__main__":
    run_all_tests()