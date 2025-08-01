import os

dir_parent = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dir_cascade = os.path.join(dir_parent, "external", "cascade")

import numpy as np
from typing import Tuple
from cascade2p import cascade
from cascade2p.utils_discrete_spikes import infer_discrete_spikes

# run Cascade model and predict spike_prob and spikes
def runCascade(
    traces: np.ndarray,
    model_name: str,
) -> Tuple[np.ndarray, np.ndarray]:
    model_folder=f"{dir_cascade}/Pretrained_models"
    # download model if not exists
    cascade.download_model(
        model_name=model_name,
        model_folder=model_folder,
        verbose=1
    )
    spike_prob = cascade.predict(
        model_name=model_name, 
        traces=traces, 
        model_folder=model_folder,
    )
    # infer discrete spikes from spike_prob
    discrete_approximation, spike_time_estimates = infer_discrete_spikes(
        spike_prob, 
        model_name, 
        model_folder
    )
    # convert spike_prob to 0/1 spikes array
    spike_events = np.zeros_like(spike_prob, dtype=int)
    for i, spike_time in enumerate(spike_time_estimates):
        spike_events[i][spike_time] = 1
    return spike_prob, spike_events