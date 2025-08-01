import argparse

def main(path_dff0, model_name='Global_EXC_30Hz_smoothing25ms'):
    import os
    import sys
    import numpy as np
    # Set up paths
    dir_parent = os.path.dirname(os.path.abspath("__file__"))
    os.chdir(dir_parent)
    sys.path.append(dir_parent)
    sys.path.append(f"{dir_parent}\\cascade2p")

    from cascade2p import cascade
    from cascade2p.utils import plot_dFF_traces, plot_noise_level_distribution, plot_noise_matched_ground_truth
    from cascade2p import checks
    import ruamel.yaml as yaml
    
    # Check required packages
    checks.check_packages()
    
    # Configure yaml
    yaml = yaml.YAML(typ='rt')
    
    # Load and process data
    dff0 = np.load(path_dff0)
    spike_prob = cascade.predict(model_name, dff0)
    path_cascade = path_dff0.replace(".npy", "_cascade.npy")
    np.save(path_cascade, spike_prob)
    print(f"Cascade result saved to {path_cascade}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Cascade2p prediction')
    parser.add_argument('path_dff0', type=str, help='Path to dF/F0 numpy file')
    parser.add_argument('--model_name', type=str, default='Global_EXC_30Hz_smoothing25ms',
                      help='Model name for prediction (default: Global_EXC_30Hz_smoothing25ms)')
    
    args = parser.parse_args()
    main(args.path_dff0, args.model_name)
